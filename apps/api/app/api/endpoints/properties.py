"""
Property endpoints — listings, search, AI valuations.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class PropertySummary(BaseModel):
    """Summary of a property listing."""

    id: str
    title: str
    title_es: str
    department: str
    municipio: str
    price_usd: float | None
    ai_valuation_usd: float | None
    bedrooms: int | None
    bathrooms: int | None
    area_m2: float | None
    property_type: str
    latitude: float
    longitude: float
    thumbnail_url: str | None


class PropertyDetail(PropertySummary):
    """Full property detail with AI analysis."""

    description: str
    description_es: str
    ai_confidence: float | None
    rental_yield_estimate: float | None
    appreciation_5yr_estimate: float | None
    neighborhood_score: float | None
    images: list[str]
    features: list[str]


class PropertySearchResponse(BaseModel):
    """Paginated property search results."""

    results: list[PropertySummary]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=PropertySearchResponse)
async def search_properties(
    department: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    property_type: str | None = None,
    bedrooms: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PropertySearchResponse:
    """Search property listings with filters."""
    # TODO: Implement PostGIS-powered geospatial search
    return PropertySearchResponse(results=[], total=0, page=page, page_size=page_size)


@router.get("/{property_id}", response_model=PropertyDetail)
async def get_property(property_id: str) -> PropertyDetail:
    """Get full property details with AI valuation."""
    # TODO: Fetch from database + run AI valuation
    raise NotImplementedError("Property detail endpoint not yet implemented")


@router.post("/{property_id}/valuation")
async def request_valuation(property_id: str) -> dict:
    """Trigger an AI valuation for a specific property."""
    # TODO: Queue AI valuation job
    return {"status": "queued", "property_id": property_id}
