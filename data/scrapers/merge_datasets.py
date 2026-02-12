#!/usr/bin/env python3
"""
Merge multiple realtor.com JSONL scraper outputs into a single
deduplicated dataset, preferring records with the richest detail data.
"""

import json
import sys
from pathlib import Path


def richness_score(record: dict) -> int:
    """Score a record by how much detail data it has."""
    score = 0
    if record.get("description"):
        score += 3
    if record.get("description_es"):
        score += 3
    if record.get("images") and len(record["images"]) > 0:
        score += 2
    if record.get("features") and len(record["features"]) > 0:
        score += 1
    if record.get("area_m2"):
        score += 1
    if record.get("lot_size_m2"):
        score += 1
    if record.get("bedrooms") is not None:
        score += 1
    if record.get("bathrooms") is not None:
        score += 1
    if record.get("latitude") is not None:
        score += 1
    if record.get("listing_date"):
        score += 1
    if record.get("property_type"):
        score += 1
    if record.get("department"):
        score += 1
    if record.get("municipio"):
        score += 1
    if record.get("price_usd"):
        score += 1
    return score


def merge_records(existing: dict, new: dict) -> dict:
    """Merge two records, keeping the richest data from each."""
    merged = dict(existing)
    
    # If the new record has a higher richness score, prefer it as the base
    if richness_score(new) > richness_score(existing):
        merged = dict(new)
        # But fill in any missing fields from the existing record
        for key, val in existing.items():
            if not merged.get(key) and val:
                merged[key] = val
    else:
        # Fill in missing fields from the new record
        for key, val in new.items():
            if not merged.get(key) and val:
                merged[key] = val
    
    # Always take the longer images list
    existing_imgs = existing.get("images", [])
    new_imgs = new.get("images", [])
    if len(new_imgs) > len(existing_imgs):
        merged["images"] = new_imgs
    
    # Always take the longer description
    for desc_key in ("description", "description_es"):
        ed = existing.get(desc_key, "")
        nd = new.get(desc_key, "")
        if len(nd) > len(ed):
            merged[desc_key] = nd
    
    return merged


def main():
    output_dir = Path(__file__).parent / "data" / "scraper_output"
    
    # Files to merge — the detail-enriched runs
    files_to_merge = [
        # Earlier full scrape (no details, 528 properties — good for basic coverage)
        output_dir / "realtor_all_20260210_110019.jsonl",
        # First detail-enriched run (200 properties, pages 1-8)
        output_dir / "realtor_all_20260210_115840.jsonl",
        # Second detail-enriched run (300 properties, pages 9-21)
        output_dir / "realtor_all_20260210_131343.jsonl",
    ]
    
    # Merge all records, keyed by source_url
    all_records: dict[str, dict] = {}
    
    for filepath in files_to_merge:
        if not filepath.exists():
            print(f"  SKIP (not found): {filepath.name}")
            continue
        
        count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                url = record.get("source_url", "")
                if not url:
                    continue
                
                count += 1
                if url in all_records:
                    all_records[url] = merge_records(all_records[url], record)
                else:
                    all_records[url] = record
        
        print(f"  Loaded {count} records from {filepath.name}")
    
    # Sort by department then price
    sorted_records = sorted(
        all_records.values(),
        key=lambda r: (r.get("department", ""), r.get("price_usd") or 0),
    )
    
    # Write merged output
    output_file = output_dir / "realtor_merged_all.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for record in sorted_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    # Stats
    total = len(sorted_records)
    with_desc = sum(1 for r in sorted_records if r.get("description") or r.get("description_es"))
    with_images = sum(1 for r in sorted_records if r.get("images"))
    with_price = sum(1 for r in sorted_records if r.get("price_usd"))
    with_dept = sum(1 for r in sorted_records if r.get("department"))
    
    depts = {}
    for r in sorted_records:
        d = r.get("department", "Unknown") or "Unknown"
        depts[d] = depts.get(d, 0) + 1
    
    prices = [r["price_usd"] for r in sorted_records if r.get("price_usd")]
    avg_price = sum(prices) / len(prices) if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    
    print(f"\n{'='*60}")
    print(f"MERGED DATASET SUMMARY")
    print(f"{'='*60}")
    print(f"  Total unique properties: {total}")
    print(f"  With description:        {with_desc} ({100*with_desc/total:.0f}%)")
    print(f"  With images:             {with_images} ({100*with_images/total:.0f}%)")
    print(f"  With price:              {with_price} ({100*with_price/total:.0f}%)")
    print(f"  With department:         {with_dept} ({100*with_dept/total:.0f}%)")
    print(f"  Price range:             ${min_price:,.0f} — ${max_price:,.0f}")
    print(f"  Average price:           ${avg_price:,.0f}")
    print(f"\n  By department:")
    for dept, count in sorted(depts.items(), key=lambda x: -x[1]):
        print(f"    {dept:20s}: {count}")
    print(f"\n  Output: {output_file}")
    print(f"  Size:   {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
