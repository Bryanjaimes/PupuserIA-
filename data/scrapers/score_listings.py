#!/usr/bin/env python3
"""
Score all PupuserIA listings for completeness and ad-readiness.
Self-contained — no project imports needed.  Just run:

    python score_listings.py
"""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

# ── Scoring config ──────────────────────────────────────────

FIELDS = [
    # (key, label, weight, check_mode, threshold, exempt_types)
    ("title",         "Title",          10, "truthy",  0,  ()),
    ("price_usd",     "Price",          10, "truthy",  0,  ()),
    ("images",        "Has images",      9, "list>N",  1,  ()),
    ("department",    "Department",      8, "truthy",  0,  ()),
    ("property_type", "Property type",   7, "truthy",  0,  ()),
    ("description",   "Description",     8, "length>N",10, ()),
    ("images",        "3+ photos",       7, "list>N",  3,  ()),
    ("area_m2",       "Area (m²)",       6, "truthy",  0,  ()),
    ("municipio",     "Municipio",       6, "truthy",  0,  ()),
    ("address",       "Address",         5, "truthy",  0,  ()),
    ("bedrooms",      "Bedrooms",        5, "truthy",  0,  ("land", "commercial", "farm")),
    ("bathrooms",     "Bathrooms",       5, "truthy",  0,  ("land", "commercial", "farm")),
    ("lot_size_m2",   "Lot size",        4, "truthy",  0,  ("apartment",)),
    ("images",        "6+ photos",       4, "list>N",  6,  ()),
    ("seller",        "Seller info",     2, "truthy",  0,  ()),
    ("listing_date",  "Listing date",    2, "truthy",  0,  ()),
    ("latitude",      "GPS coordinates", 3, "nonzero", 0,  ()),
    ("features",      "Feature details", 3, "list>N",  1,  ()),
]


def _check(record, key, mode, threshold):
    val = record.get(key)
    if mode == "truthy":
        return bool(val)
    if mode == "length>N":
        if key == "description":
            val = record.get("description") or record.get("description_es") or ""
        return isinstance(val, str) and len(val.strip()) > threshold
    if mode == "list>N":
        return isinstance(val, list) and len(val) > threshold
    if mode == "nonzero":
        try:
            return val is not None and float(val) != 0.0
        except (ValueError, TypeError):
            return False
    return bool(val)


def score(record):
    ptype = (record.get("property_type") or "").lower().strip()
    earned = 0.0
    total = 0.0
    missing = []

    for key, label, weight, mode, threshold, exempt_types in FIELDS:
        exempt = ptype in exempt_types
        filled = _check(record, key, mode, threshold)
        total += weight
        if exempt or filled:
            earned += weight
        if not exempt and not filled:
            missing.append(label)

    pct = round(earned / total * 100) if total else 0
    tier = "gold" if pct >= 80 else "silver" if pct >= 60 else "bronze"
    ad_ok = (
        bool(record.get("title"))
        and bool(record.get("price_usd"))
        and isinstance(record.get("images"), list)
        and len(record.get("images", [])) >= 1
        and pct >= 50
    )

    record["completeness_score"] = pct
    record["quality_tier"] = tier
    record["missing_fields"] = missing
    record["ad_ready"] = ad_ok
    return record


# ── Main ────────────────────────────────────────────────────

INPUT = Path("data/scraper_output/all_listings_20260220.jsonl")

print(f"Loading {INPUT} ...")
with open(INPUT, "r", encoding="utf-8") as f:
    records = [json.loads(l) for l in f if l.strip()]
print(f"  {len(records)} records")

scored = [score(r) for r in records]

# Write JSONL (full)
out_jsonl = INPUT.with_name("all_listings_scored.jsonl")
with open(out_jsonl, "w", encoding="utf-8") as f:
    for r in scored:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# Write JSON (frontend-friendly)
out_json = INPUT.with_name("all_listings_scored.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(scored, f, ensure_ascii=False, indent=2)

# ── Report ──────────────────────────────────────────────────

n = len(scored)
scores = sorted(r["completeness_score"] for r in scored)
tiers = Counter(r["quality_tier"] for r in scored)
ad_ready = sum(1 for r in scored if r["ad_ready"])
miss = Counter()
for r in scored:
    for m in r["missing_fields"]:
        miss[m] += 1

print(f"\n{'='*60}")
print(f"  PupuserIA Listing Quality Report")
print(f"{'='*60}")
print(f"  Total:    {n}")
print(f"  Avg:      {sum(scores)/n:.0f}   Median: {scores[n//2]}   Range: {scores[0]}-{scores[-1]}")
print(f"\n  ★ Gold:   {tiers['gold']:4d} ({100*tiers['gold']/n:.0f}%)")
print(f"  ☆ Silver: {tiers['silver']:4d} ({100*tiers['silver']/n:.0f}%)")
print(f"  ○ Bronze: {tiers['bronze']:4d} ({100*tiers['bronze']/n:.0f}%)")
print(f"\n  Ad-ready: {ad_ready} ({100*ad_ready/n:.0f}%)")
print(f"\n  Top gaps:")
for label, count in miss.most_common(10):
    print(f"    {label:20s} {count:4d} ({100*count/n:.0f}%)")
print(f"\n  → {out_jsonl}")
print(f"  → {out_json}  ({os.path.getsize(out_json)/1024/1024:.1f} MB)")
print(f"{'='*60}")
