"""
Analytics endpoints — event tracking + dashboard metrics.

Privacy-first: no PII stored, sessions are anonymous UUIDs,
IP-based geo is coarse (country/region only).
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter()


# ── Request / Response Models ────────────────────────


class TrackEventRequest(BaseModel):
    """A single analytics event to record."""

    session_id: str = Field(..., max_length=64)
    event_type: str = Field(..., max_length=50)
    page_path: Optional[str] = None
    referrer: Optional[str] = None
    properties: dict = Field(default_factory=dict)
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    language: Optional[str] = None


class TrackBatchRequest(BaseModel):
    """Batch of events (reduces HTTP overhead)."""

    events: list[TrackEventRequest] = Field(..., max_items=50)


class PlatformOverview(BaseModel):
    """High-level platform metrics for the dashboard."""

    # Real-time (today)
    active_visitors_now: int = 0
    page_views_today: int = 0
    sessions_today: int = 0

    # Trailing periods
    visitors_7d: int = 0
    visitors_30d: int = 0
    page_views_7d: int = 0
    page_views_30d: int = 0

    # Engagement
    property_views_7d: int = 0
    property_searches_7d: int = 0
    tour_views_7d: int = 0
    concierge_chats_7d: int = 0
    map_interactions_7d: int = 0
    avg_session_duration_sec: float = 0

    # Content
    total_listings: int = 0
    listings_with_valuation: int = 0
    departments_covered: int = 0

    # Geographic breakdown
    top_countries: dict = Field(default_factory=dict)
    top_departments: dict = Field(default_factory=dict)

    # Trends (daily counts for last 30 days)
    daily_visitors: list[dict] = Field(default_factory=list)
    daily_page_views: list[dict] = Field(default_factory=list)


class ImpactDashboard(BaseModel):
    """Foundation impact metrics for the transparency dashboard."""

    # Revenue & allocation
    total_platform_revenue_usd: float = 0
    foundation_allocation_usd: float = 0
    allocation_rate: float = 17.5  # percentage

    # Human impact
    students_reached: int = 0
    meals_served: int = 0
    devices_deployed: int = 0
    schools_active: int = 0
    solar_installations: int = 0
    supply_kits: int = 0
    children_per_dollar: float = 0  # efficiency metric

    # Per-program breakdown
    program_breakdown: list[dict] = Field(default_factory=list)

    # Transparency
    blockchain_verified_count: int = 0
    fund_efficiency_pct: float = 92.0  # % reaching children directly

    # Trend (monthly impact growth)
    monthly_impact: list[dict] = Field(default_factory=list)

    # Geographic distribution
    impact_by_department: dict = Field(default_factory=dict)


class DailyMetric(BaseModel):
    """Single day of metrics for timeline charts."""

    date: str
    unique_visitors: int = 0
    page_views: int = 0
    property_views: int = 0
    sessions: int = 0


# ── Endpoints ────────────────────────────────────────


@router.post("/track", status_code=202)
async def track_event(event: TrackEventRequest) -> dict:
    """
    Record a single analytics event.
    Returns 202 Accepted — fire-and-forget from the client.
    """
    # TODO: Write to database (or queue for batch insert)
    # For now, accept and acknowledge
    return {"status": "accepted"}


@router.post("/track/batch", status_code=202)
async def track_batch(batch: TrackBatchRequest) -> dict:
    """
    Record a batch of analytics events.
    Client buffers events and flushes periodically.
    """
    # TODO: Batch insert to database
    return {"status": "accepted", "count": len(batch.events)}


@router.get("/overview", response_model=PlatformOverview)
async def get_platform_overview() -> PlatformOverview:
    """
    Get platform-wide analytics overview.
    Used by the admin/impact dashboard.
    """
    # TODO: Aggregate from analytics_events + daily_metrics tables
    # For now, return realistic seed data so the dashboard renders
    today = datetime.utcnow().date()
    daily = []
    for i in range(30, 0, -1):
        d = today - timedelta(days=i)
        # Simulated growth curve
        base = max(5, int(10 + i * 0.5))
        daily.append({
            "date": d.isoformat(),
            "visitors": base + (i % 7) * 3,
            "page_views": base * 3 + (i % 5) * 8,
        })

    return PlatformOverview(
        active_visitors_now=0,
        page_views_today=0,
        sessions_today=0,
        visitors_7d=0,
        visitors_30d=0,
        page_views_7d=0,
        page_views_30d=0,
        property_views_7d=0,
        property_searches_7d=0,
        tour_views_7d=0,
        concierge_chats_7d=0,
        map_interactions_7d=0,
        avg_session_duration_sec=0,
        total_listings=2524,  # From E24 scrape
        listings_with_valuation=0,
        departments_covered=14,
        top_countries={},
        top_departments={},
        daily_visitors=[{"date": d["date"], "value": d["visitors"]} for d in daily],
        daily_page_views=[{"date": d["date"], "value": d["page_views"]} for d in daily],
    )


@router.get("/impact", response_model=ImpactDashboard)
async def get_impact_dashboard() -> ImpactDashboard:
    """
    Get Foundation impact dashboard data.
    Combines platform revenue tracking with foundation allocation.
    """
    # TODO: Aggregate from impact_transactions + schools tables
    programs = [
        {"program": "AI Tutoring", "emoji": "🤖", "allocated_usd": 0, "students": 0},
        {"program": "Nutrition", "emoji": "🍽️", "allocated_usd": 0, "meals": 0},
        {"program": "Devices", "emoji": "💻", "allocated_usd": 0, "deployed": 0},
        {"program": "Solar Energy", "emoji": "☀️", "allocated_usd": 0, "installations": 0},
        {"program": "Supplies", "emoji": "📚", "allocated_usd": 0, "kits": 0},
    ]

    return ImpactDashboard(
        total_platform_revenue_usd=0,
        foundation_allocation_usd=0,
        allocation_rate=17.5,
        students_reached=0,
        meals_served=0,
        devices_deployed=0,
        schools_active=0,
        solar_installations=0,
        supply_kits=0,
        children_per_dollar=0,
        program_breakdown=programs,
        blockchain_verified_count=0,
        fund_efficiency_pct=92.0,
        monthly_impact=[],
        impact_by_department={},
    )


@router.get("/daily", response_model=list[DailyMetric])
async def get_daily_metrics(
    days: int = Query(default=30, ge=1, le=365),
) -> list[DailyMetric]:
    """Get daily metrics for the last N days."""
    # TODO: Query daily_metrics table
    today = datetime.utcnow().date()
    return [
        DailyMetric(
            date=(today - timedelta(days=i)).isoformat(),
            unique_visitors=0,
            page_views=0,
            property_views=0,
            sessions=0,
        )
        for i in range(days, 0, -1)
    ]
