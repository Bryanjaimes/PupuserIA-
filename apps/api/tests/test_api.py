"""
Basic API tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


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
