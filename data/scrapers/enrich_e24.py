#!/usr/bin/env python3
"""
Encuentra24 Detail Enrichment
==============================
Reads existing JSONL from the AJAX scraper and enriches each record
by fetching the individual detail page to extract:

  - Full description (from JSON-LD Product.description)
  - Full image gallery (all unique photos at highest resolution)
  - Features table (beds, baths, area confirmation)
  - Seller info (from JSON-LD)
  - Address details (from JSON-LD PostalAddress)

Data NOT available on E24 detail pages (confirmed via probe):
  - GPS coordinates (no lat/lng anywhere in page)
  - Listing date (not in HTML or JSON-LD)
  - Lot size (only construction m² shown)

Rate limiting: 0.5 req/sec with jitter, respectful of robots.txt.
Saves progress every 50 records so it can resume if interrupted.

Usage:
    python enrich_e24.py
    python enrich_e24.py --input data/scraper_output/encuentra24_ajax_all_20260218_205135.jsonl
    python enrich_e24.py --resume  # Continue from last checkpoint
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── Config ──

DEFAULT_INPUT = "data/scraper_output/encuentra24_ajax_all_20260218_205135.jsonl"
OUTPUT_DIR = Path("data/scraper_output")
CHECKPOINT_FILE = OUTPUT_DIR / "_enrich_checkpoint.json"
PROGRESS_EVERY = 50  # Save progress every N records

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Delay between requests: 1.5-3.0 seconds (respectful)
MIN_DELAY = 1.5
MAX_DELAY = 3.0


def extract_json_ld(html: str) -> dict:
    """Extract the JSON-LD Product object from the page."""
    for m in re.finditer(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    ):
        try:
            d = json.loads(m.group(1))
            if d.get("@type") == "Product":
                return d
        except (json.JSONDecodeError, ValueError):
            continue
    return {}


def extract_description(product_ld: dict, html: str) -> str:
    """Extract description from JSON-LD or fallback to HTML parsing."""
    # Primary: JSON-LD
    desc = product_ld.get("description", "")
    if desc and len(desc.strip()) > 10:
        return desc.strip()

    # Fallback: HTML patterns
    for pat in [
        r'class="[^"]*d3-ad-view__description[^"]*"[^>]*>(.*?)</div>',
        r'class="[^"]*ad-body[^"]*"[^>]*>(.*?)</div>',
        r'class="[^"]*description[^"]*"[^>]*>(.*?)</div>',
        r'itemprop="description"[^>]*>(.*?)</(?:div|span|p)',
    ]:
        m = re.search(pat, html, re.S | re.I)
        if m:
            text = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
            text = re.sub(r"\s+", " ", text)
            if len(text) > 10:
                return text[:3000]

    return ""


def extract_all_images(html: str, ad_id: str) -> list[str]:
    """
    Extract all unique high-res images from the detail page.
    
    Strategy:
    1. Find all unique image hashes for this ad ID
    2. Construct the largest variant URL (t_or_fh_l) for each
    """
    # Find all image hashes for this listing
    # Pattern: /ADID_HASH where HASH is 6 hex chars
    hashes = set()
    for m in re.finditer(rf"/{ad_id}_([a-f0-9]{{4,8}})", html):
        hashes.add(m.group(1))

    if not hashes:
        # Fallback: grab any photos.encuentra24.com URL
        imgs = []
        for m in re.finditer(
            r"(https://photos\.encuentra24\.com/[^\"'\\]+)", html
        ):
            url = m.group(1)
            if "cnseal" not in url and "badge" not in url and "user_photo" not in url:
                if url not in imgs:
                    imgs.append(url)
        return imgs[:20]

    # Reconstruct the path from ad_id: 31801322 → 31/80/13/22
    digits = ad_id.zfill(8)
    path_parts = f"{digits[0:2]}/{digits[2:4]}/{digits[4:6]}/{digits[6:8]}"

    best_imgs = []
    for h in sorted(hashes):
        url = (
            f"https://photos.encuentra24.com/t_or_fh_l/f_auto/v1/sv/"
            f"{path_parts}/{ad_id}_{h}"
        )
        best_imgs.append(url)

    return best_imgs[:20]


def extract_features_from_html(html: str) -> dict:
    """Extract beds, baths, area from the features/attributes section."""
    result = {}
    features_text = []

    # Look for feature items
    for m in re.finditer(
        r'class="[^"]*(?:feature|attribute|spec|property-attr|detail-item)[^"]*"[^>]*>(.*?)</(?:li|div|tr|dd)',
        html,
        re.S | re.I,
    ):
        text = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
        text = re.sub(r"\s+", " ", text)
        if 3 < len(text) < 200:
            features_text.append(text)

            # Parse specific values
            lower = text.lower()
            if "bedroom" in lower or "habitacion" in lower or "dormitorio" in lower:
                nums = re.findall(r"\d+", text)
                if nums:
                    result["bedrooms"] = int(nums[0])
            elif "bathroom" in lower or "baño" in lower:
                nums = re.findall(r"[\d.]+", text)
                if nums:
                    result["bathrooms"] = float(nums[0])
            # Check lot/terreno BEFORE general m² to avoid misclassifying
            elif "terreno" in lower or "lot size" in lower or "lote" in lower:
                nums = re.findall(r"[\d,.]+", text)
                if nums:
                    val = float(nums[0].replace(",", ""))
                    if val > 0:
                        result["lot_size_m2"] = val
            elif "m\u00b2" in text or "m2" in lower or "construccion" in lower:
                nums = re.findall(r"[\d,.]+", text)
                if nums:
                    val = float(nums[0].replace(",", ""))
                    if val > 0:
                        result["area_m2"] = val
            elif "parking" in lower or "estacionamiento" in lower or "garage" in lower:
                nums = re.findall(r"\d+", text)
                if nums:
                    result["parking"] = int(nums[0])

    result["features_detail"] = features_text
    return result


def extract_seller(product_ld: dict) -> str:
    """Extract seller name from JSON-LD."""
    offers = product_ld.get("offers", {})
    seller = offers.get("seller", {})
    name = seller.get("name", "").strip()
    return name if name and name.lower() != "owner" else ""


def extract_address_detail(product_ld: dict) -> dict:
    """Extract structured address from JSON-LD."""
    offers = product_ld.get("offers", {})
    place = offers.get("availableAtOrFrom", {})
    addr = place.get("address", {})
    return {
        "street": addr.get("streetAddress", ""),
        "locality": addr.get("addressLocality", ""),
        "postal_code": addr.get("postalCode", ""),
    }


def get_ad_id_from_url(url: str) -> str:
    """Extract numeric ad ID from E24 URL."""
    m = re.search(r"/(\d{6,10})$", url.rstrip("/"))
    return m.group(1) if m else ""


async def enrich_one(
    client: httpx.AsyncClient, record: dict, idx: int, total: int
) -> dict:
    """Fetch detail page and enrich a single record."""
    url = record.get("source_url", "")
    ad_id = get_ad_id_from_url(url)

    if not url or not ad_id:
        logger.warning(f"  [{idx}/{total}] No URL/ID, skipping")
        return record

    # Random delay
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    await asyncio.sleep(delay)

    try:
        resp = await client.get(
            url,
            headers={
                **HEADERS,
                "Referer": "https://www.encuentra24.com/el-salvador-en/real-estate-for-sale",
            },
            follow_redirects=True,
        )

        if resp.status_code == 403 or resp.status_code == 429:
            logger.warning(
                f"  [{idx}/{total}] Rate limited ({resp.status_code}), "
                f"backing off 30s"
            )
            await asyncio.sleep(30)
            return record

        if resp.status_code != 200:
            logger.warning(
                f"  [{idx}/{total}] HTTP {resp.status_code} for {ad_id}"
            )
            return record

        html = resp.text
        if len(html) < 1000:
            logger.warning(f"  [{idx}/{total}] Tiny response for {ad_id}")
            return record

        # ── Extract JSON-LD ──
        product_ld = extract_json_ld(html)
        logger.debug(f"    JSON-LD keys: {list(product_ld.keys()) if product_ld else 'EMPTY'}")

        # ── Description ──
        desc = extract_description(product_ld, html)
        logger.debug(f"    description len={len(desc)}")
        if desc:
            record["description_es"] = desc
            # Also set description (will be translated by AI later)
            if not record.get("description"):
                record["description"] = desc

        # ── Full image gallery ──
        images = extract_all_images(html, ad_id)
        if images and len(images) > len(record.get("images", [])):
            record["images"] = images

        # ── Features from detail page ──
        feat = extract_features_from_html(html)
        if feat.get("bedrooms") and not record.get("bedrooms"):
            record["bedrooms"] = feat["bedrooms"]
        if feat.get("bathrooms") and not record.get("bathrooms"):
            record["bathrooms"] = feat["bathrooms"]
        if feat.get("area_m2") and not record.get("area_m2"):
            record["area_m2"] = feat["area_m2"]
        if feat.get("lot_size_m2"):
            record["lot_size_m2"] = feat["lot_size_m2"]
        if feat.get("parking"):
            record["parking"] = feat["parking"]
        # Replace features with detail-page features (more detailed)
        if feat.get("features_detail"):
            record["features"] = feat["features_detail"]

        # ── Seller ──
        seller = extract_seller(product_ld)
        if seller:
            record["seller"] = seller

        # ── Address detail ──
        addr = extract_address_detail(product_ld)
        if addr.get("street") and not record.get("address"):
            record["address"] = addr["street"]
        if addr.get("locality"):
            record["address_locality"] = addr["locality"]

        # Mark as enriched
        record["enriched_at"] = datetime.now(timezone.utc).isoformat()

        img_count = len(record.get("images", []))
        desc_len = len(record.get("description_es", ""))
        logger.info(
            f"  [{idx}/{total}] {ad_id} — "
            f"desc={desc_len}ch imgs={img_count} "
            f"beds={record.get('bedrooms')} baths={record.get('bathrooms')}"
        )

    except httpx.RequestError as e:
        logger.warning(f"  [{idx}/{total}] Request error: {e}")
    except Exception as e:
        logger.error(f"  [{idx}/{total}] Unexpected error: {e}")

    return record


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Enrich E24 listings with detail page data")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT, help="Input JSONL file")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of records (0=all)")
    parser.add_argument("--concurrent", type=int, default=1, help="Concurrent requests (keep at 1)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # Load records
    logger.info(f"Loading {input_path}...")
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    total = len(records)
    logger.info(f"Loaded {total} records")

    # Resume logic
    start_idx = 0
    enriched_records = []
    if args.resume and CHECKPOINT_FILE.exists():
        ckpt = json.loads(CHECKPOINT_FILE.read_text())
        start_idx = ckpt.get("last_idx", 0)
        enriched_file = OUTPUT_DIR / ckpt.get("enriched_file", "")
        if enriched_file.exists():
            with open(enriched_file, "r", encoding="utf-8") as f:
                enriched_records = [json.loads(l) for l in f if l.strip()]
        logger.info(f"Resuming from index {start_idx} ({len(enriched_records)} already done)")

    if args.limit > 0:
        records = records[: start_idx + args.limit]
        total = len(records)

    # Output file
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"encuentra24_enriched_{ts}.jsonl"

    # Write already-enriched records
    if enriched_records:
        with open(output_file, "w", encoding="utf-8") as f:
            for r in enriched_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Create HTTP client
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    ) as client:
        start_time = time.time()

        for idx in range(start_idx, total):
            record = records[idx]

            # Skip if already has description (already enriched)
            if record.get("description_es") and record.get("enriched_at"):
                enriched_records.append(record)
                continue

            enriched = await enrich_one(client, record, idx + 1, total)
            enriched_records.append(enriched)

            # Append to output file
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(enriched, ensure_ascii=False) + "\n")

            # Save checkpoint
            if (idx + 1) % PROGRESS_EVERY == 0:
                elapsed = time.time() - start_time
                rate = (idx + 1 - start_idx) / elapsed if elapsed > 0 else 0
                eta_sec = (total - idx - 1) / rate if rate > 0 else 0
                eta_min = eta_sec / 60

                ckpt = {
                    "last_idx": idx + 1,
                    "enriched_file": output_file.name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                CHECKPOINT_FILE.write_text(json.dumps(ckpt))

                with_desc = sum(1 for r in enriched_records if r.get("description_es"))
                with_imgs = sum(
                    1 for r in enriched_records if len(r.get("images", [])) > 1
                )

                logger.info(
                    f"\n  ── Progress: {idx+1}/{total} ({100*(idx+1)/total:.1f}%) ──\n"
                    f"  Enriched desc: {with_desc}  Multi-img: {with_imgs}\n"
                    f"  Rate: {rate:.2f} rec/sec  ETA: {eta_min:.0f} min\n"
                )

    # Final stats
    elapsed = time.time() - start_time
    with_desc = sum(1 for r in enriched_records if r.get("description_es"))
    with_multi_img = sum(1 for r in enriched_records if len(r.get("images", [])) > 1)
    with_beds = sum(1 for r in enriched_records if r.get("bedrooms"))
    with_baths = sum(1 for r in enriched_records if r.get("bathrooms"))
    with_lot = sum(1 for r in enriched_records if r.get("lot_size_m2"))
    avg_imgs = sum(len(r.get("images", [])) for r in enriched_records) / len(enriched_records)

    print(f"\n{'='*60}")
    print(f"ENRICHMENT COMPLETE")
    print(f"{'='*60}")
    print(f"  Total records:     {len(enriched_records)}")
    print(f"  With description:  {with_desc} ({100*with_desc/len(enriched_records):.0f}%)")
    print(f"  With 2+ images:    {with_multi_img} ({100*with_multi_img/len(enriched_records):.0f}%)")
    print(f"  Avg images/record: {avg_imgs:.1f}")
    print(f"  With bedrooms:     {with_beds}")
    print(f"  With bathrooms:    {with_baths}")
    print(f"  With lot size:     {with_lot}")
    print(f"  Duration:          {elapsed/60:.1f} min")
    print(f"  Output:            {output_file}")

    # Clean up checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


if __name__ == "__main__":
    asyncio.run(main())
