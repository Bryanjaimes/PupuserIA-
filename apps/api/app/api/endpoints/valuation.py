"""
Valuation endpoints — AI-powered property price estimation.

POST /valuation/estimate   → Get an estimated value for a property
GET  /valuation/model-info → Metadata about the loaded ML model
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Ensure project root is importable (for `ai.*` package) ──
_PROJECT_ROOT = Path(__file__).resolve().parents[5]  # …/PupuserIA-
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ── Path to the trained model ─────────────────────────
_MODEL_DIR = _PROJECT_ROOT / "ai" / "valuation" / "models"
_MODEL_PATH = _MODEL_DIR / "xgb_valuation_v1.json"

# Lazy-loaded singleton engine
_engine = None


def _get_engine():
    """Return (or initialise) the singleton ValuationEngine."""
    global _engine
    if _engine is None:
        from ai.valuation.engine import ValuationEngine

        _engine = ValuationEngine(str(_MODEL_PATH) if _MODEL_PATH.exists() else None)
    return _engine


# ── Pydantic schemas ─────────────────────────────────


class ValuationRequest(BaseModel):
    """Input features for a property valuation."""

    latitude: float = Field(..., ge=12.0, le=16.0, description="Latitude (WGS-84)")
    longitude: float = Field(..., ge=-91.0, le=-86.0, description="Longitude (WGS-84)")
    department: str = Field(..., description="Department name, e.g. 'San Salvador'")
    municipio: str = Field("", description="Municipio / city name")

    area_m2: float = Field(..., gt=0, description="Built area in square metres")
    lot_size_m2: float | None = Field(None, ge=0, description="Lot size in m² (optional)")
    bedrooms: int | None = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: int | None = Field(None, ge=0, description="Number of bathrooms")
    property_type: str = Field("house", description="house | apartment | land | commercial")

    listing_description: str | None = Field(None, description="Free-text listing description")
    image_urls: list[str] = Field(default_factory=list, description="Image URLs (count is a feature)")
    is_foreclosure: bool = Field(False, description="Whether the property is bank-foreclosed")

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "latitude": 13.69,
                "longitude": -89.22,
                "department": "San Salvador",
                "municipio": "San Salvador",
                "area_m2": 150,
                "bedrooms": 3,
                "bathrooms": 2,
                "property_type": "house",
            }
        ]
    }}


class ValuationResponse(BaseModel):
    """AI-generated property valuation result."""

    estimated_value_usd: float
    confidence_interval_low: float
    confidence_interval_high: float
    confidence_score: float = Field(..., ge=0, le=1, description="0–1 confidence")
    rental_yield_estimate: float = Field(..., description="Estimated annual rental yield (%)")
    appreciation_5yr_estimate: float = Field(..., description="Estimated 5-year appreciation (%)")
    model_version: str
    features_importance: dict[str, float]


class ModelInfoResponse(BaseModel):
    """Metadata about the currently-loaded valuation model."""

    is_loaded: bool
    model_version: str
    training_samples: int | None = None
    cv_metrics: dict[str, float] | None = None
    feature_count: int | None = None


# ── Endpoints ─────────────────────────────────────────


@router.post("/estimate", response_model=ValuationResponse)
async def estimate_value(payload: ValuationRequest):
    """
    Estimate the market value of a property based on its features.

    Returns an estimated price in USD, a confidence interval,
    rental yield estimate, and feature-importance breakdown.
    """
    engine = _get_engine()

    from ai.valuation.engine import PropertyFeatures

    features = PropertyFeatures(
        latitude=payload.latitude,
        longitude=payload.longitude,
        department=payload.department,
        municipio=payload.municipio,
        area_m2=payload.area_m2,
        lot_size_m2=payload.lot_size_m2,
        bedrooms=payload.bedrooms,
        bathrooms=payload.bathrooms,
        property_type=payload.property_type,
        listing_description=payload.listing_description,
        image_urls=payload.image_urls,
        is_foreclosure=payload.is_foreclosure,
    )

    try:
        result = engine.predict(features)
    except Exception as exc:
        logger.exception("Valuation prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    return ValuationResponse(
        estimated_value_usd=result.estimated_value_usd,
        confidence_interval_low=result.confidence_interval_low,
        confidence_interval_high=result.confidence_interval_high,
        confidence_score=result.confidence_score,
        rental_yield_estimate=result.rental_yield_estimate,
        appreciation_5yr_estimate=result.appreciation_5yr_estimate,
        model_version=result.model_version,
        features_importance=result.features_importance,
    )


@router.get("/model-info", response_model=ModelInfoResponse)
async def model_info():
    """
    Return metadata about the currently-loaded valuation model,
    including CV metrics and training sample count.
    """
    engine = _get_engine()

    cv_metrics = engine.metadata.get("cv_metrics") if engine.metadata else None
    training_samples = engine.metadata.get("training_samples") if engine.metadata else None
    feature_count = engine.metadata.get("n_features") if engine.metadata else None

    return ModelInfoResponse(
        is_loaded=engine.is_loaded,
        model_version=engine.model_version,
        training_samples=training_samples,
        cv_metrics=cv_metrics,
        feature_count=feature_count,
    )
