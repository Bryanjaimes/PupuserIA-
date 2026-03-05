"""
US Real Estate Valuation endpoints.

Mirrors the El Salvador valuation API but tuned for the American market:
  - US-centric features (school district, HOA, zip codes, Zestimate-style comps)
  - Lat/lon bounds for CONUS + Hawaii + Alaska
  - Price ranges calibrated for US market ($25K – $50M)
  - State + county instead of department + municipio
"""

from __future__ import annotations

import logging
import math
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Enums ─────────────────────────────────────────────


class USPropertyType(str, Enum):
    single_family = "single_family"
    condo = "condo"
    townhouse = "townhouse"
    multi_family = "multi_family"
    land = "land"
    commercial = "commercial"
    mobile_home = "mobile_home"


# ── Pydantic Schemas ─────────────────────────────────


class USValuationRequest(BaseModel):
    """Input features for a US property valuation."""

    # Location
    latitude: float = Field(..., ge=18.0, le=72.0, description="Latitude (CONUS + AK + HI)")
    longitude: float = Field(..., ge=-180.0, le=-66.0, description="Longitude")
    state: str = Field(..., min_length=2, max_length=2, description="Two-letter state code, e.g. 'CA'")
    county: str = Field("", description="County name")
    zip_code: str = Field("", max_length=10, description="ZIP or ZIP+4 code")

    # Physical
    area_sqft: float = Field(..., gt=0, description="Living area in square feet")
    lot_size_sqft: float | None = Field(None, ge=0, description="Lot size in sq ft")
    bedrooms: int | None = Field(None, ge=0)
    bathrooms: float | None = Field(None, ge=0, description="Full + half baths (e.g. 2.5)")
    year_built: int | None = Field(None, ge=1600, le=2030)
    stories: int | None = Field(None, ge=1, le=100)
    garage_spaces: int | None = Field(None, ge=0)
    property_type: USPropertyType = Field(USPropertyType.single_family)
    has_pool: bool = Field(False)
    has_basement: bool = Field(False)

    # Neighbourhood / amenities
    school_rating: float | None = Field(None, ge=1, le=10, description="GreatSchools 1-10")
    hoa_monthly_usd: float | None = Field(None, ge=0, description="Monthly HOA fee")
    crime_index: float | None = Field(None, ge=0, le=100, description="0 = safest, 100 = most crime")
    walk_score: int | None = Field(None, ge=0, le=100)
    transit_score: int | None = Field(None, ge=0, le=100)

    # Listing metadata
    listing_description: str | None = None
    image_count: int = Field(0, ge=0)
    is_foreclosure: bool = Field(False)
    is_new_construction: bool = Field(False)

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "latitude": 34.05,
                "longitude": -118.24,
                "state": "CA",
                "county": "Los Angeles",
                "zip_code": "90012",
                "area_sqft": 1800,
                "lot_size_sqft": 6000,
                "bedrooms": 3,
                "bathrooms": 2.5,
                "year_built": 1985,
                "property_type": "single_family",
                "school_rating": 7,
            }
        ]
    }}


class USValuationResponse(BaseModel):
    """AI-generated US property valuation result."""

    estimated_value_usd: float
    confidence_interval_low: float
    confidence_interval_high: float
    confidence_score: float = Field(..., ge=0, le=1)
    price_per_sqft: float
    rental_yield_estimate: float
    appreciation_5yr_estimate: float
    comparable_range_low: float
    comparable_range_high: float
    model_version: str
    features_importance: dict[str, float]


class USModelInfoResponse(BaseModel):
    """Metadata about the US valuation model."""

    is_loaded: bool
    model_version: str
    markets_covered: list[str]
    training_samples: int | None = None
    median_error_pct: float | None = None


# ── Heuristic price-per-sqft by state (2025 medians) ─


_STATE_PPSF: dict[str, float] = {
    "AL": 130, "AK": 200, "AZ": 260, "AR": 115, "CA": 440,
    "CO": 300, "CT": 250, "DE": 220, "FL": 270, "GA": 185,
    "HI": 630, "ID": 280, "IL": 180, "IN": 140, "IA": 130,
    "KS": 135, "KY": 130, "LA": 125, "ME": 220, "MD": 230,
    "MA": 370, "MI": 145, "MN": 200, "MS": 115, "MO": 145,
    "MT": 270, "NE": 150, "NV": 260, "NH": 260, "NJ": 290,
    "NM": 195, "NY": 300, "NC": 195, "ND": 165, "OH": 140,
    "OK": 125, "OR": 290, "PA": 175, "RI": 270, "SC": 175,
    "SD": 175, "TN": 195, "TX": 170, "UT": 300, "VT": 250,
    "VA": 235, "WA": 350, "WV": 100, "WI": 165, "WY": 210,
    "DC": 480,
}

# Approximate metro premium multiplier
_METRO_COUNTIES: dict[str, float] = {
    "Los Angeles": 1.35, "San Francisco": 1.70, "New York": 1.50,
    "Manhattan": 2.20, "Kings": 1.40, "Miami-Dade": 1.30,
    "Cook": 1.15, "King": 1.40, "Maricopa": 1.05,
    "Clark": 1.10, "Travis": 1.25, "Fulton": 1.20,
    "Denver": 1.20, "Multnomah": 1.25, "Suffolk": 1.30,
    "Honolulu": 1.40, "Boulder": 1.30, "Marin": 1.60,
    "San Mateo": 1.65, "Santa Clara": 1.55,
}

