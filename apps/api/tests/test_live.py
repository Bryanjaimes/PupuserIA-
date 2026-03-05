"""Live endpoint smoke tests — run against a running server."""
import httpx
import json

base = "http://127.0.0.1:8000/api/v1/valuation"

# Test 1: Standard house in San Salvador
print("=== 1. House in San Salvador (150m², 3bd/2ba) ===")
r = httpx.post(f"{base}/estimate", json={
    "latitude": 13.69, "longitude": -89.22,
    "department": "San Salvador", "municipio": "San Salvador",
    "area_m2": 150.0, "bedrooms": 3, "bathrooms": 2, "property_type": "house",
})
assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
d = r.json()
print(f"  ${d['estimated_value_usd']:,.0f}  (confidence: {d['confidence_score']})")
assert d["estimated_value_usd"] > 0

# Test 2: Beach apartment in La Libertad
print("=== 2. Beach apartment La Libertad (80m²) ===")
r = httpx.post(f"{base}/estimate", json={
    "latitude": 13.483, "longitude": -89.383,
    "department": "La Libertad", "municipio": "La Libertad",
    "area_m2": 80.0, "bedrooms": 2, "bathrooms": 1, "property_type": "apartment",
})
assert r.status_code == 200
d = r.json()
print(f"  ${d['estimated_value_usd']:,.0f}  (rental yield: {d['rental_yield_estimate']})")

# Test 3: Bank foreclosure in Santa Ana
print("=== 3. Bank foreclosure in Santa Ana (200m²) ===")
r = httpx.post(f"{base}/estimate", json={
    "latitude": 13.99, "longitude": -89.56,
    "department": "Santa Ana", "municipio": "Santa Ana",
    "area_m2": 200.0, "bedrooms": 4, "bathrooms": 3, "property_type": "house",
    "is_foreclosure": True,
})
assert r.status_code == 200
d = r.json()
print(f"  ${d['estimated_value_usd']:,.0f}")

# Test 4: Rural land in Morazán
print("=== 4. Rural land in Morazán (5,000 m²) ===")
r = httpx.post(f"{base}/estimate", json={
    "latitude": 13.77, "longitude": -88.10,
    "department": "Morazán", "municipio": "San Francisco Gotera",
    "area_m2": 5000.0, "property_type": "land",
})
assert r.status_code == 200
d = r.json()
print(f"  ${d['estimated_value_usd']:,.0f}")

# Test 5: Commercial property in San Miguel
print("=== 5. Commercial in San Miguel (300m²) ===")
r = httpx.post(f"{base}/estimate", json={
    "latitude": 13.48, "longitude": -88.18,
    "department": "San Miguel", "municipio": "San Miguel",
    "area_m2": 300.0, "property_type": "commercial",
})
assert r.status_code == 200
d = r.json()
print(f"  ${d['estimated_value_usd']:,.0f}")

# Test 6: Validation error — missing required field
print("=== 6. Validation error (missing area_m2) ===")
r = httpx.post(f"{base}/estimate", json={
    "latitude": 13.69, "longitude": -89.22, "department": "San Salvador",
})
assert r.status_code == 422, f"Expected 422, got {r.status_code}"
print(f"  Status: {r.status_code} ✓")

# Test 7: Validation error — latitude out of range
print("=== 7. Validation error (latitude out of range) ===")
r = httpx.post(f"{base}/estimate", json={
    "latitude": 50.0, "longitude": -89.22,
    "department": "San Salvador", "area_m2": 100,
})
assert r.status_code == 422
print(f"  Status: {r.status_code} ✓")

# Test 8: GET /model-info
print("=== 8. GET /model-info ===")
r = httpx.get(f"{base}/model-info")
assert r.status_code == 200
d = r.json()
print(f"  is_loaded: {d['is_loaded']}")
print(f"  model_version: {d['model_version']}")

# Test 9: Swagger docs accessible
print("=== 9. Swagger docs page ===")
r = httpx.get("http://127.0.0.1:8000/api/docs")
assert r.status_code == 200
print(f"  Status: {r.status_code} ✓ (OpenAPI docs served)")

print("\n✅ All 9 live endpoint tests passed!")
