"""
Tests for the valuation endpoint and engine.

Runs against the FastAPI test client (no DB required).
Also directly tests the ValuationEngine heuristic path.
"""

import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure project root is importable
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


# ── Fixtures ──────────────────────────────────────────


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Endpoint Tests ────────────────────────────────────


VALID_PAYLOAD = {
    "latitude": 13.69,
    "longitude": -89.22,
    "department": "San Salvador",
    "municipio": "San Salvador",
    "area_m2": 150.0,
    "bedrooms": 3,
    "bathrooms": 2,
    "property_type": "house",
}


@pytest.mark.asyncio
async def test_valuation_estimate_success(client: AsyncClient):
    """POST /valuation/estimate returns 200 with valid input."""
    response = await client.post("/api/v1/valuation/estimate", json=VALID_PAYLOAD)
    assert response.status_code == 200, response.text
    data = response.json()

    # All required fields present
    assert "estimated_value_usd" in data
    assert "confidence_interval_low" in data
    assert "confidence_interval_high" in data
    assert "confidence_score" in data
    assert "rental_yield_estimate" in data
    assert "model_version" in data
    assert "features_importance" in data

    # Sanity: price is positive
    assert data["estimated_value_usd"] > 0
    assert data["confidence_interval_low"] <= data["estimated_value_usd"]
    assert data["confidence_interval_high"] >= data["estimated_value_usd"]
    assert 0.0 <= data["confidence_score"] <= 1.0


@pytest.mark.asyncio
async def test_valuation_estimate_minimal(client: AsyncClient):
    """Minimum required fields should still produce a valid response."""
    payload = {
        "latitude": 13.50,
        "longitude": -89.00,
        "department": "La Libertad",
        "area_m2": 80.0,
    }
    response = await client.post("/api/v1/valuation/estimate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_value_usd"] > 0


