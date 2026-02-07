"""
API Router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.endpoints import health, properties, tours, concierge, content, foundation

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])
api_router.include_router(tours.router, prefix="/tours", tags=["Tours & Experiences"])
api_router.include_router(concierge.router, prefix="/concierge", tags=["AI Concierge"])
api_router.include_router(content.router, prefix="/content", tags=["Content & SEO"])
api_router.include_router(foundation.router, prefix="/foundation", tags=["Foundation Impact"])