_DEFAULT_PPSF = 200.0


def _estimate_us_property(req: USValuationRequest) -> USValuationResponse:
    """Heuristic valuation for US properties (pre-ML-model bootstrap)."""

    # Base price per sqft
    ppsf = _STATE_PPSF.get(req.state.upper(), _DEFAULT_PPSF)

    # County / metro premium
    metro_mult = _METRO_COUNTIES.get(req.county, 1.0)
    ppsf *= metro_mult

    # Age depreciation: ~0.3% per year past 10 years old
    if req.year_built:
        age = max(0, 2026 - req.year_built)
        if age > 10:
            ppsf *= max(0.70, 1.0 - 0.003 * (age - 10))

    # School rating premium: +2% per point above 5
    if req.school_rating and req.school_rating > 5:
        ppsf *= 1.0 + 0.02 * (req.school_rating - 5)

    # Pool premium
    if req.has_pool:
        ppsf *= 1.05

    # New construction premium
    if req.is_new_construction:
        ppsf *= 1.12

    # Foreclosure discount
    if req.is_foreclosure:
        ppsf *= 0.80

    # Property type adjustments
    type_mult = {
        "single_family": 1.00,
        "condo": 0.90,
        "townhouse": 0.93,
        "multi_family": 1.10,
        "land": 0.25,
        "commercial": 1.15,
        "mobile_home": 0.45,
    }
    ppsf *= type_mult.get(req.property_type.value, 1.0)

    estimated = ppsf * req.area_sqft

    # Confidence — low because heuristic only
    confidence = 0.30
    if req.year_built:
        confidence += 0.05
    if req.school_rating:
        confidence += 0.05
    if req.lot_size_sqft:
        confidence += 0.03
    if req.bathrooms:
        confidence += 0.03
    confidence = min(confidence, 0.55)

    interval_pct = max(0.12, 0.40 * (1 - confidence))
    ci_low = estimated * (1 - interval_pct)
    ci_high = estimated * (1 + interval_pct)

    # Rental yield varies by market
    base_yield = 0.055
    if req.state.upper() in ("CA", "NY", "HI", "MA", "DC"):
        base_yield = 0.035  # Low-yield / high-appreciation
    elif req.state.upper() in ("OH", "IN", "MI", "AL", "MS", "AR"):
        base_yield = 0.08   # High-yield / cash-flow
    if req.property_type == USPropertyType.multi_family:
        base_yield *= 1.30

    # Appreciation estimate by market tier
    if req.state.upper() in ("TX", "FL", "AZ", "NC", "TN", "ID", "UT", "CO"):
        appreciation = 0.30  # High-growth Sun Belt
    elif req.state.upper() in ("CA", "NY", "WA", "MA"):
        appreciation = 0.20  # Mature / expensive
    else:
        appreciation = 0.22

    fi = {
        "area_sqft": 0.30,
        "state": 0.25,
        "county_metro": 0.15,
        "year_built": 0.10,
        "school_rating": 0.08,
        "property_type": 0.07,
        "pool_amenities": 0.03,
        "foreclosure": 0.02,
    }

    return USValuationResponse(
        estimated_value_usd=round(estimated, -2),
        confidence_interval_low=round(ci_low, -2),
        confidence_interval_high=round(ci_high, -2),
        confidence_score=round(confidence, 3),
        price_per_sqft=round(ppsf, 2),
        rental_yield_estimate=round(base_yield, 4),
        appreciation_5yr_estimate=round(appreciation, 3),
        comparable_range_low=round(ci_low * 0.95, -2),
        comparable_range_high=round(ci_high * 1.05, -2),
        model_version="0.1.0-heuristic",
        features_importance=fi,
    )


# ── Endpoints ─────────────────────────────────────────


@router.post("/estimate", response_model=USValuationResponse)
async def us_estimate_value(payload: USValuationRequest):
    """
    Estimate the market value of a US property.

    Returns Zestimate-style pricing: estimated value, confidence interval,
    price per sqft, rental yield, and feature-importance breakdown.
    """
    try:
        return _estimate_us_property(payload)
    except Exception as exc:
        logger.exception("US valuation prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc


@router.post("/batch-estimate", response_model=list[USValuationResponse])
async def us_batch_estimate(payloads: list[USValuationRequest]):
    """Batch-estimate up to 50 US properties in a single request."""
    if len(payloads) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 properties per batch")
    return [_estimate_us_property(p) for p in payloads]


@router.get("/model-info", response_model=USModelInfoResponse)
async def us_model_info():
    """Metadata about the US valuation model."""
    return USModelInfoResponse(
        is_loaded=False,
        model_version="0.1.0-heuristic",
        markets_covered=sorted(_STATE_PPSF.keys()),
        training_samples=None,
        median_error_pct=None,
    )


@router.get("/markets", response_model=dict[str, float])
async def us_markets():
    """Return the median price-per-sqft for all supported state markets."""
    return dict(sorted(_STATE_PPSF.items()))
