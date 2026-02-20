"""
Listing Completeness & Quality Scoring
========================================

Analyzes each property listing and assigns:
  - completeness_score (0-100): weighted % of filled fields
  - quality_tier: "gold" | "silver" | "bronze"
  - completeness_detail: per-field breakdown with filled/missing status
  - missing_fields: list of actionable gaps
  - ad_ready: bool — whether the listing can be advertised as-is

Weights reflect advertising value — a listing with no images is far
worse than one with no lot size. Structural exemptions apply: land
listings aren't penalized for missing bedrooms/bathrooms.

Usage:
    from ai.content.scoring import ListingScorer

    scorer = ListingScorer()
    scored = scorer.score(record)
    # scored["completeness_score"] → 78
    # scored["quality_tier"] → "silver"

    # Batch:
    results = scorer.score_dataset(records)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ── Field definitions with weights ──
# Higher weight = more important for a usable listing.
# "condition" allows structural exemptions (e.g., land has no beds).

@dataclass(frozen=True)
class ScoringField:
    key: str            # field name in the record
    label: str          # human-readable label
    weight: float       # importance 0-10
    check: str          # check type: "truthy", "length>N", "list>N", "nonzero"
    threshold: int = 0  # for length/list checks
    exempt_types: tuple[str, ...] = ()  # property types where N/A


FIELDS: list[ScoringField] = [
    # ── Critical (ad won't work without these) ──
    ScoringField("title",        "Title",           10, "truthy"),
    ScoringField("price_usd",    "Price",           10, "truthy"),
    ScoringField("images",       "Has images",       9, "list>N",  threshold=1),
    ScoringField("department",   "Department",       8, "truthy"),
    ScoringField("property_type","Property type",    7, "truthy"),

    # ── High value (major quality boost) ──
    ScoringField("description",  "Description",      8, "length>N", threshold=10),
    ScoringField("images",       "3+ photos",        7, "list>N",   threshold=3),
    ScoringField("area_m2",      "Area (m²)",        6, "truthy"),
    ScoringField("municipio",    "Municipio",        6, "truthy"),
    ScoringField("address",      "Address",          5, "truthy"),

    # ── Medium value (nice to have) ──
    ScoringField("bedrooms",     "Bedrooms",         5, "truthy",
                 exempt_types=("land", "commercial", "farm")),
    ScoringField("bathrooms",    "Bathrooms",        5, "truthy",
                 exempt_types=("land", "commercial", "farm")),
    ScoringField("lot_size_m2",  "Lot size",         4, "truthy",
                 exempt_types=("apartment",)),
    ScoringField("images",       "6+ photos",        4, "list>N", threshold=6),

    # ── Lower value (completeness boosters) ──
    ScoringField("seller",       "Seller info",      2, "truthy"),
    ScoringField("listing_date", "Listing date",     2, "truthy"),
    ScoringField("latitude",     "GPS coordinates",  3, "nonzero"),
    ScoringField("features",     "Feature details",  3, "list>N", threshold=1),
]


def _check_field(record: dict, field: ScoringField) -> bool:
    """Evaluate whether a field passes its check."""
    val = record.get(field.key)

    if field.check == "truthy":
        return bool(val)

    if field.check == "length>N":
        # Check description: try both fields
        if field.key == "description":
            desc = record.get("description") or record.get("description_es") or ""
            return isinstance(desc, str) and len(desc.strip()) > field.threshold
        return isinstance(val, str) and len(val.strip()) > field.threshold

    if field.check == "list>N":
        return isinstance(val, list) and len(val) > field.threshold

    if field.check == "nonzero":
        if val is None:
            return False
        try:
            return float(val) != 0.0
        except (ValueError, TypeError):
            return False

    return bool(val)


def _is_exempt(record: dict, field: ScoringField) -> bool:
    """Check if this field is N/A for this property type."""
    if not field.exempt_types:
        return False
    ptype = (record.get("property_type") or "").lower().strip()
    return ptype in field.exempt_types


class ListingScorer:
    """Score listings for completeness and advertising readiness."""

    def __init__(self, fields: list[ScoringField] | None = None):
        self.fields = fields or FIELDS

    def score(self, record: dict) -> dict[str, Any]:
        """
        Score a single listing.

        Returns the original record augmented with:
          - completeness_score: int 0-100
          - quality_tier: "gold" | "silver" | "bronze"
          - completeness_detail: dict of field → {filled, exempt, weight}
          - missing_fields: list of missing field labels
          - ad_ready: bool
        """
        detail: dict[str, dict] = {}
        earned_weight = 0.0
        max_weight = 0.0

        for field in self.fields:
            exempt = _is_exempt(record, field)
            filled = _check_field(record, field)

            if exempt:
                # Don't count against the listing
                detail[field.label] = {
                    "filled": True,
                    "exempt": True,
                    "weight": field.weight,
                }
                earned_weight += field.weight
                max_weight += field.weight
            else:
                detail[field.label] = {
                    "filled": filled,
                    "exempt": False,
                    "weight": field.weight,
                }
                max_weight += field.weight
                if filled:
                    earned_weight += field.weight

        # Calculate score
        score = round(earned_weight / max_weight * 100) if max_weight > 0 else 0

        # Quality tier
        if score >= 80:
            tier = "gold"
        elif score >= 60:
            tier = "silver"
        else:
            tier = "bronze"

        # Missing fields (non-exempt, not filled), sorted by weight desc
        missing = [
            f.label for f in sorted(self.fields, key=lambda x: -x.weight)
            if not _is_exempt(record, f) and not _check_field(record, f)
        ]

        # Ad-ready: has title, price, at least 1 image, and score >= 50
        ad_ready = (
            bool(record.get("title"))
            and bool(record.get("price_usd"))
            and isinstance(record.get("images"), list)
            and len(record.get("images", [])) >= 1
            and score >= 50
        )

        # Augment record
        result = dict(record)
        result["completeness_score"] = score
        result["quality_tier"] = tier
        result["completeness_detail"] = detail
        result["missing_fields"] = missing
        result["ad_ready"] = ad_ready

        return result

    def score_dataset(self, records: list[dict]) -> list[dict]:
        """Score all listings and return augmented records."""
        return [self.score(r) for r in records]

    def summary(self, scored_records: list[dict]) -> dict:
        """Generate dataset-level statistics from scored records."""
        n = len(scored_records)
        if n == 0:
            return {}

        scores = [r["completeness_score"] for r in scored_records]
        scores_sorted = sorted(scores)

        tier_counts = {"gold": 0, "silver": 0, "bronze": 0}
        for r in scored_records:
            tier_counts[r["quality_tier"]] += 1

        ad_ready_count = sum(1 for r in scored_records if r["ad_ready"])

        # Most common missing fields
        from collections import Counter
        missing_counter: Counter[str] = Counter()
        for r in scored_records:
            for m in r["missing_fields"]:
                missing_counter[m] += 1

        return {
            "total_listings": n,
            "avg_score": round(sum(scores) / n, 1),
            "median_score": scores_sorted[n // 2],
            "min_score": scores_sorted[0],
            "max_score": scores_sorted[-1],
            "tiers": tier_counts,
            "ad_ready": ad_ready_count,
            "ad_ready_pct": round(100 * ad_ready_count / n, 1),
            "top_missing_fields": missing_counter.most_common(10),
        }
