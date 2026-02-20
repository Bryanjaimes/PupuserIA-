#!/usr/bin/env python3
"""
Merge all enriched listings into a single clean dataset.
Removes source attribution fields per user request ("We are now that source").

Usage:
    python merge_all.py
    python merge_all.py --e24 data/scraper_output/encuentra24_enriched_TIMESTAMP.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

OUTPUT_DIR = Path("data/scraper_output")

# Fields to remove (source attribution)
STRIP_FIELDS = {"source", "source_url", "raw_html", "scraped_at", "enriched_at"}

# Fields to keep in final output (ordered)
KEEP_FIELDS = [
    "id",
    "title",
    "description",
    "description_es",
    "price_usd",
    "price_currency",
    "property_type",
    "bedrooms",
    "bathrooms",
    "parking",
    "area_m2",
    "lot_size_m2",
    "department",
    "municipio",
    "canton",
    "address",
    "address_locality",
    "latitude",
    "longitude",
    "images",
    "features",
    "seller",
    "listing_date",
]


def find_latest_e24_enriched() -> Path | None:
    """Find the most recent E24 enriched file."""
    pattern = "encuentra24_enriched_*.jsonl"
    files = sorted(OUTPUT_DIR.glob(pattern))
    if files:
        # Return the largest one (most complete)
        return max(files, key=lambda f: f.stat().st_size)
    return None


def clean_record(record: dict, idx: int) -> dict:
    """Clean a record: strip source fields, assign ID, normalize."""
    clean = {"id": f"PIA-{idx:06d}"}

    for field in KEEP_FIELDS:
        if field == "id":
            continue
        val = record.get(field)

        # Normalize empty values
        if val is None or val == "" or val == []:
            continue
        if isinstance(val, str) and val.strip() == "":
            continue

        # Normalize price
        if field == "price_usd" and isinstance(val, str):
            nums = re.findall(r"[\d,.]+", val)
            if nums:
                try:
                    val = float(nums[0].replace(",", ""))
                except ValueError:
                    pass

        # Normalize coordinates (0 means missing)
        if field in ("latitude", "longitude"):
            if val == 0 or val == "0" or val == 0.0:
                continue

        # Clean up images list
        if field == "images" and isinstance(val, list):
            val = [img for img in val if img and isinstance(img, str)]
            if not val:
                continue

        # Clean up description
        if field in ("description", "description_es") and isinstance(val, str):
            val = val.strip()
            if len(val) < 5:
                continue

        clean[field] = val

    return clean


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def deduplicate(records: list[dict]) -> list[dict]:
    """Remove duplicates based on title + price + location."""
    seen = set()
    unique = []
    for r in records:
        key = (
            r.get("title", "").lower().strip()[:80],
            str(r.get("price_usd", "")).strip(),
            r.get("department", "").lower().strip(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def main():
    parser = argparse.ArgumentParser(description="Merge all enriched data")
    parser.add_argument("--e24", help="Path to E24 enriched JSONL")
    parser.add_argument("--realtor", default=str(OUTPUT_DIR / "realtor_enriched.jsonl"),
                        help="Path to Realtor enriched JSONL")
    args = parser.parse_args()

    # Find E24 enriched file
    if args.e24:
        e24_path = Path(args.e24)
    else:
        e24_path = find_latest_e24_enriched()

    if not e24_path or not e24_path.exists():
        print(f"ERROR: E24 enriched file not found. Use --e24 to specify path.")
        print(f"  Looked in: {OUTPUT_DIR}")
        sys.exit(1)

    realtor_path = Path(args.realtor)

    # Load data
    print(f"Loading E24:     {e24_path} ...", end=" ")
    e24_records = load_jsonl(e24_path)
    print(f"{len(e24_records)} records")

    realtor_records = []
    if realtor_path.exists():
        print(f"Loading Realtor: {realtor_path} ...", end=" ")
        realtor_records = load_jsonl(realtor_path)
        print(f"{len(realtor_records)} records")
    else:
        print(f"Realtor file not found: {realtor_path}")

    # Combine
    all_records = e24_records + realtor_records
    print(f"\nTotal before dedup: {len(all_records)}")

    # Deduplicate
    unique = deduplicate(all_records)
    print(f"After dedup:        {len(unique)}")

    # Clean and assign IDs
    cleaned = []
    for i, r in enumerate(unique, start=1):
        cleaned.append(clean_record(r, i))

    # Write output
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    output_file = OUTPUT_DIR / f"all_listings_{ts}.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for r in cleaned:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Also write JSON array version (for web app)
    output_json = OUTPUT_DIR / f"all_listings_{ts}.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    # Stats
    with_desc = sum(1 for r in cleaned if r.get("description") or r.get("description_es"))
    with_imgs = sum(1 for r in cleaned if len(r.get("images", [])) > 0)
    multi_imgs = sum(1 for r in cleaned if len(r.get("images", [])) > 1)
    with_beds = sum(1 for r in cleaned if r.get("bedrooms"))
    with_baths = sum(1 for r in cleaned if r.get("bathrooms"))
    with_area = sum(1 for r in cleaned if r.get("area_m2"))
    with_lot = sum(1 for r in cleaned if r.get("lot_size_m2"))
    with_coords = sum(1 for r in cleaned if r.get("latitude") and r.get("longitude"))
    with_date = sum(1 for r in cleaned if r.get("listing_date"))
    avg_imgs = sum(len(r.get("images", [])) for r in cleaned) / max(1, len(cleaned))
    avg_desc = sum(
        len(r.get("description", "") or r.get("description_es", ""))
        for r in cleaned
        if r.get("description") or r.get("description_es")
    ) / max(1, with_desc)

    n = len(cleaned)
    print(f"\n{'='*60}")
    print(f"  MERGED DATASET — PupuserIA")
    print(f"{'='*60}")
    print(f"  Total listings:    {n}")
    print(f"  Description:       {with_desc:4d} ({100*with_desc/n:5.1f}%)  avg {avg_desc:.0f}ch")
    print(f"  Images (any):      {with_imgs:4d} ({100*with_imgs/n:5.1f}%)")
    print(f"  Images (2+):       {multi_imgs:4d} ({100*multi_imgs/n:5.1f}%)  avg {avg_imgs:.1f}/listing")
    print(f"  Bedrooms:          {with_beds:4d} ({100*with_beds/n:5.1f}%)")
    print(f"  Bathrooms:         {with_baths:4d} ({100*with_baths/n:5.1f}%)")
    print(f"  Area m²:           {with_area:4d} ({100*with_area/n:5.1f}%)")
    print(f"  Lot size:          {with_lot:4d} ({100*with_lot/n:5.1f}%)")
    print(f"  Coordinates:       {with_coords:4d} ({100*with_coords/n:5.1f}%)")
    print(f"  Listing date:      {with_date:4d} ({100*with_date/n:5.1f}%)")
    print(f"  Source fields:     REMOVED (PupuserIA is the source)")
    print(f"\n  Output JSONL:      {output_file}")
    print(f"  Output JSON:       {output_json}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
