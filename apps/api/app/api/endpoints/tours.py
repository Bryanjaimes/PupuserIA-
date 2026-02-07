"""
Tour & Experience endpoints — booking, listing, search.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class TourSummary(BaseModel):
    """Summary of a bookable tour or experience."""

    id: str
    title: str
    title_es: str
    description: str
    department: str
    category: str  # surf, volcano, coffee, culture, food, adventure
    price_usd: float
    duration_hours: float
    rating: float | None
    review_count: int
    thumbnail_url: str | None
    available: bool


class TourSearchResponse(BaseModel):
    """Paginated tour search results."""

    results: list[TourSummary]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=TourSearchResponse)
async def search_tours(
    department: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> TourSearchResponse:
    """Search available tours and experiences."""
    # TODO: Query database with filters
    return TourSearchResponse(results=[], total=0, page=page, page_size=page_size)


@router.post("/{tour_id}/book")
async def book_tour(tour_id: str) -> dict:
    """Book a tour — creates a Stripe checkout session."""
    # TODO: Create Stripe checkout session, record booking
    return {"status": "booking_created", "tour_id": tour_id}
