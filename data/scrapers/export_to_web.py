#!/usr/bin/env python3
"""Convert merged JSONL to static JSON for the Next.js frontend.

Geocodes properties missing coordinates using department/municipio
centroids with randomized jitter so pins don't stack on one point.
"""
import json
import random
import uuid
from pathlib import Path

# ── Department centroids (lat, lng) ──────────────────────────

DEPARTMENT_CENTROIDS: dict[str, tuple[float, float]] = {
    "San Salvador":   (13.6989, -89.1914),
    "La Libertad":    (13.4900, -89.3200),
    "Santa Ana":      (13.9940, -89.5597),
    "San Miguel":     (13.4833, -88.1833),
    "Sonsonate":      (13.7190, -89.7240),
    "Usulután":       (13.3500, -88.4500),
    "Ahuachapán":     (13.9214, -89.8450),
    "La Paz":         (13.5000, -88.9500),
    "La Unión":       (13.3400, -87.8400),
    "Chalatenango":   (14.0333, -88.9333),
    "Cuscatlán":      (13.7200, -88.9300),
    "Morazán":        (13.7500, -88.1000),
    "San Vicente":    (13.6333, -88.8000),
    "Cabañas":        (13.8600, -88.7500),
}

# Municipio-level centroids for higher-precision fallback
MUNICIPIO_CENTROIDS: dict[str, tuple[float, float]] = {
    # ── San Salvador department ──
    "San Salvador":      (13.6989, -89.1914),
    "Soyapango":         (13.7100, -89.1380),
    "Apopa":             (13.8070, -89.1810),
    "Mejicanos":         (13.7290, -89.2130),
    "Santa Tecla":       (13.6770, -89.2900),
    "Ciudad Delgado":    (13.7260, -89.1700),
    "Ilopango":          (13.6950, -89.1080),
    "Tonacatepeque":     (13.7790, -89.1120),
    "Cuscatancingo":     (13.7300, -89.1830),
    "San Marcos":        (13.6580, -89.1830),
    "San Martín":        (13.7870, -89.0570),
    "Antiguo Cuscatlán": (13.6700, -89.2500),
    "Ayutuxtepeque":     (13.7440, -89.2060),
    # ── La Libertad ──
    "La Libertad":       (13.4880, -89.3230),
    "Colón":             (13.7240, -89.3690),
    "Quezaltepeque":     (13.8310, -89.2720),
    "Opico":             (13.8620, -89.3900),
    "San Juan Opico":    (13.8760, -89.3570),
    "Ciudad Arce":       (13.8380, -89.4430),
    "Zaragoza":          (13.5900, -89.2900),
    "Tamanique":         (13.5100, -89.4000),
    "Teotepeque":        (13.5300, -89.4800),
    "Chiltiupán":        (13.5200, -89.5000),
    # ── Santa Ana ──
    "Santa Ana":         (13.9940, -89.5597),
    "Chalchuapa":        (13.9870, -89.6810),
    "Metapán":           (14.3330, -89.4500),
    "Coatepeque":        (13.9300, -89.5000),
    "Texistepeque":      (14.1300, -89.5000),
    "Candelaria de la Frontera": (14.1200, -89.6500),
    # ── San Miguel ──
    "San Miguel":        (13.4833, -88.1833),
    "Chinameca":         (13.5000, -88.3500),
    "Moncagua":          (13.5300, -88.2500),
    # ── Sonsonate ──
    "Sonsonate":         (13.7190, -89.7240),
    "Izalco":            (13.7450, -89.6730),
    "Nahuizalco":        (13.7740, -89.7370),
    "Acajutla":          (13.5930, -89.8270),
    "Juayúa":            (13.8430, -89.7480),
    "Apaneca":           (13.8590, -89.8040),
    # ── Ahuachapán ──
    "Ahuachapán":        (13.9214, -89.8450),
    "Atiquizaya":        (13.9700, -89.7500),
    "Concepción de Ataco": (13.8700, -89.8500),
    # ── La Paz ──
    "Zacatecoluca":      (13.5170, -88.8700),
    "San Luis La Herradura": (13.3300, -88.9700),
    "Olocuilta":         (13.5700, -89.1200),
    "San Pedro Masahuat": (13.5400, -89.0400),
    # ── Chalatenango ──
    "Chalatenango":      (14.0333, -88.9333),
    "La Palma":          (14.3200, -89.1600),
    "San Ignacio":       (14.3400, -89.1700),
    "Citalá":            (14.3800, -89.1800),
    # ── Usulután ──
    "Usulután":          (13.4410, -88.4400),
    "Jiquilisco":        (13.3210, -88.5730),
    "Santiago de María":  (13.4900, -88.4700),
    # ── Cuscatlán ──
    "Cojutepeque":       (13.7170, -88.9350),
    "San Pedro Perulapán": (13.7660, -88.9400),
    "Suchitoto":         (13.9380, -89.0280),
    # ── San Vicente ──
    "San Vicente":       (13.6333, -88.7840),
    # ── Cabañas ──
    "Sensuntepeque":     (13.8700, -88.6300),
    "Ilobasco":          (13.8420, -88.8450),
    # ── La Unión ──
    "La Unión":          (13.3400, -87.8400),
    "Conchagua":         (13.3100, -87.8700),
    # ── Morazán ──
    "Perquín":           (13.9600, -88.1600),
    "San Francisco Gotera": (13.7000, -88.1000),
}

