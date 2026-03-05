"""Live tests for the scraped-data / properties endpoints.

Updated: image URLs and source URLs are stripped for copyright safety.
Responses now include `image_count` and `source_domain` instead.
"""
import httpx

BASE = "http://127.0.0.1:8000/api/v1/properties"

# 1. Paginated listing (default page 1, 50 items)
print("=== 1. GET /properties (page 1, default 50) ===")
r = httpx.get(BASE)
assert r.status_code == 200
d = r.json()
print(f"  Total records: {d['total']}")
print(f"  Page: {d['page']}, Page size: {d['page_size']}")
print(f"  Results on this page: {len(d['results'])}")
print(f"  Source file: {d['source_file']}")
assert d["total"] > 0
assert len(d["results"]) <= 50

# Verify image URLs are stripped
first = d["results"][0]
assert "images" not in first, "images field should be stripped!"
assert "source_url" not in first, "source_url field should be stripped!"
assert "image_count" in first, "image_count should be present"
print(f"  ✓ No raw image URLs — image_count={first['image_count']}, source_domain={first.get('source_domain')}")

# 2. Paginated with filters
print("=== 2. GET /properties?department=San Salvador&page_size=5 ===")
r = httpx.get(BASE, params={"department": "San Salvador", "page_size": 5})
assert r.status_code == 200
d = r.json()
print(f"  San Salvador records: {d['total']}")
print(f"  Returned: {len(d['results'])}")
for rec in d["results"][:3]:
    price = f"${rec['price_usd']:,.0f}" if rec.get("price_usd") else "N/A"
    print(f"    {rec['id']} | {rec['property_type']} | {price} | imgs={rec['image_count']}")

# 3. Filter by price range
print("=== 3. GET /properties?min_price=100000&max_price=200000 ===")
r = httpx.get(BASE, params={"min_price": 100000, "max_price": 200000, "page_size": 5})
assert r.status_code == 200
d = r.json()
print(f"  In $100K-$200K range: {d['total']}")

# 4. Single property by ID
print("=== 4. GET /properties/PIA-000001 ===")
r = httpx.get(f"{BASE}/PIA-000001")
assert r.status_code == 200
prop = r.json()
print(f"  ID: {prop['id']}")
print(f"  Title: {prop['title'][:60]}...")
price = f"${prop['price_usd']:,.0f}" if prop.get("price_usd") else "N/A"
print(f"  Price: {price}")
print(f"  Type: {prop['property_type']}")
print(f"  Quality: {prop.get('quality_tier', 'N/A')}")
print(f"  Image count: {prop['image_count']}")
print(f"  Source domain: {prop.get('source_domain')}")
assert "images" not in prop, "images should be stripped from single-property response too"

# 5. Property not found
print("=== 5. GET /properties/NONEXISTENT ===")
r = httpx.get(f"{BASE}/NONEXISTENT")
assert r.status_code == 404
print(f"  Status: {r.status_code} ✓")

# 6. Stats
print("=== 6. GET /properties/stats ===")
r = httpx.get(f"{BASE}/stats")
assert r.status_code == 200
s = r.json()
print(f"  Total records: {s['total_records']}")
print(f"  With price: {s['with_price']}")
avg = f"${s['avg_price_usd']:,.0f}" if s.get("avg_price_usd") else "N/A"
print(f"  Avg price: {avg}")
print(f"  Departments: {list(s['by_department'].keys())[:5]}...")
print(f"  Property types: {s['by_property_type']}")
print(f"  Quality tiers: {s['by_quality_tier']}")

# 7. Source files
print("=== 7. GET /properties/sources ===")
r = httpx.get(f"{BASE}/sources")
assert r.status_code == 200
files = r.json()
print(f"  JSONL files: {len(files)}")
for f in files[:5]:
    print(f"    {f['filename']} ({f['size_bytes'] / 1024:.0f} KB)")

print(f"\n✅ All 7 properties endpoint tests passed!")
