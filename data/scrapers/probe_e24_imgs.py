#!/usr/bin/env python3
"""Inspect E24 image patterns and gallery structure."""
import re

html = open("_probe_detail.html", "r", encoding="utf-8").read()

# Get distinct size prefixes
sizes = set()
for m in re.finditer(r"photos\.encuentra24\.com/(t_[^/]+)/", html):
    sizes.add(m.group(1))
print("Image size variants:", sorted(sizes))

# Count distinct photo hashes (exclude user photos)
hashes = set()
for m in re.finditer(r"/31801322_([a-f0-9]+)", html):
    hashes.add(m.group(1))
print(f"Distinct photo hashes for this listing: {len(hashes)}")
print("Hashes:", sorted(hashes))

# Best strategy: get largest variant (t_or_fh_l) of each unique hash
best_imgs = []
for h in sorted(hashes):
    best_imgs.append(
        f"https://photos.encuentra24.com/t_or_fh_l/f_auto/v1/sv/31/80/13/22/31801322_{h}"
    )
print(f"\nBest quality images ({len(best_imgs)}):")
for img in best_imgs:
    print(f"  {img}")

# Check for additional data in JS variables
print("\n=== JS DATA OBJECTS ===")
# Look for large JSON objects in script tags
for m in re.finditer(r"<script[^>]*>(.*?)</script>", html, re.S):
    content = m.group(1)
    if len(content) > 200 and ("adId" in content or "listing" in content or "property" in content):
        # trim
        snippet = content[:500].replace("\n", " ")
        print(f"  JS block ({len(content)} chars): {snippet[:200]}...")