# El Salvador bounding box for validation
ES_BOUNDS = {"lat_min": 13.0, "lat_max": 14.5, "lng_min": -90.2, "lng_max": -87.5}


def geocode(record: dict) -> tuple[float, float, bool]:
    """
    Return (lat, lng, is_exact) for a record.
    
    Priority:
      1. Exact coords from scraper (if valid and within El Salvador)
      2. Municipio centroid + jitter
      3. Department centroid + jitter
      4. Country center (San Salvador) + jitter
    """
    lat = record.get("latitude")
    lng = record.get("longitude")

    # Check if scraper provided valid coordinates
    if (
        lat is not None
        and lng is not None
        and lat != 0
        and lng != 0
        and ES_BOUNDS["lat_min"] <= lat <= ES_BOUNDS["lat_max"]
        and ES_BOUNDS["lng_min"] <= lng <= ES_BOUNDS["lng_max"]
    ):
        return lat, lng, True

    # Municipio centroid lookup
    municipio = record.get("municipio", "").strip()
    if municipio and municipio in MUNICIPIO_CENTROIDS:
        clat, clng = MUNICIPIO_CENTROIDS[municipio]
        # Small jitter (~200-500m) so pins don't stack
        return (
            clat + random.uniform(-0.003, 0.003),
            clng + random.uniform(-0.003, 0.003),
            False,
        )

    # Try fuzzy municipio match (partial match on address field)
    address = record.get("address", "")
    for muni_name, (clat, clng) in MUNICIPIO_CENTROIDS.items():
        if muni_name.lower() in address.lower():
            return (
                clat + random.uniform(-0.003, 0.003),
                clng + random.uniform(-0.003, 0.003),
                False,
            )

    # Department centroid fallback
    department = record.get("department", "").strip()
    if department and department in DEPARTMENT_CENTROIDS:
        clat, clng = DEPARTMENT_CENTROIDS[department]
        # Wider jitter (~1-2km) since department is less precise
        return (
            clat + random.uniform(-0.015, 0.015),
            clng + random.uniform(-0.015, 0.015),
            False,
        )

    # Last resort: San Salvador center
    return (
        13.6989 + random.uniform(-0.02, 0.02),
        -89.1914 + random.uniform(-0.02, 0.02),
        False,
    )


# ── Main export ──────────────────────────────────────────────

jsonl = Path(__file__).parent / "data" / "scraper_output" / "realtor_merged_all.jsonl"
out = Path(__file__).parent / ".." / ".." / "apps" / "web" / "public" / "data" / "properties.json"
out.parent.mkdir(parents=True, exist_ok=True)

random.seed(42)  # Reproducible jitter

properties = []
exact_coords = 0
approx_coords = 0

for line in jsonl.read_text(encoding="utf-8").strip().split("\n"):
    r = json.loads(line)
    imgs = r.get("images", [])

    lat, lng, is_exact = geocode(r)
    if is_exact:
        exact_coords += 1
    else:
        approx_coords += 1

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
        "latitude": round(lat, 6),
        "longitude": round(lng, 6),
        "coords_exact": is_exact,
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
print(f"Coordinates: {exact_coords} exact, {approx_coords} estimated (centroid + jitter)")
featured = sum(1 for p in properties if p["is_featured"])
print(f"Featured: {featured}")
