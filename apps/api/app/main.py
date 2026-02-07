"""
Gateway El Salvador — FastAPI Application
==========================================
The core API powering the platform: AI concierge, property valuations,
bookings, user management, and Foundation impact tracking.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    # ── Startup ──
    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Load AI models / warm caches
    print("🇸🇻 Gateway El Salvador API starting...")
    yield
    # ── Shutdown ──
    # TODO: Close database connections
    # TODO: Close Redis connections
    print("🇸🇻 Gateway El Salvador API shutting down...")


app = FastAPI(
    title="Gateway El Salvador API",
    description="AI-powered platform API for tourism, real estate, and education in El Salvador.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "gateway-es-api"}
