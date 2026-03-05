"""Live tests for Swagger dropdown + US valuation + both OpenAPI specs."""
import httpx
import json

BASE = "http://127.0.0.1:8000"

# 1. Both Swagger UIs are accessible
print("=== 1. Swagger UI pages ===")
r = httpx.get(f"{BASE}/api/docs")
assert r.status_code == 200
assert "swagger-ui" in r.text.lower()
r2 = httpx.get(f"{BASE}/api/us/docs")
assert r2.status_code == 200
assert "swagger-ui" in r2.text.lower()
print("  OK — ES docs at /api/docs, US docs at /api/us/docs")

# 2. El Salvador OpenAPI spec
print("=== 2. El Salvador OpenAPI spec ===")
r = httpx.get(f"{BASE}/api/openapi.json")
assert r.status_code == 200
es = r.json()
print(f"  Title: {es['info']['title']}")
print(f"  Paths: {len(es['paths'])}")

# 3. US Real Estate OpenAPI spec
print("=== 3. US Real Estate OpenAPI spec ===")
r = httpx.get(f"{BASE}/api/us/openapi.json")
assert r.status_code == 200
us = r.json()
print(f"  Title: {us['info']['title']}")
print(f"  Paths: {len(us['paths'])}")

# 4. US valuation — house in Los Angeles
print("=== 4. US valuation: house in LA ===")
r = httpx.post(f"{BASE}/api/us/valuation/estimate", json={
    "latitude": 34.05, "longitude": -118.24,
    "state": "CA", "county": "Los Angeles",
    "area_sqft": 1800, "bedrooms": 3, "bathrooms": 2.5,
    "year_built": 1985, "property_type": "single_family",
    "school_rating": 7,
})
assert r.status_code == 200
d = r.json()
print(f"  Estimated: ${d['estimated_value_usd']:,.0f}")
print(f"  Price/sqft: ${d['price_per_sqft']:.0f}")
print(f"  Confidence: {d['confidence_score']}")

# 5. US valuation — condo in Manhattan
print("=== 5. US valuation: condo in Manhattan ===")
r = httpx.post(f"{BASE}/api/us/valuation/estimate", json={
    "latitude": 40.76, "longitude": -73.97,
    "state": "NY", "county": "Manhattan",
    "area_sqft": 900, "bedrooms": 1, "bathrooms": 1,
    "year_built": 2010, "property_type": "condo",
    "has_pool": False, "school_rating": 8,
})
assert r.status_code == 200
d = r.json()
print(f"  Estimated: ${d['estimated_value_usd']:,.0f}")
print(f"  Price/sqft: ${d['price_per_sqft']:.0f}")

# 6. US valuation — foreclosure in Ohio
print("=== 6. US valuation: foreclosure in Ohio ===")
r = httpx.post(f"{BASE}/api/us/valuation/estimate", json={
    "latitude": 41.50, "longitude": -81.69,
    "state": "OH", "county": "Cuyahoga",
    "area_sqft": 1400, "bedrooms": 3, "bathrooms": 1.5,
    "year_built": 1955, "property_type": "single_family",
    "is_foreclosure": True,
})
assert r.status_code == 200
d = r.json()
print(f"  Estimated: ${d['estimated_value_usd']:,.0f}  (foreclosure discount applied)")
print(f"  Rental yield: {d['rental_yield_estimate']:.1%}")

# 7. US batch estimate
print("=== 7. US batch estimate (3 properties) ===")
batch = [
    {"latitude": 33.45, "longitude": -112.07, "state": "AZ", "area_sqft": 2000, "property_type": "single_family"},
    {"latitude": 47.61, "longitude": -122.33, "state": "WA", "county": "King", "area_sqft": 1500, "property_type": "townhouse"},
    {"latitude": 25.76, "longitude": -80.19, "state": "FL", "county": "Miami-Dade", "area_sqft": 1100, "property_type": "condo"},
]
r = httpx.post(f"{BASE}/api/us/valuation/batch-estimate", json=batch)
assert r.status_code == 200
results = r.json()
assert len(results) == 3
for i, res in enumerate(results):
    print(f"  [{i+1}] ${res['estimated_value_usd']:,.0f}  ({batch[i]['state']})")

# 8. US model info
print("=== 8. US model info ===")
r = httpx.get(f"{BASE}/api/us/valuation/model-info")
assert r.status_code == 200
d = r.json()
print(f"  Markets covered: {len(d['markets_covered'])} states")

# 9. US markets list
print("=== 9. US markets list ===")
r = httpx.get(f"{BASE}/api/us/valuation/markets")
assert r.status_code == 200
markets = r.json()
print(f"  States: {len(markets)}")
print(f"  Most expensive: HI=${markets.get('HI', '?')}/sqft, CA=${markets.get('CA', '?')}/sqft")
print(f"  Most affordable: WV=${markets.get('WV', '?')}/sqft, MS=${markets.get('MS', '?')}/sqft")

# 10. Validation errors
print("=== 10. US validation errors ===")
r = httpx.post(f"{BASE}/api/us/valuation/estimate", json={
    "latitude": 34.05, "longitude": -118.24, "state": "CA",
})
assert r.status_code == 422
print(f"  Missing area_sqft → 422 ✓")

r = httpx.post(f"{BASE}/api/us/valuation/estimate", json={
    "latitude": 34.05, "longitude": -118.24, "state": "CA", "area_sqft": -100,
})
assert r.status_code == 422
print(f"  Negative area → 422 ✓")

print("\n✅ All 10 live tests passed!")
