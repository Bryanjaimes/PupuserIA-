"""
Realtor Enrichment — Parse beds/baths from features list.

The Realtor features list contains entries like:
  ['Land', '6', '2', '|\nHouse', 'Land']
  ['Industrial/Warehouse', '2', '1', '|\nHouse', '3']

The pattern appears to be: property_type, beds_count, baths_count, separator, ...
Also tries to fetch description from Realtor detail pages for records missing it.
"""
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

INPUT = Path("data/scraper_output/realtor_merged_all.jsonl")
OUTPUT = Path("data/scraper_output/realtor_enriched.jsonl")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}


def parse_beds_baths_from_features(features: list) -> dict:
    """
    Parse beds/baths from the Realtor features list.
    
    Pattern observed:
    - Features alternate between property types and numbers
    - First number after property type = beds
    - Second number = baths  
    - '|\\n' separates multiple property entries
    """
    result = {}
    
    # Collect all numeric values (likely beds/baths)
    numbers = []
    for feat in features:
        feat_clean = feat.strip()
        if feat_clean.isdigit():
            numbers.append(int(feat_clean))
        elif re.match(r"^\d+\.?\d*$", feat_clean):
            numbers.append(float(feat_clean))
    
    # If we have at least 2 numbers, first is likely beds, second baths
    if len(numbers) >= 2:
        beds, baths = numbers[0], numbers[1]
        if 0 < beds <= 50:  # Sanity check
            result["bedrooms"] = int(beds)
        if 0 < baths <= 50:
            result["bathrooms"] = int(baths) if baths == int(baths) else baths
    elif len(numbers) == 1:
        if 0 < numbers[0] <= 50:
            result["bedrooms"] = int(numbers[0])
    
    return result


def fetch_realtor_description(url: str) -> str:
    """Try to fetch description from Realtor detail page."""
    try:
        resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
        if resp.status_code != 200:
            return ""
        
        html = resp.text
        
        # Look for JSON-LD
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            try:
                d = json.loads(m.group(1))
                desc = d.get("description", "")
                if desc and len(desc.strip()) > 20:
                    return desc.strip()
            except:
                continue
        
        # Look for description in meta tag
        m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html, re.I)
        if m and len(m.group(1)) > 30:
            return m.group(1).strip()
        
        # Look for description class
        m = re.search(r'class="[^"]*listing-description[^"]*"[^>]*>(.*?)</div>', html, re.S | re.I)
        if m:
            text = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
            text = re.sub(r"\s+", " ", text)
            if len(text) > 20:
                return text[:3000]
        
        return ""
    except Exception as e:
        return ""


def main():
    print(f"Loading {INPUT}...")
    with open(INPUT, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    
    total = len(records)
    print(f"Loaded {total} Realtor records")
    
    # Phase 1: Parse beds/baths from features
    print("\n=== Phase 1: Parse beds/baths from features ===")
    parsed_beds = 0
    parsed_baths = 0
    
    for r in records:
        if not r.get("bedrooms"):
            feats = r.get("features", [])
            parsed = parse_beds_baths_from_features(feats)
            if parsed.get("bedrooms"):
                r["bedrooms"] = parsed["bedrooms"]
                parsed_beds += 1
            if parsed.get("bathrooms") and not r.get("bathrooms"):
                r["bathrooms"] = parsed["bathrooms"]
                parsed_baths += 1
    
    print(f"  Parsed beds from features: {parsed_beds}")
    print(f"  Parsed baths from features: {parsed_baths}")
    
    # Phase 2: Try to fetch descriptions for records missing them
    no_desc = [r for r in records if not r.get("description") or len(r.get("description", "")) <= 10]
    print(f"\n=== Phase 2: Fetch descriptions for {len(no_desc)} records ===")
    
    fetched_desc = 0
    for i, r in enumerate(no_desc):
        url = r.get("source_url", "")
        if not url:
            continue
        
        if i > 0 and i % 10 == 0:
            print(f"  Progress: {i}/{len(no_desc)} (fetched: {fetched_desc})")
        
        time.sleep(1.5)  # Rate limit
        desc = fetch_realtor_description(url)
        if desc:
            r["description"] = desc
            fetched_desc += 1
    
    print(f"  Fetched descriptions: {fetched_desc}")
    
    # Write output
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for r in records:
            r["enriched_at"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    # Stats
    with_desc = sum(1 for r in records if r.get("description") and len(r["description"]) > 10)
    with_beds = sum(1 for r in records if r.get("bedrooms"))
    with_baths = sum(1 for r in records if r.get("bathrooms"))
    avg_imgs = sum(len(r.get("images", [])) for r in records) / len(records)
    
    print(f"\n{'='*60}")
    print(f"REALTOR ENRICHMENT COMPLETE")
    print(f"{'='*60}")
    print(f"  Total records:     {total}")
    print(f"  With description:  {with_desc} ({100*with_desc/total:.0f}%)")
    print(f"  With bedrooms:     {with_beds} ({100*with_beds/total:.0f}%)")
    print(f"  With bathrooms:    {with_baths} ({100*with_baths/total:.0f}%)")
    print(f"  Avg images/record: {avg_imgs:.1f}")
    print(f"  Output:            {OUTPUT}")


if __name__ == "__main__":
    main()
