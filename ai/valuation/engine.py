"""
AI Valuation Engine — "The Zestimate for El Salvador"
=====================================================

Hybrid ML model for property price estimation in a market with zero comps data.

Architecture:
  - XGBoost ensemble for structured features (location, size, amenities)
  - Vision Transformer for satellite/street imagery analysis (V2)
  - Text embeddings for listing description signals (V2)
  - Macroeconomic feature engineering (tourism growth, construction permits)

Data Sources:
  - Scraped listing data from ES property sites
  - Government cadastral records
  - Satellite imagery (Mapbox / Google Earth Engine)
  - Proximity features (beach, airport, schools, hospitals)

Usage:
    engine = ValuationEngine("ai/valuation/models/xgb_valuation_v1.json")
    result = engine.predict(PropertyFeatures(
        latitude=13.69, longitude=-89.22,
        department="San Salvador", municipio="San Salvador",
        area_m2=150, property_type="house", bedrooms=3, bathrooms=2,
    ))
    print(f"Estimated: ${result.estimated_value_usd:,.0f}")
"""

import json
import logging
from pathlib import Path

import numpy as np
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Constants (must match train.py) ───────────────────

DEPARTMENTS = [
    "San Salvador", "La Libertad", "Santa Ana", "San Miguel",
    "Sonsonate", "La Paz", "Usulután", "Ahuachapán",
    "Cuscatlán", "Chalatenango", "Cabañas", "Morazán",
    "La Unión", "San Vicente",
]

PROPERTY_TYPES = ["house", "apartment", "land", "commercial"]

DEPARTMENT_CENTROIDS = {
    "San Salvador":  (13.6929, -89.2182),
    "La Libertad":   (13.4883, -89.3220),
    "Santa Ana":     (13.9946, -89.5597),
    "San Miguel":    (13.4833, -88.1833),
    "Sonsonate":     (13.7167, -89.7333),
    "La Paz":        (13.5000, -88.9500),
    "Usulután":      (13.3500, -88.4500),
    "Ahuachapán":    (13.9214, -89.8450),
    "Cuscatlán":     (13.7167, -88.9333),
    "Chalatenango":  (14.0333, -88.9333),
    "Cabañas":       (13.8667, -88.7500),
    "Morazán":       (13.7667, -88.1000),
    "La Unión":      (13.3333, -87.8500),
    "San Vicente":   (13.6333, -88.8000),
}

BEACH_COORDS = [
    (13.4833, -89.3833),
    (13.4300, -89.5500),
    (13.3333, -88.5833),
    (13.1667, -87.8333),
]

AIRPORT_COORD = (13.4409, -89.0557)
SAN_SALVADOR_COORD = (13.6929, -89.2182)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return float(R * 2 * np.arcsin(np.sqrt(a)))


# ── Data Models ───────────────────────────────────────


@dataclass
class PropertyFeatures:
    """Structured features for the valuation model."""

    # Location
    latitude: float
    longitude: float
    department: str
    municipio: str

    # Physical
    area_m2: float
    lot_size_m2: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    year_built: int | None = None
    property_type: str = "house"

    # Proximity (km)
    distance_to_beach_km: float | None = None
    distance_to_airport_km: float | None = None
    distance_to_san_salvador_km: float | None = None
    distance_to_nearest_school_km: float | None = None
    distance_to_nearest_hospital_km: float | None = None

    # Neighborhood
    tourism_density_score: float | None = None
    safety_score: float | None = None
    walkability_score: float | None = None

    # Listing metadata
    listing_description: str | None = None
    image_urls: list[str] = field(default_factory=list)
    is_foreclosure: bool = False


@dataclass
class ValuationResult:
    """Output of the valuation model."""

    estimated_value_usd: float
    confidence_interval_low: float
    confidence_interval_high: float
    confidence_score: float  # 0.0 - 1.0
    rental_yield_estimate: float  # Annual percentage
    appreciation_5yr_estimate: float  # Percentage
    model_version: str
    features_importance: dict[str, float]


# ── Engine ────────────────────────────────────────────


