#!/usr/bin/env python3
"""Convert merged JSONL to static JSON for the Next.js frontend."""
import json
import uuid
from pathlib import Path

jsonl = Path(__file__).parent / "data" / "scraper_output" / "realtor_merged_all.jsonl"
out = Path(__file__).parent / ".." / ".." / "apps" / "web" / "public" / "data" / "properties.json"
out.parent.mkdir(parents=True, exist_ok=True)

properties = []
for line in jsonl.read_text(encoding="utf-8").strip().split("\n"):
    r = json.loads(line)
    imgs = r.get("images", [])
    p = {
        "id": r.get("content_hash", str(uuid.uuid4())[:8]),
        "title": r.get("title", ""),
        "title_es": (r.get("description_es", "") or "")[:80] or r.get("title", ""),
        "department": r.get("department", ""),
        "municipio": r.get("municipio", ""),
        "price_usd": r.get("price_usd"),
        "ai_valuation_usd": None,
        "bedrooms": r.get("bedrooms"),
        "bathrooms": r.get("bathrooms"),
        "area_m2": r.get("area_m2"),
        "lot_size_m2": r.get("lot_size_m2"),
        "property_type": r.get("property_type", ""),
        "latitude": r.get("latitude") or 0,
        "longitude": r.get("longitude") or 0,
        "thumbnail_url": imgs[0] if imgs else None,
        "images": imgs[:8],
        "is_featured": (r.get("price_usd") or 0) > 200000 and bool(r.get("description")),
        "neighborhood_score": None,
        "features": r.get("features", []),
        "description": r.get("description", ""),
        "description_es": r.get("description_es", ""),
        "source": r.get("source", "realtor_intl"),
        "source_url": r.get("source_url", ""),
        "listing_date": r.get("listing_date", ""),
        "address": r.get("address", ""),
    }
    properties.append(p)

out.write_text(json.dumps(properties, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(properties)} properties to {out.resolve()}")
print(f"Size: {out.stat().st_size / 1024:.0f} KB")
featured = sum(1 for p in properties if p["is_featured"])
print(f"Featured: {featured}")
