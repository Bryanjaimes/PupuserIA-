"""
Valuation Model — Training Pipeline
=====================================
End-to-end pipeline: scraped JSONL → feature engineering → XGBoost model.

This implements V1 of "The Zestimate for El Salvador":
  1. Load & clean scraped property data from JSONL files
  2. Engineer features (location encoding, proximity, size ratios)
  3. Train XGBoost regressor with cross-validation
  4. Evaluate on holdout set
  5. Save model + metadata for serving

Usage:
    python -m ai.valuation.train --data data/scrapers/data/scraper_output/ --output ai/valuation/models/
    python -m ai.valuation.train --data data/scrapers/data/scraper_output/ --output ai/valuation/models/ --eval-only --model ai/valuation/models/xgb_valuation_v1.json
"""

from __future__ import annotations

import argparse
import json
import hashlib
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────

DEPARTMENTS = [
    "San Salvador", "La Libertad", "Santa Ana", "San Miguel",
    "Sonsonate", "La Paz", "Usulután", "Ahuachapán",
    "Cuscatlán", "Chalatenango", "Cabañas", "Morazán",
    "La Unión", "San Vicente",
]

PROPERTY_TYPES = ["house", "apartment", "land", "commercial"]

# Department centroids (lat, lon) for fallback geocoding
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

# Beach coordinates for proximity calculation (major surf spots)
BEACH_COORDS = [
    (13.4833, -89.3833),  # El Tunco / La Libertad
    (13.4300, -89.5500),  # Costa del Sol
    (13.3333, -88.5833),  # Playa El Espino
    (13.1667, -87.8333),  # Golfo de Fonseca
]

# San Salvador international airport
AIRPORT_COORD = (13.4409, -89.0557)

# San Salvador centro
SAN_SALVADOR_COORD = (13.6929, -89.2182)

# Minimum required records for training
MIN_TRAINING_RECORDS = 50

# Price outlier bounds (USD)
MIN_PRICE = 5_000
MAX_PRICE = 5_000_000


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


# ── Data Loading ──────────────────────────────────────

def load_jsonl_files(data_dir: str) -> list[dict]:
    """Load all JSONL files from a directory."""
    records = []
    data_path = Path(data_dir)

    if not data_path.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return records

    jsonl_files = list(data_path.glob("*.jsonl"))
    logger.info(f"Found {len(jsonl_files)} JSONL files in {data_dir}")

    for filepath in sorted(jsonl_files):
        count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                    count += 1
                except json.JSONDecodeError:
                    continue
        logger.info(f"  Loaded {count} records from {filepath.name}")

    logger.info(f"Total raw records: {len(records)}")
    return records


def deduplicate(records: list[dict]) -> list[dict]:
    """Deduplicate by source_url, keeping the richest record."""
    by_url: dict[str, dict] = {}

    for record in records:
        url = record.get("source_url", "")
        if not url:
            continue

        if url in by_url:
            # Keep the record with more non-null fields
            existing_score = sum(1 for v in by_url[url].values() if v)
            new_score = sum(1 for v in record.values() if v)
            if new_score > existing_score:
                by_url[url] = record
        else:
            by_url[url] = record

    logger.info(f"After deduplication: {len(by_url)} unique records")
    return list(by_url.values())


def filter_for_training(records: list[dict]) -> list[dict]:
    """Filter records that have enough data for training."""
    valid = []
    skipped = {"no_price": 0, "no_area": 0, "no_department": 0, "outlier_price": 0, "no_type": 0}

    for r in records:
        price = r.get("price_usd")
        if not price or price <= 0:
            skipped["no_price"] += 1
            continue

        if price < MIN_PRICE or price > MAX_PRICE:
            skipped["outlier_price"] += 1
            continue

        area = r.get("area_m2")
        if not area or area <= 0:
            skipped["no_area"] += 1
            continue

        dept = r.get("department", "")
        if not dept or dept not in DEPARTMENTS:
            skipped["no_department"] += 1
            continue

        ptype = r.get("property_type", "")
        if not ptype or ptype not in PROPERTY_TYPES:
            skipped["no_type"] += 1
            continue

        valid.append(r)

    logger.info(f"Valid training records: {len(valid)}")
    for reason, count in skipped.items():
        if count > 0:
            logger.info(f"  Skipped ({reason}): {count}")

    return valid


# ── Feature Engineering ───────────────────────────────

