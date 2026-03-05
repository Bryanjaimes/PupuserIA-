"""
Property endpoints — listings, search, AI valuations.
Queries live PostgreSQL + PostGIS database.
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Property
from app.api.endpoints import scraped_data

router = APIRouter()
logger = logging.getLogger(__name__)


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
    bathrooms: float | None = None
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
    verification_status: str | None = None
    is_verified: bool | None = None
    submitted_by_name: str | None = None
    submitted_by_contact: str | None = None
    submitted_at: str | None = None
    verified_by: str | None = None
    verified_at: str | None = None
    verification_notes: str | None = None


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


def _scraped_to_summary(record: dict) -> PropertySummary:
    return PropertySummary(
        id=str(record.get("id") or ""),
        title=record.get("title") or "",
        title_es=record.get("title") or "",
        department=record.get("department") or "",
        municipio=record.get("municipio") or "",
        price_usd=record.get("price_usd"),
        ai_valuation_usd=None,
        bedrooms=record.get("bedrooms"),
        bathrooms=record.get("bathrooms"),
        area_m2=record.get("area_m2"),
        lot_size_m2=record.get("lot_size_m2"),
        property_type=(record.get("property_type") or "unknown"),
        latitude=record.get("latitude") or 0.0,
        longitude=record.get("longitude") or 0.0,
        thumbnail_url=None,
        images=[],
        is_featured=(record.get("quality_tier") or "").lower() == "gold",
        neighborhood_score=record.get("completeness_score"),
        features=record.get("features") or [],
    )


def _scraped_to_detail(record: dict) -> PropertyDetail:
    summary = _scraped_to_summary(record)
    return PropertyDetail(
        **summary.model_dump(),
        description=record.get("description"),
        description_es=record.get("description_es") or record.get("description"),
        ai_confidence=None,
        rental_yield_estimate=None,
        appreciation_5yr_estimate=None,
        listing_url=None,
        source=record.get("source"),
        verification_status=record.get("verification_status"),
        is_verified=record.get("is_verified"),
        submitted_by_name=record.get("submitted_by_name"),
        submitted_by_contact=record.get("submitted_by_contact"),
        submitted_at=record.get("submitted_at"),
        verified_by=record.get("verified_by"),
        verified_at=record.get("verified_at"),
        verification_notes=record.get("verification_notes"),
    )


def _fallback_search(
    department: str | None,
    municipio: str | None,
    min_price: float | None,
    max_price: float | None,
    property_type: str | None,
    bedrooms: int | None,
    featured_only: bool,
    sort_by: str,
    page: int,
    page_size: int,
) -> PropertySearchResponse:
    records = scraped_data._load_all_records()

    if department:
        records = [r for r in records if (r.get("department") or "").lower() == department.lower()]
    if municipio:
        records = [r for r in records if (r.get("municipio") or "").lower() == municipio.lower()]
    if min_price is not None:
        records = [r for r in records if (r.get("price_usd") or 0) >= min_price]
    if max_price is not None:
        records = [r for r in records if (r.get("price_usd") or float("inf")) <= max_price]
    if property_type:
        records = [r for r in records if (r.get("property_type") or "").lower() == property_type.lower()]
    if bedrooms is not None:
        records = [r for r in records if (r.get("bedrooms") or 0) >= bedrooms]
    if featured_only:
        records = [r for r in records if (r.get("quality_tier") or "").lower() == "gold"]

    if sort_by == "price_asc":
        records.sort(key=lambda r: (r.get("price_usd") is None, r.get("price_usd") or 0))
    elif sort_by == "price_desc":
        records.sort(key=lambda r: (r.get("price_usd") is None, -(r.get("price_usd") or 0)))
    elif sort_by == "score":
        records.sort(key=lambda r: (r.get("completeness_score") or 0), reverse=True)

    total = len(records)
    start = (page - 1) * page_size
    page_records = records[start:start + page_size]

    return PropertySearchResponse(
        results=[_scraped_to_summary(r) for r in page_records],
        total=total,
        page=page,
        page_size=page_size,
    )


def _fallback_stats() -> PropertyStats:
    records = scraped_data._load_all_records()
    prices = [r.get("price_usd") for r in records if isinstance(r.get("price_usd"), (int, float)) and (r.get("price_usd") or 0) > 0]
    by_type: dict[str, int] = {}
    departments: set[str] = set()
    featured_count = 0

    for r in records:
        ptype = r.get("property_type") or "unknown"
        by_type[ptype] = by_type.get(ptype, 0) + 1
        if r.get("department"):
            departments.add(str(r.get("department")))
        if (r.get("quality_tier") or "").lower() == "gold":
            featured_count += 1

    return PropertyStats(
        total_listings=len(records),
        avg_price_usd=round(sum(prices) / len(prices), 2) if prices else None,
        min_price_usd=min(prices) if prices else None,
        max_price_usd=max(prices) if prices else None,
        departments_covered=len(departments),
        featured_count=featured_count,
        by_type=by_type,
    )


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
    try:
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
    except Exception:
        logger.warning("Database unavailable for property stats; using JSONL fallback", exc_info=True)
        return _fallback_stats()


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
    try:
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

        count_q = select(func.count(Property.id)).where(where)
        total = (await db.execute(count_q)).scalar() or 0

        order = Property.created_at.desc()
        if sort_by == "price_asc":
            order = Property.price_usd.asc().nullslast()
        elif sort_by == "price_desc":
            order = Property.price_usd.desc().nullsfirst()
        elif sort_by == "score":
            order = Property.neighborhood_score.desc().nullslast()

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
    except Exception:
        logger.warning("Database unavailable for property search; using JSONL fallback", exc_info=True)
        return _fallback_search(
            department=department,
            municipio=municipio,
            min_price=min_price,
            max_price=max_price,
            property_type=property_type,
            bedrooms=bedrooms,
            featured_only=featured_only,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
        )


@router.get("/featured", response_model=list[PropertySummary])
async def featured_properties(
    limit: int = Query(default=8, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[PropertySummary]:
    """Get featured property listings."""
    try:
        query = (
            select(Property)
            .where(and_(Property.is_active == True, Property.is_featured == True))  # noqa: E712
            .order_by(Property.neighborhood_score.desc().nullslast())
            .limit(limit)
        )
        result = await db.execute(query)
        return [_row_to_summary(p) for p in result.scalars().all()]
    except Exception:
        logger.warning("Database unavailable for featured properties; using JSONL fallback", exc_info=True)
        records = [r for r in scraped_data._load_all_records() if (r.get("quality_tier") or "").lower() == "gold"]
        records.sort(key=lambda r: (r.get("completeness_score") or 0), reverse=True)
        return [_scraped_to_summary(r) for r in records[:limit]]


@router.get("/{property_id}", response_model=PropertyDetail)
async def get_property(
    property_id: str,
    db: AsyncSession = Depends(get_db),
) -> PropertyDetail:
    """Get full property details with AI valuation."""
    try:
        pid = UUID(property_id)
    except ValueError:
        records = scraped_data._load_all_records()
        for record in records:
            if str(record.get("id")) == property_id:
                return _scraped_to_detail(record)
        raise HTTPException(status_code=404, detail="Property not found")

    try:
        result = await db.execute(
            select(Property).where(Property.id == pid)
        )
        prop = result.scalar_one_or_none()
        if prop:
            return _row_to_detail(prop)
    except Exception:
        logger.warning("Database unavailable for get_property; using JSONL fallback", exc_info=True)

    records = scraped_data._load_all_records()
    for record in records:
        if str(record.get("id")) == property_id:
            return _scraped_to_detail(record)

    raise HTTPException(status_code=404, detail="Property not found")


@router.get("/sources")
async def list_property_sources():
    """List JSONL source files currently available in fallback storage."""
    return await scraped_data.list_source_files()


@router.post(
    "/submit",
    response_model=scraped_data.CrowdListingCreateResponse,
    status_code=201,
)
async def submit_crowd_listing(payload: scraped_data.CrowdListingCreate):
    """Submit a crowd-sourced listing (always uses JSONL crowd storage)."""
    return await scraped_data.submit_crowd_listing(payload)


@router.post("/{property_id}/verify", response_model=scraped_data.ScrapedPropertyOut)
async def verify_crowd_listing(
    property_id: str,
    payload: scraped_data.VerifyListingRequest,
    x_broker_token: str | None = Header(default=None),
):
    """Broker-verifies a crowd listing stored in JSONL fallback layer."""
    return await scraped_data.verify_crowd_listing(
        property_id=property_id,
        payload=payload,
        x_broker_token=x_broker_token,
    )


@router.post("/{property_id}/valuation")
async def request_valuation(property_id: str) -> dict:
    """Trigger an AI valuation for a specific property."""
    # TODO: Queue AI valuation job
    return {"status": "queued", "property_id": property_id}