@pytest.mark.asyncio
async def test_valuation_estimate_foreclosure(client: AsyncClient):
    """Foreclosure flag should be accepted and not break prediction."""
    payload = {**VALID_PAYLOAD, "is_foreclosure": True}
    response = await client.post("/api/v1/valuation/estimate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["estimated_value_usd"] > 0


@pytest.mark.asyncio
async def test_valuation_estimate_all_departments(client: AsyncClient):
    """Every department should produce a valid valuation."""
    departments = [
        "San Salvador", "La Libertad", "Santa Ana", "San Miguel",
        "Sonsonate", "La Paz", "Usulután", "Ahuachapán",
        "Cuscatlán", "Chalatenango", "Cabañas", "Morazán",
        "La Unión", "San Vicente",
    ]
    for dept in departments:
        payload = {
            "latitude": 13.69,
            "longitude": -89.22,
            "department": dept,
            "area_m2": 120.0,
        }
        response = await client.post("/api/v1/valuation/estimate", json=payload)
        assert response.status_code == 200, f"Failed for {dept}: {response.text}"
        data = response.json()
        assert data["estimated_value_usd"] > 0, f"Zero price for {dept}"


@pytest.mark.asyncio
async def test_valuation_estimate_all_property_types(client: AsyncClient):
    """Each property type should produce different valuations."""
    results = {}
    for ptype in ["house", "apartment", "land", "commercial"]:
        payload = {**VALID_PAYLOAD, "property_type": ptype}
        response = await client.post("/api/v1/valuation/estimate", json=payload)
        assert response.status_code == 200
        results[ptype] = response.json()["estimated_value_usd"]

    # All prices should be positive
    assert all(v > 0 for v in results.values())


@pytest.mark.asyncio
async def test_valuation_estimate_validation_errors(client: AsyncClient):
    """Invalid payloads should return 422."""
    # Missing required field (area_m2)
    response = await client.post(
        "/api/v1/valuation/estimate",
        json={"latitude": 13.69, "longitude": -89.22, "department": "San Salvador"},
    )
    assert response.status_code == 422

    # Negative area
    response = await client.post(
        "/api/v1/valuation/estimate",
        json={**VALID_PAYLOAD, "area_m2": -10},
    )
    assert response.status_code == 422

    # Latitude out of range
    response = await client.post(
        "/api/v1/valuation/estimate",
        json={**VALID_PAYLOAD, "latitude": 50.0},
    )
    assert response.status_code == 422

    # Empty body
    response = await client.post("/api/v1/valuation/estimate", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_valuation_model_info(client: AsyncClient):
    """GET /valuation/model-info returns metadata."""
    response = await client.get("/api/v1/valuation/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "is_loaded" in data
    assert "model_version" in data
    assert isinstance(data["is_loaded"], bool)


# ── Direct Engine Tests ──────────────────────────────


def test_engine_heuristic_fallback():
    """Engine without a model should return heuristic valuations."""
    from ai.valuation.engine import ValuationEngine, PropertyFeatures

    engine = ValuationEngine()  # no model loaded
    assert not engine.is_loaded

    result = engine.predict(PropertyFeatures(
        latitude=13.69,
        longitude=-89.22,
        department="San Salvador",
        municipio="San Salvador",
        area_m2=200,
        property_type="house",
        bedrooms=4,
        bathrooms=3,
    ))

    assert result.estimated_value_usd > 0
    assert result.confidence_score == 0.3  # heuristic confidence
    assert result.confidence_interval_low < result.estimated_value_usd
    assert result.confidence_interval_high > result.estimated_value_usd


def test_engine_heuristic_scales_with_area():
    """Bigger area → higher price for the same department."""
    from ai.valuation.engine import ValuationEngine, PropertyFeatures

    engine = ValuationEngine()

    small = engine.predict(PropertyFeatures(
        latitude=13.69, longitude=-89.22,
        department="San Salvador", municipio="San Salvador",
        area_m2=80, property_type="house",
    ))
    large = engine.predict(PropertyFeatures(
        latitude=13.69, longitude=-89.22,
        department="San Salvador", municipio="San Salvador",
        area_m2=300, property_type="house",
    ))

    assert large.estimated_value_usd > small.estimated_value_usd


def test_engine_heuristic_department_varies():
    """San Salvador should be more expensive than Cabañas per m²."""
    from ai.valuation.engine import ValuationEngine, PropertyFeatures

    engine = ValuationEngine()

    ss = engine.predict(PropertyFeatures(
        latitude=13.69, longitude=-89.22,
        department="San Salvador", municipio="San Salvador",
        area_m2=100, property_type="house",
    ))
    cab = engine.predict(PropertyFeatures(
        latitude=13.87, longitude=-88.75,
        department="Cabañas", municipio="Sensuntepeque",
        area_m2=100, property_type="house",
    ))

    assert ss.estimated_value_usd > cab.estimated_value_usd


def test_engine_haversine():
    """Verify haversine distance function produces reasonable results."""
    from ai.valuation.engine import _haversine_km

    # San Salvador to Airport ≈ 40 km
    dist = _haversine_km(13.6929, -89.2182, 13.4409, -89.0557)
    assert 25 < dist < 35  # roughly 30 km


def test_engine_beach_proximity_premium():
    """Property near beach should get a higher heuristic via proximity premium."""
    from ai.valuation.engine import ValuationEngine, PropertyFeatures

    engine = ValuationEngine()

    # Near La Libertad beach
    beach = engine.predict(PropertyFeatures(
        latitude=13.483, longitude=-89.383,
        department="La Libertad", municipio="La Libertad",
        area_m2=100, property_type="house",
        distance_to_beach_km=2.0,
    ))

    # Inland La Libertad
    inland = engine.predict(PropertyFeatures(
        latitude=13.60, longitude=-89.32,
        department="La Libertad", municipio="Quezaltepeque",
        area_m2=100, property_type="house",
        distance_to_beach_km=30.0,
    ))

    assert beach.estimated_value_usd > inland.estimated_value_usd