def engineer_features(records: list[dict]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Transform raw records into feature matrix X and target vector y.
    
    Features:
      - area_m2 (log-transformed)
      - lot_size_m2 (log-transformed, 0 if missing)
      - bedrooms (0 if missing)
      - bathrooms (0 if missing)
      - property_type (one-hot: house, apartment, land, commercial)
      - department (one-hot: 14 departments)
      - latitude, longitude (raw, or department centroid)
      - distance_to_beach_km (min distance to any major beach)
      - distance_to_airport_km
      - distance_to_san_salvador_km
      - price_per_m2_department_median (leakage-free: uses leave-one-out)
      - is_foreclosure (binary flag)
      - has_images (binary)
      - image_count
      - description_length
    
    Returns:
      (X, y, feature_names)
    """
    n = len(records)

    # Pre-compute department median price per m² (leave-one-out)
    dept_prices: dict[str, list[float]] = {}
    for r in records:
        dept = r["department"]
        ppm2 = r["price_usd"] / r["area_m2"]
        dept_prices.setdefault(dept, []).append(ppm2)

    dept_medians: dict[str, float] = {}
    for dept, prices in dept_prices.items():
        dept_medians[dept] = float(np.median(prices))

    # Build feature names
    feature_names = [
        "log_area_m2",
        "log_lot_size_m2",
        "bedrooms",
        "bathrooms",
        "latitude",
        "longitude",
        "distance_to_beach_km",
        "distance_to_airport_km",
        "distance_to_san_salvador_km",
        "dept_median_price_per_m2",
        "is_foreclosure",
        "has_images",
        "image_count",
        "description_length",
    ]
    # One-hot property type
    for ptype in PROPERTY_TYPES:
        feature_names.append(f"type_{ptype}")
    # One-hot department
    for dept in DEPARTMENTS:
        feature_names.append(f"dept_{dept.lower().replace(' ', '_')}")

    num_features = len(feature_names)
    X = np.zeros((n, num_features), dtype=np.float32)
    y = np.zeros(n, dtype=np.float32)

    for i, r in enumerate(records):
        # Target: log price (helps with skewed distribution)
        y[i] = np.log1p(r["price_usd"])

        col = 0

        # Continuous features
        X[i, col] = np.log1p(r["area_m2"]); col += 1
        lot = r.get("lot_size_m2") or 0
        X[i, col] = np.log1p(lot) if lot > 0 else 0; col += 1
        X[i, col] = r.get("bedrooms") or 0; col += 1
        X[i, col] = r.get("bathrooms") or 0; col += 1

        # Coordinates
        lat = r.get("latitude")
        lon = r.get("longitude")
        if not lat or not lon or not (13.0 < lat < 15.0 and -91.0 < lon < -87.0):
            # Fallback to department centroid
            centroid = DEPARTMENT_CENTROIDS.get(r["department"], (13.69, -89.22))
            lat, lon = centroid
        X[i, col] = lat; col += 1
        X[i, col] = lon; col += 1

        # Proximity features
        beach_dists = [haversine_km(lat, lon, blat, blon) for blat, blon in BEACH_COORDS]
        X[i, col] = min(beach_dists); col += 1
        X[i, col] = haversine_km(lat, lon, *AIRPORT_COORD); col += 1
        X[i, col] = haversine_km(lat, lon, *SAN_SALVADOR_COORD); col += 1

        # Department median (leave-one-out to prevent leakage)
        my_ppm2 = r["price_usd"] / r["area_m2"]
        dept_prices_list = dept_prices[r["department"]]
        if len(dept_prices_list) > 1:
            loo_median = float(np.median([p for p in dept_prices_list if p != my_ppm2]))
        else:
            loo_median = dept_medians[r["department"]]
        X[i, col] = loo_median; col += 1

        # Binary features
        features_list = r.get("features", [])
        X[i, col] = 1.0 if "foreclosure" in features_list else 0.0; col += 1
        images = r.get("images", [])
        X[i, col] = 1.0 if images else 0.0; col += 1
        X[i, col] = len(images); col += 1
        desc = r.get("description", "") or r.get("description_es", "") or ""
        X[i, col] = len(desc); col += 1

        # One-hot property type
        ptype = r.get("property_type", "")
        for pt in PROPERTY_TYPES:
            X[i, col] = 1.0 if pt == ptype else 0.0
            col += 1

        # One-hot department
        dept = r["department"]
        for d in DEPARTMENTS:
            X[i, col] = 1.0 if d == dept else 0.0
            col += 1

    return X, y, feature_names


# ── Training ──────────────────────────────────────────

def train_model(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    output_dir: str,
    n_folds: int = 5,
) -> dict[str, Any]:
    """
    Train an XGBoost model with k-fold cross-validation.
    
    Returns metrics dict with RMSE, MAE, R², and feature importance.
    """
    try:
        import xgboost as xgb
        from sklearn.model_selection import KFold
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    except ImportError as e:
        logger.error(
            f"Missing dependency: {e}\n"
            "Install with: pip install xgboost scikit-learn"
        )
        sys.exit(1)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"\nTraining XGBoost model")
    logger.info(f"  Samples:  {X.shape[0]}")
    logger.info(f"  Features: {X.shape[1]}")
    logger.info(f"  Folds:    {n_folds}")

    # Hyperparameters (tuned for small-to-medium real estate datasets)
    params = {
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "max_depth": 6,
        "learning_rate": 0.05,
        "n_estimators": 500,
        "min_child_weight": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "random_state": 42,
        "verbosity": 0,
    }

    # Cross-validation
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    fold_metrics = []
    oof_predictions = np.zeros(len(y))

    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X)):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model = xgb.XGBRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        y_pred = model.predict(X_val)
        oof_predictions[val_idx] = y_pred

        # Metrics in log space
        rmse_log = float(np.sqrt(mean_squared_error(y_val, y_pred)))

        # Metrics in USD space (more interpretable)
        y_val_usd = np.expm1(y_val)
        y_pred_usd = np.expm1(y_pred)
        rmse_usd = float(np.sqrt(mean_squared_error(y_val_usd, y_pred_usd)))
        mae_usd = float(mean_absolute_error(y_val_usd, y_pred_usd))
        r2 = float(r2_score(y_val_usd, y_pred_usd))

        # Median Absolute Percentage Error
        mape = float(np.median(np.abs(y_val_usd - y_pred_usd) / y_val_usd) * 100)

        fold_metrics.append({
            "fold": fold_idx + 1,
            "rmse_log": rmse_log,
            "rmse_usd": rmse_usd,
            "mae_usd": mae_usd,
            "r2": r2,
            "median_ape": mape,
            "n_train": len(train_idx),
            "n_val": len(val_idx),
        })

        logger.info(
            f"  Fold {fold_idx + 1}: RMSE=${rmse_usd:,.0f}  MAE=${mae_usd:,.0f}  "
            f"R²={r2:.3f}  MdAPE={mape:.1f}%"
        )

    # Aggregate cross-validation metrics
    avg_rmse = np.mean([m["rmse_usd"] for m in fold_metrics])
    avg_mae = np.mean([m["mae_usd"] for m in fold_metrics])
    avg_r2 = np.mean([m["r2"] for m in fold_metrics])
    avg_mape = np.mean([m["median_ape"] for m in fold_metrics])

    logger.info(f"\n  CV Average: RMSE=${avg_rmse:,.0f}  MAE=${avg_mae:,.0f}  R²={avg_r2:.3f}  MdAPE={avg_mape:.1f}%")

    # Train final model on all data
    logger.info("\nTraining final model on all data...")
    final_model = xgb.XGBRegressor(**params)
    final_model.fit(X, y, verbose=False)

    # Feature importance
    importance = dict(zip(feature_names, final_model.feature_importances_.tolist()))
    top_features = sorted(importance.items(), key=lambda x: -x[1])[:15]

    logger.info("\n  Top 15 features:")
    for fname, fscore in top_features:
        logger.info(f"    {fname:35s} {fscore:.4f}")

    # Save model
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    model_version = f"1.0.0-{timestamp[:8]}"

    model_filename = f"xgb_valuation_v1.json"
    model_path = out_path / model_filename
    final_model.save_model(str(model_path))
    logger.info(f"\n  Model saved: {model_path}")

    # Save metadata
    data_hash = hashlib.sha256(
        json.dumps({"n": X.shape[0], "features": X.shape[1]}).encode()
    ).hexdigest()[:12]

    metadata = {
        "model_version": model_version,
        "model_file": model_filename,
        "trained_at": datetime.utcnow().isoformat(),
        "n_samples": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "feature_names": feature_names,
        "target": "log1p(price_usd)",
        "hyperparameters": params,
        "cv_folds": n_folds,
        "cv_metrics": {
            "rmse_usd": round(avg_rmse, 2),
            "mae_usd": round(avg_mae, 2),
            "r2": round(avg_r2, 4),
            "median_ape_pct": round(avg_mape, 2),
        },
        "fold_metrics": fold_metrics,
        "feature_importance": dict(top_features),
        "data_hash": data_hash,
        "price_bounds": {"min": MIN_PRICE, "max": MAX_PRICE},
        "departments": DEPARTMENTS,
        "property_types": PROPERTY_TYPES,
    }

    meta_path = out_path / "model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info(f"  Metadata saved: {meta_path}")

    # Save feature config (needed by inference)
    feature_config = {
        "feature_names": feature_names,
        "departments": DEPARTMENTS,
        "property_types": PROPERTY_TYPES,
        "department_centroids": {k: list(v) for k, v in DEPARTMENT_CENTROIDS.items()},
        "beach_coords": BEACH_COORDS,
        "airport_coord": list(AIRPORT_COORD),
        "san_salvador_coord": list(SAN_SALVADOR_COORD),
        "dept_median_price_per_m2": {
            dept: round(float(np.median(prices)), 2)
            for dept, prices in dept_prices_global.items()
        } if "dept_prices_global" in dir() else {},
    }

    config_path = out_path / "feature_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(feature_config, f, indent=2, ensure_ascii=False)
    logger.info(f"  Feature config saved: {config_path}")

    return metadata


# Global for saving dept prices into feature config
dept_prices_global: dict[str, list[float]] = {}


def run_pipeline(
    data_dir: str,
    output_dir: str,
    n_folds: int = 5,
) -> dict[str, Any]:
    """Run the complete training pipeline."""

    global dept_prices_global

    logger.info("=" * 60)
    logger.info("Valuation Model — Training Pipeline")
    logger.info("=" * 60)
    logger.info(f"  Data dir:    {data_dir}")
    logger.info(f"  Output dir:  {output_dir}")
    logger.info(f"  CV folds:    {n_folds}")
    logger.info("=" * 60)

    # 1. Load data
    logger.info("\n[1/5] Loading data...")
    records = load_jsonl_files(data_dir)
    if not records:
        logger.error("No records found. Exiting.")
        sys.exit(1)

    # 2. Deduplicate
    logger.info("\n[2/5] Deduplicating...")
    records = deduplicate(records)

    # 3. Filter
    logger.info("\n[3/5] Filtering for training...")
    records = filter_for_training(records)
    if len(records) < MIN_TRAINING_RECORDS:
        logger.error(
            f"Only {len(records)} valid records — need at least {MIN_TRAINING_RECORDS}. "
            f"Run more scrapers to collect data."
        )
        sys.exit(1)

    # 4. Feature engineering
    logger.info("\n[4/5] Engineering features...")
    X, y, feature_names = engineer_features(records)

    # Store dept prices for feature config
    for r in records:
        dept = r["department"]
        ppm2 = r["price_usd"] / r["area_m2"]
        dept_prices_global.setdefault(dept, []).append(ppm2)

    # Print data summary
    prices = [r["price_usd"] for r in records]
    logger.info(f"\n  Data summary:")
    logger.info(f"    Records:      {len(records)}")
    logger.info(f"    Price range:  ${min(prices):,.0f} — ${max(prices):,.0f}")
    logger.info(f"    Median price: ${np.median(prices):,.0f}")
    logger.info(f"    Mean price:   ${np.mean(prices):,.0f}")

    dept_counts = {}
    for r in records:
        dept_counts[r["department"]] = dept_counts.get(r["department"], 0) + 1
    logger.info(f"\n  By department:")
    for dept, count in sorted(dept_counts.items(), key=lambda x: -x[1]):
        logger.info(f"    {dept:20s}: {count}")

    type_counts = {}
    for r in records:
        type_counts[r["property_type"]] = type_counts.get(r["property_type"], 0) + 1
    logger.info(f"\n  By property type:")
    for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        logger.info(f"    {ptype:20s}: {count}")

    foreclosure_count = sum(1 for r in records if "foreclosure" in r.get("features", []))
    logger.info(f"\n  Foreclosures:   {foreclosure_count}")

    # 5. Train
    logger.info("\n[5/5] Training model...")
    metadata = train_model(X, y, feature_names, output_dir, n_folds)

    logger.info("\n" + "=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"  Model:  {output_dir}/xgb_valuation_v1.json")
    logger.info(f"  RMSE:   ${metadata['cv_metrics']['rmse_usd']:,.0f}")
    logger.info(f"  MAE:    ${metadata['cv_metrics']['mae_usd']:,.0f}")
    logger.info(f"  R²:     {metadata['cv_metrics']['r2']:.4f}")
    logger.info(f"  MdAPE:  {metadata['cv_metrics']['median_ape_pct']:.1f}%")
    logger.info("=" * 60)

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Train the property valuation model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data", "-d",
        default="data/scrapers/data/scraper_output",
        help="Directory containing JSONL files from scrapers",
    )
    parser.add_argument(
        "--output", "-o",
        default="ai/valuation/models",
        help="Directory to save the trained model",
    )
    parser.add_argument(
        "--folds", "-k",
        type=int,
        default=5,
        help="Number of cross-validation folds",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    run_pipeline(args.data, args.output, args.folds)


if __name__ == "__main__":
    main()
