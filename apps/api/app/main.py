"""
Gateway El Salvador — FastAPI Application
==========================================
The core API powering the platform: AI concierge, property valuations,
bookings, user management, and Foundation impact tracking.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router, us_router


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


# ── Main app (El Salvador) ────────────────────────────
app = FastAPI(
    title="Gateway El Salvador API",
    description=(
        "AI-powered platform API for tourism, real estate, and education in El Salvador.\n\n"
        "**[Switch to US Real Estate API →](/api/us/docs)**"
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── US Real Estate sub-app ───────────────────────────
us_app = FastAPI(
    title="US Real Estate API",
    description=(
        "AI-powered property valuation for the US market — "
        "Zestimate-style pricing across all 50 states + DC.\n\n"
        "**[Switch to El Salvador API →](/api/docs)**"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)
us_app.include_router(us_router)

# ── CORS (both apps) ──
for _app in (app, us_app):
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ── Mount US sub-app under /api/us ───────────────────
app.mount("/api/us", us_app)

# ── El Salvador routes ──
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing():
    """Landing page with links to both API docs."""
    return """<!DOCTYPE html><html><head><title>PupuserIA API</title>
<style>body{font-family:system-ui;max-width:500px;margin:80px auto;text-align:center}
a{display:block;margin:20px;padding:20px;border:2px solid #333;border-radius:12px;
text-decoration:none;color:#333;font-size:1.2em}a:hover{background:#f0f0f0}</style>
</head><body>
<h1>PupuserIA API</h1>
<a href="/api/docs">🇸🇻 El Salvador API Docs</a>
<a href="/api/us/docs">🇺🇸 US Real Estate API Docs</a>
</body></html>"""


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "gateway-es-api"}
