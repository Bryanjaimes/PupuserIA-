#!/usr/bin/env python3
"""Deep inspect the saved E24 detail page HTML."""
import json
import re

html = open("_probe_detail.html", "r", encoding="utf-8").read()

# Full JSON-LD Product
print("=== JSON-LD Product ===")
for m in re.finditer(
    r'<script type="application/ld\+json">(.*?)</script>', html, re.S
):
    d = json.loads(m.group(1))
    if d.get("@type") == "Product":
        print(json.dumps(d, indent=2, ensure_ascii=False)[:4000])

# Search for geo / coordinates
print("\n=== GEO SEARCH ===")
for pattern in [r"geo", r"latitude", r"longitude", r"latLng", r"coords", r"LatLng"]:
    for m in re.finditer(pattern, html, re.I):
        start = max(0, m.start() - 30)
        end = min(len(html), m.end() + 80)
        ctx = html[start:end].replace("\n", " ").replace("\r", " ")
        print(f"  [{pattern}] ...{ctx}...")

# Search for specific data patterns in JS
print("\n=== MARKER / MAP DATA ===")
for m in re.finditer(r"marker|initMap|map.*?center|LatLng", html, re.I):
    start = max(0, m.start() - 50)
    end = min(len(html), m.end() + 150)
    ctx = html[start:end].replace("\n", " ").replace("\r", " ")
    print(f"  ...{ctx[:200]}...")

# Find all images grouped by size variant
print("\n=== IMAGE VARIANTS ===")
imgs = re.findall(r"(https://photos\.encuentra24\.com/[^\"'\\]+)", html)
# Group by hash (last part before size)
by_hash = {}
for img in imgs:
    # e.g. .../31801322_f4317b → hash is f4317b
    parts = img.split("/")
    last = parts[-1] if parts else ""
    by_hash.setdefault(last, []).append(img)
unique_hashes = set()
for img in imgs:
    h = img.split("/")[-1]  # e.g. 31801322_f4317b
    unique_hashes.add(h)
print(f"  Unique image hashes: {len(unique_hashes)}")
for h in sorted(unique_hashes)[:10]:
    variants = [i for i in imgs if i.endswith(h)]
    print(f"    {h}: {len(variants)} variants")
    for v in variants[:2]:
        print(f"      {v}")

# Find description in HTML (non-JSON-LD)
print("\n=== DESCRIPTION IN HTML ===")
# Look for common description containers
for pat in [
    r'class="[^"]*(?:ad-body|ad-description|detail-body|listing-description)[^"]*"[^>]*>(.*?)</div>',
    r'class="[^"]*ann-box-desc[^"]*"[^>]*>(.*?)</div>',
    r'class="[^"]*d3-ad-view__description[^"]*"[^>]*>(.*?)</div>',
    r'itemprop="description"[^>]*>(.*?)</(?:div|span|p)',
]:
    for m in re.finditer(pat, html, re.S | re.I):
        text = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
        if len(text) > 20:
            print(f"  [match] {text[:300]}")

# Check for listing attributes / features table
print("\n=== FEATURES / ATTRIBUTES ===")
for pat in [
    r'class="[^"]*(?:feature|attribute|spec|detail-item|property-attr)[^"]*"[^>]*>(.*?)</(?:li|div|tr|dd)',
]:
    for m in re.finditer(pat, html, re.S | re.I):
        text = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
        if 3 < len(text) < 200:
            print(f"  {text[:100]}")
