"""
Scraped-data endpoints — serve property listings directly from JSONL files.

These endpoints work without a running PostgreSQL database. They read
from the scraper output directory and serve the raw/scored data.

GET  /data/properties          → Paginated listing of all scraped properties
GET  /data/properties/all      → Every single record (use with care)
GET  /data/properties/{id}     → Single property by PIA ID
GET  /data/stats               → Aggregate stats over scraped data
GET  /data/sources             → Available JSONL source files
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Resolve the scraper output directory ──────────────
_DATA_DIR = Path(__file__).resolve().parents[5] / "data" / "scrapers" / "data" / "scraper_output"

# Preferred scored file, then unscored, then any JSONL
_PREFERRED_FILES = [
    "all_listings_scored.jsonl",
    "all_listings_20260220_scored.jsonl",
    "all_listings_20260220.jsonl",
]

_CROWD_FILE = _DATA_DIR / "crowd_listings.jsonl"
_BROKER_VERIFY_TOKEN = os.getenv("BROKER_VERIFY_TOKEN")


def _find_data_file() -> Path | None:
    """Find the best available JSONL data file."""
    for name in _PREFERRED_FILES:
        path = _DATA_DIR / name
        if path.exists():
            return path
    # Fallback: any file that starts with "all_listings"
    for path in sorted(_DATA_DIR.glob("all_listings*.jsonl"), reverse=True):
        return path
    return None


def _sanitize_record(rec: dict[str, Any]) -> dict[str, Any]:
    """Strip third-party image URLs and source URLs for copyright safety."""
    images = rec.pop("images", []) or []
    rec["image_count"] = len(images) if isinstance(images, list) else 0

    source_url = rec.pop("source_url", None)
    if source_url:
        try:
            rec["source_domain"] = urlparse(source_url).netloc
        except Exception:
            rec["source_domain"] = None
    else:
        rec["source_domain"] = None

    status_value = rec.get("verification_status")
    if status_value not in {"unverified", "verified"}:
        rec["verification_status"] = "verified"
    rec["is_verified"] = rec["verification_status"] == "verified"
    return rec


def _load_crowd_records() -> list[dict[str, Any]]:
    """Load crowd-submitted listing records."""
    if not _CROWD_FILE.exists():
        return []

    records: list[dict[str, Any]] = []
    with open(_CROWD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _write_crowd_records(records: list[dict[str, Any]]) -> None:
    """Rewrite the crowd listings file in JSONL format."""
    _CROWD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_CROWD_FILE, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _append_crowd_record(record: dict[str, Any]) -> None:
    """Append a single crowd listing record."""
    _CROWD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_CROWD_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_crowd_id() -> str:
    return f"USR-{uuid4().hex[:10].upper()}"


def _load_all_records() -> list[dict[str, Any]]:
    """Load every record from the best available JSONL file."""
    path = _find_data_file()
    records: list[dict[str, Any]] = []

    if path:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(_sanitize_record(json.loads(line)))
                    except json.JSONDecodeError:
                        continue

    for crowd in _load_crowd_records():
        records.append(_sanitize_record(crowd))

    return records


# ── Pydantic Schemas ─────────────────────────────────


class ScrapedPropertyOut(BaseModel):
    """A scraped property listing as stored in JSONL."""

    id: str | None = None
    title: str | None = None
    description: str | None = None
    price_usd: float | None = None
    price_currency: str | None = None
    property_type: str | None = None
    bedrooms: int | None = None
    bathrooms: float | None = None
    area_m2: float | None = None
    lot_size_m2: float | None = None
    department: str | None = None
    municipio: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_count: int = 0
    features: list[str] = []
    source: str | None = None
    source_domain: str | None = None
    listing_date: str | None = None
    scraped_at: str | None = None
    completeness_score: int | None = None
    quality_tier: str | None = None
    missing_fields: list[str] = []
    ad_ready: bool | None = None
    verification_status: str = "verified"
    is_verified: bool = True
    submitted_by_name: str | None = None
    submitted_by_contact: str | None = None
    submitted_at: str | None = None
    verified_by: str | None = None
    verified_at: str | None = None
    verification_notes: str | None = None

    model_config = {"extra": "allow"}  # pass through any extra fields


class PaginatedPropertiesResponse(BaseModel):
    """Paginated response of scraped properties."""

    results: list[ScrapedPropertyOut]
    total: int
    page: int
    page_size: int
    source_file: str


class DataStatsResponse(BaseModel):
    """Aggregate stats from scraped data."""

    total_records: int
    with_price: int
    avg_price_usd: float | None
    min_price_usd: float | None
    max_price_usd: float | None
    by_department: dict[str, int]
    by_property_type: dict[str, int]
    by_quality_tier: dict[str, int]
    source_file: str


class SourceFileInfo(BaseModel):
    """Info about a JSONL source file."""

    filename: str
    size_bytes: int
    record_count: int | None = None


class CrowdListingCreate(BaseModel):
    title: str = Field(min_length=4, max_length=255)
    description: str | None = None
    price_usd: float | None = Field(default=None, ge=0)
    property_type: str = Field(min_length=2, max_length=50)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: float | None = Field(default=None, ge=0)
    area_m2: float | None = Field(default=None, ge=0)
    lot_size_m2: float | None = Field(default=None, ge=0)
    department: str = Field(min_length=2, max_length=100)
    municipio: str = Field(min_length=2, max_length=100)
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    features: list[str] = []
    submitted_by_name: str = Field(min_length=2, max_length=120)
    submitted_by_contact: str | None = Field(default=None, max_length=120)


class CrowdListingCreateResponse(BaseModel):
    id: str
    verification_status: str
    message: str


class VerifyListingRequest(BaseModel):
    broker_name: str = Field(min_length=2, max_length=120)
    notes: str | None = Field(default=None, max_length=2000)


# ── Endpoints ─────────────────────────────────────────


@router.get("", response_model=PaginatedPropertiesResponse)
async def list_properties(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=500, description="Items per page"),
    department: str | None = Query(default=None, description="Filter by department"),
    property_type: str | None = Query(default=None, description="Filter by type"),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    quality_tier: str | None = Query(default=None, description="gold, silver, or bronze"),
    verification_status: str | None = Query(default=None, pattern="^(unverified|verified)$"),
):
    """
    Paginated listing of all scraped properties.

    Reads directly from JSONL files — no database required.
    Supports filtering by department, property type, price range, and quality tier.
    """
    records = _load_all_records()
    source_file = _find_data_file()

    # Apply filters
    if department:
        records = [r for r in records if (r.get("department") or "").lower() == department.lower()]
    if property_type:
        records = [r for r in records if (r.get("property_type") or "").lower() == property_type.lower()]
    if min_price is not None:
        records = [r for r in records if (r.get("price_usd") or 0) >= min_price]
    if max_price is not None:
        records = [r for r in records if (r.get("price_usd") or float("inf")) <= max_price]
    if quality_tier:
        records = [r for r in records if (r.get("quality_tier") or "").lower() == quality_tier.lower()]
    if verification_status:
        records = [r for r in records if (r.get("verification_status") or "verified") == verification_status]

    total = len(records)
    start = (page - 1) * page_size
    page_records = records[start : start + page_size]

    return PaginatedPropertiesResponse(
        results=[ScrapedPropertyOut(**r) for r in page_records],
        total=total,
        page=page,
        page_size=page_size,
        source_file=source_file.name if source_file else "none",
    )


@router.get("/stats", response_model=DataStatsResponse)
async def data_stats():
    """Aggregate statistics over all scraped listings."""
    records = _load_all_records()
    source_file = _find_data_file()
    if not records:
        raise HTTPException(status_code=404, detail="No scraped data found")

    prices = [r["price_usd"] for r in records if r.get("price_usd") and r["price_usd"] > 0]

    by_dept: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_tier: dict[str, int] = {}
    for r in records:
        dept = r.get("department", "Unknown")
        by_dept[dept] = by_dept.get(dept, 0) + 1
        ptype = r.get("property_type", "unknown")
        by_type[ptype] = by_type.get(ptype, 0) + 1
        tier = r.get("quality_tier", "unscored")
        by_tier[tier] = by_tier.get(tier, 0) + 1

    return DataStatsResponse(
        total_records=len(records),
        with_price=len(prices),
        avg_price_usd=round(sum(prices) / len(prices), 2) if prices else None,
        min_price_usd=min(prices) if prices else None,
        max_price_usd=max(prices) if prices else None,
        by_department=dict(sorted(by_dept.items(), key=lambda x: -x[1])),
        by_property_type=dict(sorted(by_type.items(), key=lambda x: -x[1])),
        by_quality_tier=dict(sorted(by_tier.items(), key=lambda x: -x[1])),
        source_file=source_file.name if source_file else "none",
    )


@router.get("/sources", response_model=list[SourceFileInfo])
async def list_source_files():
    """List all JSONL files in the scraper output directory."""
    if not _DATA_DIR.exists():
        return []
    files = []
    for p in sorted(_DATA_DIR.glob("*.jsonl")):
        files.append(SourceFileInfo(
            filename=p.name,
            size_bytes=p.stat().st_size,
        ))
    return files


@router.get("/{property_id}", response_model=ScrapedPropertyOut)
async def get_property_by_id(property_id: str):
    """Look up a single property by its PIA ID (e.g. PIA-000042)."""
    records = _load_all_records()
    for r in records:
        if r.get("id") == property_id:
            return ScrapedPropertyOut(**r)
    raise HTTPException(status_code=404, detail=f"Property {property_id} not found")


@router.post("/submit", response_model=CrowdListingCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_crowd_listing(payload: CrowdListingCreate):
    """Submit a crowd-sourced property listing as unverified."""
    record = {
        "id": _new_crowd_id(),
        "title": payload.title,
        "description": payload.description,
        "price_usd": payload.price_usd,
        "price_currency": "USD",
        "property_type": payload.property_type,
        "bedrooms": payload.bedrooms,
        "bathrooms": payload.bathrooms,
        "area_m2": payload.area_m2,
        "lot_size_m2": payload.lot_size_m2,
        "department": payload.department,
        "municipio": payload.municipio,
        "address": payload.address,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "features": payload.features,
        "source": "crowd_submitted",
        "verification_status": "unverified",
        "submitted_by_name": payload.submitted_by_name,
        "submitted_by_contact": payload.submitted_by_contact,
        "submitted_at": _utcnow_iso(),
        "scraped_at": _utcnow_iso(),
    }
    _append_crowd_record(record)

    return CrowdListingCreateResponse(
        id=record["id"],
        verification_status="unverified",
        message="Listing submitted and pending broker verification",
    )


@router.post("/{property_id}/verify", response_model=ScrapedPropertyOut)
async def verify_crowd_listing(
    property_id: str,
    payload: VerifyListingRequest,
    x_broker_token: str | None = Header(default=None),
):
    """Mark a crowd-submitted listing as broker-verified."""
    if not _BROKER_VERIFY_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Broker verification token not configured",
        )

    if x_broker_token != _BROKER_VERIFY_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid broker token")

    crowd_records = _load_crowd_records()
    if not crowd_records:
        raise HTTPException(status_code=404, detail="No crowd-submitted listings found")

    updated_record: dict[str, Any] | None = None
    for rec in crowd_records:
        if rec.get("id") != property_id:
            continue

        if rec.get("verification_status") == "verified":
            raise HTTPException(status_code=409, detail="Listing is already verified")

        rec["verification_status"] = "verified"
        rec["verified_by"] = payload.broker_name
        rec["verified_at"] = _utcnow_iso()
        rec["verification_notes"] = payload.notes
        updated_record = rec
        break

    if not updated_record:
        raise HTTPException(status_code=404, detail=f"Crowd listing {property_id} not found")

    _write_crowd_records(crowd_records)
    return ScrapedPropertyOut(**_sanitize_record(updated_record))
