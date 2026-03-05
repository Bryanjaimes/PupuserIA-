"""
API Router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.endpoints import (
    health, tours, concierge, content,
    foundation, coverage, analytics, valuation, us_valuation,
    scraped_data, properties,
)

# ── El Salvador API ──────────────────────────────────
api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])
api_router.include_router(scraped_data.router, prefix="/properties/raw", tags=["Properties (Raw Scraped)"])
api_router.include_router(tours.router, prefix="/tours", tags=["Tours & Experiences"])
api_router.include_router(concierge.router, prefix="/concierge", tags=["AI Concierge"])
api_router.include_router(content.router, prefix="/content", tags=["Content & SEO"])
api_router.include_router(foundation.router, prefix="/foundation", tags=["Foundation Impact"])
api_router.include_router(coverage.router, prefix="/coverage", tags=["Data Coverage & Gaps"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Metrics"])
api_router.include_router(valuation.router, prefix="/valuation", tags=["AI Valuation"])

# ── US Real Estate API ───────────────────────────────
us_router = APIRouter()

us_router.include_router(health.router, prefix="/health", tags=["Health"])
us_router.include_router(scraped_data.router, prefix="/properties", tags=["Properties"])
us_router.include_router(us_valuation.router, prefix="/valuation", tags=["US Valuation"])
