"""
Basic API tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.endpoints import scraped_data


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_health(client: AsyncClient):
    response = await client.get("/api/v1/health/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_properties_search(client: AsyncClient):
    response = await client.get("/api/v1/properties/")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_crowd_listing_submit_unverified(client: AsyncClient, tmp_path):
    scraped_data._CROWD_FILE = tmp_path / "crowd_test.jsonl"
    scraped_data._BROKER_VERIFY_TOKEN = "test-broker-token"

    payload = {
        "title": "Casa cerca del centro en Santa Ana",
        "description": "Propiedad familiar con patio",
        "price_usd": 85000,
        "property_type": "house",
        "bedrooms": 3,
        "bathrooms": 2,
        "area_m2": 120,
        "department": "Santa Ana",
        "municipio": "Santa Ana",
        "address": "Colonia Centro",
        "latitude": 13.994,
        "longitude": -89.559,
        "submitted_by_name": "Ana López",
        "submitted_by_contact": "+50370000000",
    }
    response = await client.post("/api/v1/properties/submit", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()

    assert data["id"].startswith("USR-")
    assert data["verification_status"] == "unverified"

    detail = await client.get(f"/api/v1/properties/{data['id']}")
    assert detail.status_code == 200
    listing = detail.json()
    assert listing["verification_status"] == "unverified"
    assert listing["is_verified"] is False


@pytest.mark.asyncio
async def test_broker_can_verify_crowd_listing(client: AsyncClient, tmp_path):
    scraped_data._CROWD_FILE = tmp_path / "crowd_test_verify.jsonl"
    scraped_data._BROKER_VERIFY_TOKEN = "test-broker-token"

    submit_payload = {
        "title": "Terreno en Sonsonate",
        "property_type": "land",
        "department": "Sonsonate",
        "municipio": "Sonsonate",
        "submitted_by_name": "Carlos Pérez",
    }
    submit_response = await client.post("/api/v1/properties/submit", json=submit_payload)
    assert submit_response.status_code == 201, submit_response.text
    listing_id = submit_response.json()["id"]

    verify_response = await client.post(
        f"/api/v1/properties/{listing_id}/verify",
        json={"broker_name": "Broker Marta", "notes": "Visited site and confirmed details."},
        headers={"x-broker-token": "test-broker-token"},
    )
    assert verify_response.status_code == 200, verify_response.text
    verified = verify_response.json()
    assert verified["verification_status"] == "verified"
    assert verified["is_verified"] is True
    assert verified["verified_by"] == "Broker Marta"


@pytest.mark.asyncio
async def test_broker_verify_requires_token(client: AsyncClient, tmp_path):
    scraped_data._CROWD_FILE = tmp_path / "crowd_test_unauth.jsonl"
    scraped_data._BROKER_VERIFY_TOKEN = "test-broker-token"

    submit_response = await client.post(
        "/api/v1/properties/submit",
        json={
            "title": "Casa para verificacion",
            "property_type": "house",
            "department": "San Salvador",
            "municipio": "San Salvador",
            "submitted_by_name": "Luis",
        },
    )
    assert submit_response.status_code == 201, submit_response.text
    listing_id = submit_response.json()["id"]

    unauthorized = await client.post(
        f"/api/v1/properties/{listing_id}/verify",
        json={"broker_name": "Broker X"},
    )
    assert unauthorized.status_code == 401


@pytest.mark.asyncio
async def test_tours_search(client: AsyncClient):
    response = await client.get("/api/v1/tours/")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


@pytest.mark.asyncio
async def test_concierge_chat(client: AsyncClient):
    response = await client.post(
        "/api/v1/concierge/chat",
        json={"message": "Hello!", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data


@pytest.mark.asyncio
async def test_foundation_impact(client: AsyncClient):
    response = await client.get("/api/v1/foundation/impact")
    assert response.status_code == 200
    data = response.json()
    assert "students_tutored" in data
