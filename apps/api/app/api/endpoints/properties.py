"""
Property endpoints — listings, search, AI valuations.
Queries live PostgreSQL + PostGIS database.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Property

router = APIRouter()


# ── Schemas ──────────────────────────────────────────


class PropertySummary(BaseModel):
    """Summary of a property listing."""

    id: str
    title: str
    title_es: str
    department: str
    municipio: str
    price_usd: float | None = None
    ai_valuation_usd: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_m2: float | None = None
    lot_size_m2: float | None = None
    property_type: str
    latitude: float
    longitude: float
    thumbnail_url: str | None = None
    images: list[str] = []
    is_featured: bool = False
    neighborhood_score: float | None = None
    features: list[str] = []


class PropertyDetail(PropertySummary):
    """Full property detail with AI analysis."""

    description: str | None = None
    description_es: str | None = None
    ai_confidence: float | None = None
    rental_yield_estimate: float | None = None
    appreciation_5yr_estimate: float | None = None
    listing_url: str | None = None
    source: str | None = None


class PropertySearchResponse(BaseModel):
    """Paginated property search results."""

    results: list[PropertySummary]
    total: int
    page: int
    page_size: int


class PropertyStats(BaseModel):
    """Quick stats about the property database."""

    total_listings: int
    avg_price_usd: float | None
    min_price_usd: float | None
    max_price_usd: float | None
    departments_covered: int
    featured_count: int
    by_type: dict[str, int]


# ── Helpers ──────────────────────────────────────────


def _row_to_summary(p: Property) -> PropertySummary:
    images = p.images or []
    return PropertySummary(
        id=str(p.id),
        title=p.title,
        title_es=p.title_es,
        department=p.department,
        municipio=p.municipio,
        price_usd=p.price_usd,
        ai_valuation_usd=p.ai_valuation_usd,
        bedrooms=p.bedrooms,
        bathrooms=p.bathrooms,
        area_m2=p.area_m2,
        lot_size_m2=p.lot_size_m2,
        property_type=p.property_type,
        latitude=p.latitude,
        longitude=p.longitude,
        thumbnail_url=images[0] if images else None,
        images=images,
        is_featured=p.is_featured or False,
        neighborhood_score=p.neighborhood_score,
        features=p.features or [],
    )


def _row_to_detail(p: Property) -> PropertyDetail:
    images = p.images or []
    return PropertyDetail(
        id=str(p.id),
        title=p.title,
        title_es=p.title_es,
        department=p.department,
        municipio=p.municipio,
        price_usd=p.price_usd,
        ai_valuation_usd=p.ai_valuation_usd,
        bedrooms=p.bedrooms,
        bathrooms=p.bathrooms,
        area_m2=p.area_m2,
        lot_size_m2=p.lot_size_m2,
        property_type=p.property_type,
        latitude=p.latitude,
        longitude=p.longitude,
        thumbnail_url=images[0] if images else None,
        images=images,
        is_featured=p.is_featured or False,
        neighborhood_score=p.neighborhood_score,
        features=p.features or [],
        description=p.description,
        description_es=p.description_es,
        ai_confidence=p.ai_valuation_confidence,
        rental_yield_estimate=p.rental_yield_estimate,
        appreciation_5yr_estimate=p.appreciation_5yr_estimate,
        listing_url=p.listing_url,
        source=p.source,
    )


# ── Endpoints ────────────────────────────────────────


@router.get("/stats", response_model=PropertyStats)
async def property_stats(db: AsyncSession = Depends(get_db)) -> PropertyStats:
    """Get quick stats about the property database."""
    result = await db.execute(
        select(
            func.count(Property.id).label("total"),
            func.avg(Property.price_usd).label("avg_price"),
            func.min(Property.price_usd).label("min_price"),
            func.max(Property.price_usd).label("max_price"),
            func.count(func.distinct(Property.department)).label("depts"),
            func.count(case((Property.is_featured == True, 1))).label("featured"),  # noqa: E712
        ).where(Property.is_active == True)  # noqa: E712
    )
    row = result.one()

    # Count by type
    type_result = await db.execute(
        select(Property.property_type, func.count(Property.id))
        .where(Property.is_active == True)  # noqa: E712
        .group_by(Property.property_type)
    )
    by_type = {r[0]: r[1] for r in type_result.all()}

    return PropertyStats(
        total_listings=row.total,
        avg_price_usd=round(row.avg_price, 2) if row.avg_price else None,
        min_price_usd=row.min_price,
        max_price_usd=row.max_price,
        departments_covered=row.depts,
        featured_count=row.featured,
        by_type=by_type,
    )


@router.get("/", response_model=PropertySearchResponse)
async def search_properties(
    department: str | None = None,
    municipio: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    property_type: str | None = None,
    bedrooms: int | None = None,
    featured_only: bool = False,
    sort_by: str = Query(default="newest", pattern="^(newest|price_asc|price_desc|score)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PropertySearchResponse:
    """Search property listings with filters."""
    conditions = [Property.is_active == True]  # noqa: E712

    if department:
        conditions.append(func.lower(Property.department) == department.lower())
    if municipio:
        conditions.append(func.lower(Property.municipio) == municipio.lower())
    if min_price is not None:
        conditions.append(Property.price_usd >= min_price)
    if max_price is not None:
        conditions.append(Property.price_usd <= max_price)
    if property_type:
        conditions.append(Property.property_type == property_type)
    if bedrooms is not None:
        conditions.append(Property.bedrooms >= bedrooms)
    if featured_only:
        conditions.append(Property.is_featured == True)  # noqa: E712

    where = and_(*conditions)

    # Count
    count_q = select(func.count(Property.id)).where(where)
    total = (await db.execute(count_q)).scalar() or 0

    # Sort
    order = Property.created_at.desc()
    if sort_by == "price_asc":
        order = Property.price_usd.asc().nullslast()
    elif sort_by == "price_desc":
        order = Property.price_usd.desc().nullsfirst()
    elif sort_by == "score":
        order = Property.neighborhood_score.desc().nullslast()

    # Fetch
    query = (
        select(Property)
        .where(where)
        .order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    properties = result.scalars().all()

    return PropertySearchResponse(
        results=[_row_to_summary(p) for p in properties],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/featured", response_model=list[PropertySummary])
async def featured_properties(
    limit: int = Query(default=8, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[PropertySummary]:
    """Get featured property listings."""
    query = (
        select(Property)
        .where(and_(Property.is_active == True, Property.is_featured == True))  # noqa: E712
        .order_by(Property.neighborhood_score.desc().nullslast())
        .limit(limit)
    )
    result = await db.execute(query)
    return [_row_to_summary(p) for p in result.scalars().all()]


@router.get("/{property_id}", response_model=PropertyDetail)
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
) -> PropertyDetail:
    """Get full property details with AI valuation."""
    try:
        pid = UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    result = await db.execute(
        select(Property).where(Property.id == pid)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    return _row_to_detail(prop)


@router.post("/{property_id}/valuation")
async def request_valuation(property_id: str) -> dict:
    """Trigger an AI valuation for a specific property."""
    # TODO: Queue AI valuation job
    return {"status": "queued", "property_id": property_id}
