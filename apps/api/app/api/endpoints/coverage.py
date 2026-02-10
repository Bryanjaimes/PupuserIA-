"""
Coverage Gap endpoints — data gap analysis and field research management.

Provides insights into which municipios lack property data, imagery,
pricing info, etc., and tracks boots-on-the-ground research efforts.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import DataCoverageGap, Department, Municipio

router = APIRouter()


# ── Pydantic Schemas ─────────────────────────────────


class CoverageGapOut(BaseModel):
    """A single coverage gap record."""

    id: UUID
    municipio_id: int
    municipio_name: str
    department_name: str
    category: str
    coverage_score: float
    total_listings: int
    listings_with_price: int
    listings_with_images: int
    listings_with_coordinates: int
    avg_images_per_listing: float
    priority: str
    needs_field_research: bool
    field_research_status: str
    field_researcher: str | None
    field_research_notes: str | None
    field_research_date: datetime | None
    last_analyzed: datetime | None

    class Config:
        from_attributes = True


class CoverageGapUpdate(BaseModel):
    """Payload for updating a coverage gap record."""

    coverage_score: float | None = Field(None, ge=0.0, le=1.0)
    total_listings: int | None = Field(None, ge=0)
    listings_with_price: int | None = Field(None, ge=0)
    listings_with_images: int | None = Field(None, ge=0)
    listings_with_coordinates: int | None = Field(None, ge=0)
    avg_images_per_listing: float | None = Field(None, ge=0.0)
    priority: str | None = None
    needs_field_research: bool | None = None
    field_research_status: str | None = None
    field_researcher: str | None = None
    field_research_notes: str | None = None


class DepartmentCoverageSummary(BaseModel):
    """Aggregated coverage info for a department."""

    department_id: int
    department_name: str
    total_municipios: int
    population: int | None
    area_km2: float | None
    avg_coverage_score: float
    critical_gaps: int
    high_gaps: int
    medium_gaps: int
    low_gaps: int
    municipios_needing_research: int
    categories_covered: dict[str, float]  # category → avg score


class MunicipioCoverageDetail(BaseModel):
    """Full coverage detail for a single municipio."""

    municipio_id: int
    municipio_name: str
    department_name: str
    population: int | None
    area_km2: float | None
    elevation_m: int | None
    centroid_lat: float | None
    centroid_lng: float | None
    gaps: list[CoverageGapOut]
    overall_score: float
    worst_category: str | None
    best_category: str | None


class CoverageGapListResponse(BaseModel):
    """Paginated list of coverage gaps."""

    results: list[CoverageGapOut]
    total: int
    page: int
    page_size: int


class DataDesertZone(BaseModel):
    """A known data desert zone requiring field research."""

    zone_name: str
    department: str
    municipios: list[str]
    notes: str
    priority: str


class CoverageOverview(BaseModel):
    """High-level coverage overview for the whole country."""

    total_departments: int
    total_municipios: int
    total_gap_records: int
    avg_coverage_score: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    municipios_needing_research: int
    data_desert_zones: list[DataDesertZone]


# ── Known Data Desert Zones (static until we can auto-detect) ────

DATA_DESERT_ZONES: list[dict] = [
    {
        "zone_name": "Northern Morazán Mountains",
        "department": "Morazán",
        "municipios": [
            "Perquín", "Arambala", "Meanguera", "Joateca",
            "Torola", "San Fernando", "Jocoaitique",
        ],
        "notes": (
            "Remote mountainous terrain, Ruta de Paz area. Former conflict zone. "
            "Very few real estate listings or street imagery. "
            "NEEDS: local contacts, drone photography, community engagement."
        ),
        "priority": "critical",
    },
    {
        "zone_name": "Northern Chalatenango Border",
        "department": "Chalatenango",
        "municipios": [
            "Citalá", "San Ignacio", "La Palma", "San Fernando",
            "Dulce Nombre de María", "Arcatao", "Las Vueltas", "Las Flores",
        ],
        "notes": (
            "Rural highlands near Honduras border. Limited internet. "
            "Some ecotourism (La Palma artisan town). "
            "NEEDS: road condition surveys, property value baselines, local market interviews."
        ),
        "priority": "high",
    },
    {
        "zone_name": "Cabañas Interior",
        "department": "Cabañas",
        "municipios": [
            "Cinquera", "Victoria", "Dolores", "Guacotecti",
            "San Isidro", "Tejutepeque",
        ],
        "notes": (
            "Least-visited department. Former guerrilla territory. "
            "Cinquera forest reserve. Very few online listings. "
            "NEEDS: municipal office data, local broker contacts, environmental surveys."
        ),
        "priority": "critical",
    },
    {
        "zone_name": "La Unión Eastern Coast",
        "department": "La Unión",
        "municipios": [
            "Meanguera del Golfo", "Intipucá", "Conchagua",
            "Bolívar", "Nueva Esparta",
        ],
        "notes": (
            "Islands in Gulf of Fonseca (Meanguera del Golfo). Intipucá = remittance town. "
            "Conchagua volcano area. "
            "NEEDS: coastal property surveys, tourism asset inventory, port development data."
        ),
        "priority": "high",
    },
    {
        "zone_name": "Northern Usulután / San Miguel",
        "department": "San Miguel",
        "municipios": [
            "Carolina", "Nuevo Edén de San Juan", "San Luis de la Reina",
            "San Antonio", "Sesori",
        ],
        "notes": (
            "Remote eastern highlands. Very limited road access. Sparse population. "
            "Almost zero online real estate presence. "
            "NEEDS: community-level data, basic mapping, school inventories."
        ),
        "priority": "critical",
    },
    {
        "zone_name": "Sonsonate Indigenous Areas",
        "department": "Sonsonate",
        "municipios": [
            "Cuisnahuat", "Santa Isabel Ishuatán",
            "Santo Domingo de Guzmán", "Santa Catarina Masahuat",
        ],
        "notes": (
            "Indigenous Nahua-Pipil communities. Rich cultural heritage but limited digital presence. "
            "NEEDS: culturally sensitive documentation, community permissions, "
            "bilingual (Náhuat/Spanish) data collection."
        ),
        "priority": "high",
    },
]


# ── Endpoints ────────────────────────────────────────


@router.get("/overview", response_model=CoverageOverview)
async def get_coverage_overview(db: AsyncSession = Depends(get_db)) -> CoverageOverview:
    """
    Get a high-level overview of data coverage across all of El Salvador.
    Includes priority breakdown and known data desert zones.
    """
    # Aggregate stats
    stats = await db.execute(
        select(
            func.count(DataCoverageGap.id).label("total"),
            func.avg(DataCoverageGap.coverage_score).label("avg_score"),
            func.sum(case((DataCoverageGap.priority == "critical", 1), else_=0)).label("critical"),
            func.sum(case((DataCoverageGap.priority == "high", 1), else_=0)).label("high"),
            func.sum(case((DataCoverageGap.priority == "medium", 1), else_=0)).label("medium"),
            func.sum(case((DataCoverageGap.priority == "low", 1), else_=0)).label("low"),
            func.sum(case((DataCoverageGap.needs_field_research.is_(True), 1), else_=0)).label(
                "needs_research"
            ),
        )
    )
    row = stats.one()

    dept_count = await db.scalar(select(func.count(Department.id)))
    muni_count = await db.scalar(select(func.count(Municipio.id)))

    return CoverageOverview(
        total_departments=dept_count or 0,
        total_municipios=muni_count or 0,
        total_gap_records=row.total or 0,
        avg_coverage_score=round(float(row.avg_score or 0), 3),
        critical_count=row.critical or 0,
        high_count=row.high or 0,
        medium_count=row.medium or 0,
        low_count=row.low or 0,
        municipios_needing_research=row.needs_research or 0,
        data_desert_zones=[DataDesertZone(**z) for z in DATA_DESERT_ZONES],
    )


@router.get("/gaps", response_model=CoverageGapListResponse)
async def list_coverage_gaps(
    department: str | None = Query(None, description="Filter by department name"),
    category: str | None = Query(None, description="Filter by category"),
    priority: str | None = Query(None, description="Filter by priority (critical/high/medium/low)"),
    needs_research: bool | None = Query(None, description="Filter by needs_field_research"),
    max_score: float | None = Query(None, ge=0.0, le=1.0, description="Max coverage score"),
    sort_by: str = Query("priority", description="Sort by: priority, score, population"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> CoverageGapListResponse:
    """
    List coverage gaps with powerful filtering.
    Use to identify where data is missing and prioritize research.
    """
    base = (
        select(DataCoverageGap)
        .join(Municipio, DataCoverageGap.municipio_id == Municipio.id)
        .join(Department, Municipio.department_id == Department.id)
    )

    # Filters
    if department:
        base = base.where(Department.name == department)
    if category:
        base = base.where(DataCoverageGap.category == category)
    if priority:
        base = base.where(DataCoverageGap.priority == priority)
    if needs_research is not None:
        base = base.where(DataCoverageGap.needs_field_research == needs_research)
    if max_score is not None:
        base = base.where(DataCoverageGap.coverage_score <= max_score)

    # Count
    count_q = select(func.count()).select_from(base.subquery())
    total = await db.scalar(count_q) or 0

    # Sorting
    order_map = {
        "priority": case(
            (DataCoverageGap.priority == "critical", 0),
            (DataCoverageGap.priority == "high", 1),
            (DataCoverageGap.priority == "medium", 2),
            else_=3,
        ),
        "score": DataCoverageGap.coverage_score,
        "population": Municipio.population.desc(),
    }
    order = order_map.get(sort_by, order_map["priority"])
    query = base.order_by(order).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    gaps = result.scalars().all()

    # Build response (need to load municipio/department names)
    items: list[CoverageGapOut] = []
    for gap in gaps:
        muni = await db.get(Municipio, gap.municipio_id)
        dept = await db.get(Department, muni.department_id) if muni else None
        items.append(
            CoverageGapOut(
                id=gap.id,
                municipio_id=gap.municipio_id,
                municipio_name=muni.name if muni else "Unknown",
                department_name=dept.name if dept else "Unknown",
                category=gap.category,
                coverage_score=gap.coverage_score,
                total_listings=gap.total_listings or 0,
                listings_with_price=gap.listings_with_price or 0,
                listings_with_images=gap.listings_with_images or 0,
                listings_with_coordinates=gap.listings_with_coordinates or 0,
                avg_images_per_listing=gap.avg_images_per_listing or 0.0,
                priority=gap.priority or "medium",
                needs_field_research=gap.needs_field_research or False,
                field_research_status=gap.field_research_status or "not_started",
                field_researcher=gap.field_researcher,
                field_research_notes=gap.field_research_notes,
                field_research_date=gap.field_research_date,
                last_analyzed=gap.last_analyzed,
            )
        )

    return CoverageGapListResponse(
        results=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/departments", response_model=list[DepartmentCoverageSummary])
async def get_department_coverage(
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentCoverageSummary]:
    """
    Get coverage summary for every department.
    Shows avg scores, gap counts, and per-category breakdowns.
    """
    departments = await db.execute(
        select(Department).order_by(Department.name)
    )
    depts = departments.scalars().all()

    summaries: list[DepartmentCoverageSummary] = []
    for dept in depts:
        # Aggregate gaps for this department
        gap_stats = await db.execute(
            select(
                func.avg(DataCoverageGap.coverage_score).label("avg_score"),
                func.sum(case((DataCoverageGap.priority == "critical", 1), else_=0)).label("critical"),
                func.sum(case((DataCoverageGap.priority == "high", 1), else_=0)).label("high"),
                func.sum(case((DataCoverageGap.priority == "medium", 1), else_=0)).label("medium"),
                func.sum(case((DataCoverageGap.priority == "low", 1), else_=0)).label("low"),
                func.sum(
                    case((DataCoverageGap.needs_field_research.is_(True), 1), else_=0)
                ).label("needs_research"),
            )
            .join(Municipio, DataCoverageGap.municipio_id == Municipio.id)
            .where(Municipio.department_id == dept.id)
        )
        stats = gap_stats.one()

        # Per-category breakdown
        cat_stats = await db.execute(
            select(
                DataCoverageGap.category,
                func.avg(DataCoverageGap.coverage_score).label("avg_score"),
            )
            .join(Municipio, DataCoverageGap.municipio_id == Municipio.id)
            .where(Municipio.department_id == dept.id)
            .group_by(DataCoverageGap.category)
        )
        categories = {row.category: round(float(row.avg_score or 0), 3) for row in cat_stats}

        # Count municipios in this dept
        muni_count = await db.scalar(
            select(func.count(Municipio.id)).where(Municipio.department_id == dept.id)
        )

        summaries.append(
            DepartmentCoverageSummary(
                department_id=dept.id,
                department_name=dept.name,
                total_municipios=muni_count or 0,
                population=dept.population,
                area_km2=dept.area_km2,
                avg_coverage_score=round(float(stats.avg_score or 0), 3),
                critical_gaps=stats.critical or 0,
                high_gaps=stats.high or 0,
                medium_gaps=stats.medium or 0,
                low_gaps=stats.low or 0,
                municipios_needing_research=stats.needs_research or 0,
                categories_covered=categories,
            )
        )

    return summaries


@router.get("/municipios/{municipio_id}", response_model=MunicipioCoverageDetail)
async def get_municipio_coverage(
    municipio_id: int,
    db: AsyncSession = Depends(get_db),
) -> MunicipioCoverageDetail:
    """
    Get full coverage detail for a specific municipio.
    Includes all gap categories and field research status.
    """
    muni = await db.get(Municipio, municipio_id)
    if not muni:
        raise HTTPException(status_code=404, detail=f"Municipio {municipio_id} not found")

    dept = await db.get(Department, muni.department_id)

    # All gaps for this municipio
    result = await db.execute(
        select(DataCoverageGap).where(DataCoverageGap.municipio_id == municipio_id)
    )
    gaps = result.scalars().all()

    gap_outputs = [
        CoverageGapOut(
            id=g.id,
            municipio_id=g.municipio_id,
            municipio_name=muni.name,
            department_name=dept.name if dept else "Unknown",
            category=g.category,
            coverage_score=g.coverage_score,
            total_listings=g.total_listings or 0,
            listings_with_price=g.listings_with_price or 0,
            listings_with_images=g.listings_with_images or 0,
            listings_with_coordinates=g.listings_with_coordinates or 0,
            avg_images_per_listing=g.avg_images_per_listing or 0.0,
            priority=g.priority or "medium",
            needs_field_research=g.needs_field_research or False,
            field_research_status=g.field_research_status or "not_started",
            field_researcher=g.field_researcher,
            field_research_notes=g.field_research_notes,
            field_research_date=g.field_research_date,
            last_analyzed=g.last_analyzed,
        )
        for g in gaps
    ]

    overall = sum(g.coverage_score for g in gaps) / len(gaps) if gaps else 0.0
    worst = min(gaps, key=lambda g: g.coverage_score).category if gaps else None
    best = max(gaps, key=lambda g: g.coverage_score).category if gaps else None

    return MunicipioCoverageDetail(
        municipio_id=muni.id,
        municipio_name=muni.name,
        department_name=dept.name if dept else "Unknown",
        population=muni.population,
        area_km2=muni.area_km2,
        elevation_m=muni.elevation_m,
        centroid_lat=muni.centroid_lat,
        centroid_lng=muni.centroid_lng,
        gaps=gap_outputs,
        overall_score=round(overall, 3),
        worst_category=worst,
        best_category=best,
    )


@router.patch("/gaps/{gap_id}", response_model=CoverageGapOut)
async def update_coverage_gap(
    gap_id: UUID,
    update: CoverageGapUpdate,
    db: AsyncSession = Depends(get_db),
) -> CoverageGapOut:
    """
    Update a coverage gap record — e.g. after field research or scraping.
    """
    gap = await db.get(DataCoverageGap, gap_id)
    if not gap:
        raise HTTPException(status_code=404, detail=f"Coverage gap {gap_id} not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gap, field, value)
    gap.updated_at = datetime.utcnow()

    muni = await db.get(Municipio, gap.municipio_id)
    dept = await db.get(Department, muni.department_id) if muni else None

    return CoverageGapOut(
        id=gap.id,
        municipio_id=gap.municipio_id,
        municipio_name=muni.name if muni else "Unknown",
        department_name=dept.name if dept else "Unknown",
        category=gap.category,
        coverage_score=gap.coverage_score,
        total_listings=gap.total_listings or 0,
        listings_with_price=gap.listings_with_price or 0,
        listings_with_images=gap.listings_with_images or 0,
        listings_with_coordinates=gap.listings_with_coordinates or 0,
        avg_images_per_listing=gap.avg_images_per_listing or 0.0,
        priority=gap.priority or "medium",
        needs_field_research=gap.needs_field_research or False,
        field_research_status=gap.field_research_status or "not_started",
        field_researcher=gap.field_researcher,
        field_research_notes=gap.field_research_notes,
        field_research_date=gap.field_research_date,
        last_analyzed=gap.last_analyzed,
    )


@router.get("/desert-zones", response_model=list[DataDesertZone])
async def get_data_desert_zones() -> list[DataDesertZone]:
    """
    Get known data desert zones — areas that are known to have
    very poor data coverage and need boots-on-the-ground research.
    """
    return [DataDesertZone(**z) for z in DATA_DESERT_ZONES]
