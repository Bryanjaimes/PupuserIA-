"""Quick check of scraped JSONL output quality."""
import json
import glob
import os

# Find the most recent JSONL file
pattern = "data/scraper_output/realtor_*.jsonl"
files = sorted(glob.glob(pattern))
if not files:
    print("No JSONL files found")
    exit()

filepath = files[-1]
print(f"Reading: {filepath}")

with open(filepath, "r", encoding="utf-8") as f:
    props = [json.loads(line) for line in f if line.strip()]

# Show first property
p = props[0]
print(f"\n{'='*60}")
print(f"SAMPLE PROPERTY:")
print(f"{'='*60}")
print(json.dumps(p, indent=2, ensure_ascii=False)[:3000])

# Stats
print(f"\n{'='*60}")
print(f"QUALITY STATS ({len(props)} properties)")
print(f"{'='*60}")
print(f"  With title:       {sum(1 for p in props if p.get('title'))}")
print(f"  With price:       {sum(1 for p in props if p.get('price_usd'))}")
print(f"  With description: {sum(1 for p in props if p.get('description') or p.get('description_es'))}")
print(f"  With images:      {sum(1 for p in props if p.get('images'))}")
print(f"  Avg images/prop:  {sum(len(p.get('images',[])) for p in props)/len(props):.1f}")
print(f"  With area_m2:     {sum(1 for p in props if p.get('area_m2'))}")
print(f"  With lot_size:    {sum(1 for p in props if p.get('lot_size_m2'))}")
print(f"  With department:  {sum(1 for p in props if p.get('department'))}")
print(f"  With municipio:   {sum(1 for p in props if p.get('municipio'))}")
print(f"  With bedrooms:    {sum(1 for p in props if p.get('bedrooms') is not None)}")
print(f"  With bathrooms:   {sum(1 for p in props if p.get('bathrooms') is not None)}")
print(f"  With prop type:   {sum(1 for p in props if p.get('property_type'))}")

# Price distribution
prices = [p['price_usd'] for p in props if p.get('price_usd')]
if prices:
    prices.sort()
    print(f"\n  Price range:  ${min(prices):,.0f} — ${max(prices):,.0f}")
    print(f"  Median price: ${prices[len(prices)//2]:,.0f}")
    print(f"  Avg price:    ${sum(prices)/len(prices):,.0f}")

# Department breakdown
depts = {}
for p in props:
    d = p.get('department') or 'Unknown'
    depts[d] = depts.get(d, 0) + 1
print(f"\n  Departments:")
for d, c in sorted(depts.items(), key=lambda x: -x[1]):
    print(f"    {d}: {c}")

# Property type breakdown
types = {}
for p in props:
    t = p.get('property_type') or 'unknown'
    types[t] = types.get(t, 0) + 1
print(f"\n  Property types:")
for t, c in sorted(types.items(), key=lambda x: -x[1]):
    print(f"    {t}: {c}")
