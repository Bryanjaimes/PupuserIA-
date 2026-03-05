#!/usr/bin/env python3
"""
Image Download + WebP Pipeline
Downloads listing images, converts to WebP, and prepares for Supabase Storage upload.

Usage:
    python download_images.py [--limit 100] [--workers 8] [--quality 80]
    python download_images.py --upload-supabase  # (after configuring .env)

Reads:  data/scraper_output/all_listings_scored.json
Writes: data/images/<listing_id>/<index>.webp
Output: data/scraper_output/all_listings_with_local_images.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

# ── Constants ────────────────────────────────────────

INPUT = Path("data/scraper_output/all_listings_scored.json")
OUTPUT = Path("data/scraper_output/all_listings_with_local_images.json")
IMAGE_DIR = Path("data/images")
MAX_IMAGES_PER_LISTING = 5
DEFAULT_WORKERS = 6
DEFAULT_QUALITY = 80
TIMEOUT = 15  # seconds per image

# ── Optional deps (graceful fallback) ────────────────

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠  Pillow not installed — images will be saved as-is (no WebP conversion)")
    print("   Install: pip install Pillow")

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    import urllib.request


# ── Download helpers ─────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Referer": "https://www.encuentra24.com/",
}


def download_image(url: str, dest: Path, quality: int = 80) -> tuple[bool, str]:
    """Download a single image and optionally convert to WebP. Returns (success, message)."""
    try:
        if dest.exists():
            return True, "cached"

        dest.parent.mkdir(parents=True, exist_ok=True)

        # Download raw bytes
        if HAS_HTTPX:
            with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
                resp = client.get(url, headers=HEADERS)
                resp.raise_for_status()
                raw_bytes = resp.content
        else:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw_bytes = resp.read()

        if len(raw_bytes) < 1000:
            return False, "too small (likely error page)"

        # Convert to WebP if Pillow available
        if HAS_PIL:
            from io import BytesIO
            img = Image.open(BytesIO(raw_bytes))
            img = img.convert("RGB")

            # Resize if massive (save bandwidth)
            max_dim = 1200
            if max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            webp_path = dest.with_suffix(".webp")
            img.save(webp_path, "WEBP", quality=quality, method=4)
            return True, f"webp {webp_path.stat().st_size // 1024}KB"
        else:
            # Save raw
            ext = Path(urlparse(url).path).suffix or ".jpg"
            raw_path = dest.with_suffix(ext)
            raw_path.write_bytes(raw_bytes)
            return True, f"raw {raw_path.stat().st_size // 1024}KB"

    except Exception as e:
        return False, str(e)[:80]


def process_listing(
    listing: dict, image_dir: Path, max_images: int, quality: int
) -> dict:
    """Download images for a single listing. Returns updated listing."""
    listing_id = listing.get("id", "unknown")
    images = (listing.get("images") or [])[:max_images]
    local_images = []
    local_thumbs = []

    for idx, url in enumerate(images):
        # Use hash of URL for filename to ensure uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        dest = image_dir / listing_id / f"{idx}_{url_hash}"
        success, msg = download_image(url, dest, quality)
        if success:
            # Find the actual saved file (might be .webp or original ext)
            webp = dest.with_suffix(".webp")
            if webp.exists():
                local_images.append(str(webp))
            else:
                # Find any file with this stem
                for f in dest.parent.glob(f"{dest.stem}.*"):
                    local_images.append(str(f))
                    break

    listing = listing.copy()
    listing["images_original"] = listing.get("images", [])
    listing["images_local"] = local_images

    # For Supabase: paths will be like /storage/v1/object/public/property-images/<id>/0.webp
    listing["images_storage"] = [
        f"property-images/{listing_id}/{Path(p).name}" for p in local_images
    ]
    return listing


# ── Supabase upload (optional) ───────────────────────

def upload_to_supabase(listings: list[dict]) -> None:
    """Upload local images to Supabase Storage bucket."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    bucket = os.environ.get("SUPABASE_BUCKET", "property-images")

    if not supabase_url or not supabase_key:
        print("❌ Set SUPABASE_URL and SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)

    try:
        from supabase import create_client
    except ImportError:
        print("❌ pip install supabase")
        sys.exit(1)

    client = create_client(supabase_url, supabase_key)
    storage = client.storage.from_(bucket)

    uploaded = 0
    for listing in listings:
        for local_path, storage_path in zip(
            listing.get("images_local", []),
            listing.get("images_storage", []),
        ):
            path_obj = Path(local_path)
            if not path_obj.exists():
                continue
            try:
                with open(path_obj, "rb") as f:
                    storage.upload(
                        storage_path.replace(f"{bucket}/", ""),
                        f,
                        {"content-type": "image/webp"},
                    )
                uploaded += 1
            except Exception as e:
                if "Duplicate" in str(e):
                    uploaded += 1  # already there
                else:
                    print(f"  ⚠ Upload failed {storage_path}: {e}")

    print(f"✅ Uploaded {uploaded} images to Supabase Storage bucket '{bucket}'")


# ── Main ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Download listing images → WebP")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of listings (0=all)")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Parallel download workers")
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY, help="WebP quality (1-100)")
    parser.add_argument("--upload-supabase", action="store_true", help="Upload to Supabase Storage")
    parser.add_argument("--input", type=str, default=str(INPUT), help="Input JSON file")
    parser.add_argument("--output", type=str, default=str(OUTPUT), help="Output JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    print(f"📷 PupuserIA Image Pipeline")
    print(f"   Input:   {input_path}")
    print(f"   Output:  {output_path}")
    print(f"   Images:  {IMAGE_DIR}")
    print(f"   Workers: {args.workers}")
    print(f"   Quality: {args.quality}")
    print(f"   Max per listing: {MAX_IMAGES_PER_LISTING}")
    print(f"   PIL/WebP: {'✅' if HAS_PIL else '❌'}")
    print()

    # Load listings
    with open(input_path, "r", encoding="utf-8") as f:
        listings = json.load(f)
    if args.limit:
        listings = listings[:args.limit]
    print(f"  Loaded {len(listings)} listings")

    total_images = sum(min(len(r.get("images") or []), MAX_IMAGES_PER_LISTING) for r in listings)
    print(f"  {total_images} images to download (max {MAX_IMAGES_PER_LISTING}/listing)")
    print()

    # Download with thread pool
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    updated = []
    success_count = 0
    fail_count = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_listing, listing, IMAGE_DIR, MAX_IMAGES_PER_LISTING, args.quality
            ): i
            for i, listing in enumerate(listings)
        }

        for i, future in enumerate(as_completed(futures)):
            listing = future.result()
            updated.append(listing)
            n_local = len(listing.get("images_local", []))
            n_orig = min(len(listing.get("images_original", [])), MAX_IMAGES_PER_LISTING)
            success_count += n_local
            fail_count += (n_orig - n_local)

            if (i + 1) % 100 == 0:
                elapsed = time.time() - start
                rate = success_count / elapsed if elapsed > 0 else 0
                print(f"  [{i+1}/{len(listings)}] {success_count} ok, {fail_count} failed ({rate:.0f} img/s)")

    elapsed = time.time() - start
    print(f"\n✅ Done in {elapsed:.1f}s")
    print(f"   Downloaded: {success_count}")
    print(f"   Failed:     {fail_count}")

    # Sort by original order (futures may complete out of order)
    updated.sort(key=lambda r: r.get("id", ""))

    # Save updated JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print(f"   Output: {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # Optional Supabase upload
    if args.upload_supabase:
        upload_to_supabase(updated)


if __name__ == "__main__":
    main()