class ValuationEngine:
    """
    Property valuation engine using hybrid XGBoost + deep learning approach.

    V1: XGBoost on structured features.
    V2 (future): adds satellite imagery and text embeddings.
    """

    def __init__(self, model_path: str | None = None):
        self.model = None
        self.model_version = "0.1.0-stub"
        self.is_loaded = False
        self.metadata: dict = {}
        self.feature_config: dict = {}
        self.dept_medians: dict[str, float] = {}

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> None:
        """Load a trained XGBoost model and its config from disk."""
        model_file = Path(model_path)
        if not model_file.exists():
            logger.warning(f"Model file not found: {model_path}")
            self.is_loaded = False
            return

        try:
            import xgboost as xgb

            self.model = xgb.XGBRegressor()
            self.model.load_model(str(model_file))

            # Load metadata
            meta_path = model_file.parent / "model_metadata.json"
            if meta_path.exists():
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
                self.model_version = self.metadata.get("model_version", "1.0.0")

            # Load feature config
            config_path = model_file.parent / "feature_config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.feature_config = json.load(f)
                self.dept_medians = self.feature_config.get("dept_median_price_per_m2", {})

            self.is_loaded = True
            logger.info(
                f"Loaded valuation model v{self.model_version} "
                f"(R²={self.metadata.get('cv_metrics', {}).get('r2', '?')})"
            )

        except ImportError:
            logger.error("xgboost not installed. Run: pip install xgboost")
            self.is_loaded = False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_loaded = False

    def _featurize(self, features: PropertyFeatures) -> np.ndarray:
        """Convert PropertyFeatures into the feature vector expected by the model."""
        # Resolve coordinates
        lat = features.latitude
        lon = features.longitude
        if not (13.0 < lat < 15.0 and -91.0 < lon < -87.0):
            centroid = DEPARTMENT_CENTROIDS.get(features.department, (13.69, -89.22))
            lat, lon = centroid

        # Proximity
        beach_dists = [_haversine_km(lat, lon, blat, blon) for blat, blon in BEACH_COORDS]
        min_beach = min(beach_dists)
        airport_dist = _haversine_km(lat, lon, *AIRPORT_COORD)
        ss_dist = _haversine_km(lat, lon, *SAN_SALVADOR_COORD)

        # Department median price per m²
        dept_median = self.dept_medians.get(features.department, 500.0)

        # Build feature vector (must match train.py order exactly)
        vec = [
            np.log1p(features.area_m2),
            np.log1p(features.lot_size_m2) if features.lot_size_m2 and features.lot_size_m2 > 0 else 0.0,
            features.bedrooms or 0,
            features.bathrooms or 0,
            lat,
            lon,
            min_beach,
            airport_dist,
            ss_dist,
            dept_median,
            1.0 if features.is_foreclosure else 0.0,
            1.0 if features.image_urls else 0.0,
            len(features.image_urls),
            len(features.listing_description or ""),
        ]

        # One-hot property type
        for ptype in PROPERTY_TYPES:
            vec.append(1.0 if ptype == features.property_type else 0.0)

        # One-hot department
        for dept in DEPARTMENTS:
            vec.append(1.0 if dept == features.department else 0.0)

        return np.array([vec], dtype=np.float32)

    def predict(self, features: PropertyFeatures) -> ValuationResult:
        """Generate a property valuation from features."""
        if not self.is_loaded:
            return self._heuristic_valuation(features)

        X = self._featurize(features)
        log_pred = float(self.model.predict(X)[0])
        estimated = float(np.expm1(log_pred))

        # Confidence based on model's CV metrics and input completeness
        cv_r2 = self.metadata.get("cv_metrics", {}).get("r2", 0.5)
        completeness = 0.5
        if features.bedrooms is not None:
            completeness += 0.1
        if features.bathrooms is not None:
            completeness += 0.1
        if features.lot_size_m2:
            completeness += 0.1
        if features.image_urls:
            completeness += 0.1
        if features.listing_description:
            completeness += 0.1
        confidence = min(cv_r2 * completeness * 1.5, 0.95)

        # Confidence interval scales with confidence
        interval_pct = max(0.10, 0.40 * (1 - confidence))
        ci_low = estimated * (1 - interval_pct)
        ci_high = estimated * (1 + interval_pct)

        # Rental yield estimate by department/type
        base_yield = 0.07
        if features.property_type == "apartment":
            base_yield = 0.08
        elif features.property_type == "commercial":
            base_yield = 0.09
        elif features.property_type == "land":
            base_yield = 0.03

        # Beach proximity premium on yields
        lat = features.latitude
        lon = features.longitude
        if 13.0 < lat < 15.0 and -91.0 < lon < -87.0:
            min_beach = min(_haversine_km(lat, lon, b[0], b[1]) for b in BEACH_COORDS)
            if min_beach < 5:
                base_yield *= 1.3

        # Feature importance from model
        fi = self.metadata.get("feature_importance", {})

        return ValuationResult(
            estimated_value_usd=round(estimated, -2),
            confidence_interval_low=round(ci_low, -2),
            confidence_interval_high=round(ci_high, -2),
            confidence_score=round(confidence, 3),
            rental_yield_estimate=round(base_yield, 4),
            appreciation_5yr_estimate=0.35,
            model_version=self.model_version,
            features_importance=fi,
        )

    def _heuristic_valuation(self, features: PropertyFeatures) -> ValuationResult:
        """
        Simple heuristic-based valuation for bootstrapping.
        Uses average $/m² by department as a starting point.
        """
        price_per_m2 = {
            "San Salvador": 1200,
            "La Libertad": 1000,
            "Santa Ana": 600,
            "San Miguel": 500,
            "Sonsonate": 700,
            "La Paz": 550,
            "Usulután": 450,
            "Ahuachapán": 400,
            "Cuscatlán": 500,
            "Chalatenango": 350,
            "Cabañas": 300,
            "Morazán": 300,
            "La Unión": 400,
            "San Vicente": 400,
        }

        base_rate = price_per_m2.get(features.department, 500)
        estimated = features.area_m2 * base_rate

        # Beach proximity premium
        if features.distance_to_beach_km and features.distance_to_beach_km < 5:
            estimated *= 1.4

        return ValuationResult(
            estimated_value_usd=round(estimated, -2),
            confidence_interval_low=round(estimated * 0.7, -2),
            confidence_interval_high=round(estimated * 1.3, -2),
            confidence_score=0.3,
            rental_yield_estimate=0.08,
            appreciation_5yr_estimate=0.35,
            model_version=self.model_version,
            features_importance={"area_m2": 0.4, "department": 0.3, "beach_proximity": 0.15},
        )

    def train(self, training_data_path: str) -> dict:
        """Train the valuation model on collected data."""
        from ai.valuation.train import run_pipeline

        model_dir = str(Path(__file__).parent / "models")
        return run_pipeline(training_data_path, model_dir)
