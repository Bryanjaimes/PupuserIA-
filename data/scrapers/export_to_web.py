#!/usr/bin/env python3
"""
Export scored listings → apps/web/public/data/properties.json
Self-contained. Deduplicates by title AND description. Maps to frontend schema.

    python export_to_web.py
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

INPUT_ENRICHED = Path("data/scraper_output/all_listings_enriched.json")
INPUT_SCORED   = Path("data/scraper_output/all_listings_scored.json")
INPUT  = INPUT_ENRICHED if INPUT_ENRICHED.exists() else INPUT_SCORED
OUTPUT = Path("../../apps/web/public/data/properties.json")

print(f"Loading {INPUT} ...")
with open(INPUT, "r", encoding="utf-8") as f:
    records = json.load(f)
print(f"  {len(records)} raw records")

# ── Deduplicate by normalized title ──────────────────

def norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s

seen_titles: dict[str, int] = {}
deduped: list[dict] = []

for r in records:
    title = r.get("title") or ""
    key = norm(title)
    if not key:
        deduped.append(r)
        continue
    if key in seen_titles:
        idx = seen_titles[key]
        if r.get("completeness_score", 0) > deduped[idx].get("completeness_score", 0):
            deduped[idx] = r
    else:
        seen_titles[key] = len(deduped)
        deduped.append(r)

title_dupes = len(records) - len(deduped)
print(f"  Title dupes removed: {title_dupes} → {len(deduped)}")

# ── Deduplicate by description+department ────────────

desc_keys: dict[str, int] = {}
final: list[dict] = []
desc_dupes = 0

for r in deduped:
    desc = r.get("description") or ""
    dept = (r.get("department") or "").lower()
    dk = norm(desc)
    if dk and len(dk) > 40:
        combo = f"{dept}:{dk}"
        if combo in desc_keys:
            idx = desc_keys[combo]
            if r.get("completeness_score", 0) > final[idx].get("completeness_score", 0):
                final[idx] = r
            desc_dupes += 1
            continue
        desc_keys[combo] = len(final)
    final.append(r)

print(f"  Description dupes removed: {desc_dupes} → {len(final)}")

# ── Map to frontend schema ───────────────────────────

mapped = []
for i, r in enumerate(final):
    images = r.get("images") or []
    thumb = images[0] if images else None
    score = r.get("completeness_score", 0)
    tier = r.get("quality_tier", "bronze")
    ai = r.get("ai_enrichment", {})

    mapped.append({
        "id": r.get("id", f"PIA-{i+1:06d}"),
        "title": r.get("title") or "",
        "title_es": r.get("title") or "",
        "department": r.get("department") or "",
        "municipio": r.get("municipio") or "",
        "price_usd": r.get("price_usd"),
        "ai_valuation_usd": None,
        "bedrooms": r.get("bedrooms"),
        "bathrooms": r.get("bathrooms"),
        "area_m2": r.get("area_m2"),
        "lot_size_m2": r.get("lot_size_m2"),
        "property_type": (r.get("property_type") or "unknown").lower(),
        "latitude": r.get("latitude") or 0,
        "longitude": r.get("longitude") or 0,
        "thumbnail_url": thumb,
        "images": images,
        "is_featured": tier == "gold",
        "neighborhood_score": score,
        "features": r.get("features") or [],
        "description": r.get("description") or "",
        "description_es": r.get("description") or "",
        "address": r.get("address") or "",
        "listing_date": r.get("listing_date"),
        "seller": r.get("seller"),
        "completeness_score": score,
        "quality_tier": tier,
        "missing_fields": r.get("missing_fields") or [],
        "ad_ready": r.get("ad_ready", False),
        # AI enrichment fields
        "impact_score": ai.get("impact_score"),
        "is_single_story": ai.get("is_single_story"),
        "needs_remodel": ai.get("needs_remodel"),
        "ideal_for": ai.get("ideal_for", []),
        "english_summary": ai.get("english_summary"),
        "family_friendly_score": ai.get("family_friendly_score"),
        "investment_potential": ai.get("investment_potential"),
        "surf_proximity": ai.get("surf_proximity"),
        "walkability_estimate": ai.get("walkability_estimate"),
    })

# ── Write ────────────────────────────────────────────

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(mapped, f, ensure_ascii=False)

size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
print(f"\n  → {OUTPUT}  ({size_mb:.1f} MB, {len(mapped)} listings)")

types = Counter(r["property_type"] for r in mapped)
depts = Counter(r["department"] for r in mapped)
featured = sum(1 for r in mapped if r["is_featured"])
with_desc = sum(1 for r in mapped if len(r["description"]) > 10)
with_img = sum(1 for r in mapped if r["images"])

print(f"  Featured (gold): {featured}")
print(f"  With description: {with_desc}")
print(f"  With images: {with_img}")
print(f"  Types: {dict(types.most_common(10))}")
print(f"  Top depts: {dict(depts.most_common(5))}")
