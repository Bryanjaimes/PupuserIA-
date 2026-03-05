#!/usr/bin/env python3
"""Quick audit of image domains in scored listings."""
import json
from collections import Counter
from urllib.parse import urlparse

data = json.load(open("data/scraper_output/all_listings_scored.json", "r", encoding="utf-8"))

domains = Counter()
total_imgs = 0
for r in data:
    for img in (r.get("images") or []):
        total_imgs += 1
        try:
            domains[urlparse(img).hostname] += 1
        except:
            pass

with_img = sum(1 for r in data if r.get("images"))
print(f"Total images: {total_imgs}")
print(f"Listings with images: {with_img}/{len(data)}")
print("Domains:")
for d, c in domains.most_common(20):
    print(f"  {d}: {c}")
