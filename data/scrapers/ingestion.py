"""
Property Ingestion Pipeline
============================
Takes ScrapedProperty objects from any scraper and upserts them
into the PostgreSQL database. Handles:
  - Deduplication by listing_url + content_hash
  - Department/municipio resolution against admin division tables
  - Geocoding fallback for missing coordinates
  - Coverage gap score recalculation
  - Image URL validation
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from typing import Sequence
from uuid import uuid4

from sqlalchemy import select, func, update, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Allow running from data/scrapers/ directory
import sys
from pathlib import Path

# Add the API app to the path so we can import models
API_APP_DIR = Path(__file__).resolve().parent.parent.parent / "apps" / "api"
if str(API_APP_DIR) not in sys.path:
    sys.path.insert(0, str(API_APP_DIR))

from base import ScrapedProperty, ScrapeResult

logger = logging.getLogger(__name__)


# ── Department / Municipio coordinate centroids ──
# Fallback coordinates when scraper doesn't provide them

DEPARTMENT_CENTROIDS = {
    "San Salvador": (13.6989, -89.1914),
    "La Libertad": (13.4900, -89.3200),
    "Santa Ana": (13.9940, -89.5597),
    "San Miguel": (13.4833, -88.1833),
    "Sonsonate": (13.7190, -89.7240),
    "Usulután": (13.3500, -88.4500),
    "Ahuachapán": (13.9214, -89.8450),
    "La Paz": (13.5000, -88.9500),
    "La Unión": (13.3400, -87.8400),
    "Chalatenango": (14.0333, -88.9333),
    "Cuscatlán": (13.7200, -88.9300),
    "Morazán": (13.7500, -88.1000),
    "San Vicente": (13.6333, -88.8000),
    "Cabañas": (13.8600, -88.7500),
}


class PropertyIngester:
    """
    Ingests ScrapedProperty objects into the PostgreSQL database.
    
    Usage:
        ingester = PropertyIngester(database_url)
        async with ingester:
            stats = await ingester.ingest(scrape_result)
            print(f"Inserted {stats['inserted']}, updated {stats['updated']}")
    """

    def __init__(self, database_url: str):
        self.database_url = database_url
        self._engine = None
        self._session_factory = None

    async def __aenter__(self):
        self._engine = create_async_engine(
            self.database_url,
            pool_size=5,
            echo=False,
        )
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        return self

    async def __aexit__(self, *args):
        if self._engine:
            await self._engine.dispose()

    async def _get_session(self) -> AsyncSession:
        return self._session_factory()

    async def _resolve_department(
        self, session: AsyncSession, department_name: str
    ) -> int | None:
        """Resolve department name to ID."""
        if not department_name:
            return None

        result = await session.execute(
            text(
                "SELECT id FROM departments WHERE LOWER(name) = LOWER(:name) LIMIT 1"
            ),
            {"name": department_name},
        )
        row = result.fetchone()
        return row[0] if row else None

    async def _resolve_municipio(
        self, session: AsyncSession, municipio_name: str, department_id: int | None
    ) -> int | None:
        """Resolve municipio name to ID."""
        if not municipio_name:
            return None

        query = "SELECT id FROM municipios WHERE LOWER(name) = LOWER(:name)"
        params: dict = {"name": municipio_name}

        if department_id:
            query += " AND department_id = :dept_id"
            params["dept_id"] = department_id

        query += " LIMIT 1"

        result = await session.execute(text(query), params)
        row = result.fetchone()
        return row[0] if row else None

    def _fallback_coordinates(
        self, department: str
    ) -> tuple[float, float]:
        """Get fallback coordinates from department centroid."""
        centroid = DEPARTMENT_CENTROIDS.get(department)
        if centroid:
            return centroid
        # Default: San Salvador center
        return (13.6989, -89.1914)

    def _clean_title(self, title: str) -> str:
        """Clean and normalize a property title."""
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        # Capitalize properly
        if title.isupper() or title.islower():
            title = title.title()
        # Truncate
        return title[:255]

    def _generate_english_title(self, title_es: str, property_type: str) -> str:
        """Generate a basic English title from Spanish title."""
        # Simple translation patterns
        replacements = {
            "casa": "House",
            "apartamento": "Apartment",
            "terreno": "Land",
            "local comercial": "Commercial Space",
            "oficina": "Office",
            "bodega": "Warehouse",
            "venta": "For Sale",
            "alquiler": "For Rent",
            "en": "in",
            "de": "in",
            "con": "with",
            "habitaciones": "bedrooms",
            "baños": "bathrooms",
            "piscina": "pool",
            "jardín": "garden",
            "garaje": "garage",
            "nueva": "New",
            "nuevo": "New",
            "amplia": "Spacious",
            "amplio": "Spacious",
            "moderna": "Modern",
            "moderno": "Modern",
            "hermosa": "Beautiful",
            "hermoso": "Beautiful",
        }

        title = title_es
        for es, en in replacements.items():
            title = re.sub(
                rf'\b{re.escape(es)}\b',
                en,
                title,
                flags=re.IGNORECASE,
            )

        return title[:255]

    def _validate_images(self, images: list[str]) -> list[str]:
        """Filter and validate image URLs."""
        valid = []
        for url in images:
            if not url or not isinstance(url, str):
                continue
            # Must be a proper URL
            if not url.startswith(("http://", "https://")):
                continue
            # Skip tiny icons, tracking pixels, etc.
            if any(
                x in url.lower()
                for x in ["1x1", "pixel", "tracking", "spacer", "blank", "logo", "icon"]
            ):
                continue
            valid.append(url)
        return valid[:20]  # Cap at 20 images

    async def ingest_property(
        self, session: AsyncSession, prop: ScrapedProperty
    ) -> dict:
        """
        Ingest a single ScrapedProperty into the database.
        Returns {"action": "inserted"|"updated"|"skipped", "id": uuid}.
        """
        # Check for existing by listing_url
        existing = None
        if prop.source_url:
            result = await session.execute(
                text(
                    "SELECT id, updated_at FROM properties "
                    "WHERE listing_url = :url LIMIT 1"
                ),
                {"url": prop.source_url},
            )
            existing = result.fetchone()

        # Resolve department and municipio IDs
        dept_id = await self._resolve_department(session, prop.department)
        muni_id = await self._resolve_municipio(session, prop.municipio, dept_id)

        # Get coordinates (from scraper or fallback)
        lat = prop.latitude
        lng = prop.longitude
        if lat is None or lng is None:
            lat, lng = self._fallback_coordinates(prop.department)

        # Prepare property data
        title_es = self._clean_title(prop.title)
        title_en = self._generate_english_title(title_es, prop.property_type)
        images = self._validate_images(prop.images)

        property_data = {
            "title": title_en,
            "title_es": title_es,
            "description": "",  # Could use AI translation
            "description_es": prop.description_es or prop.description or "",
            "property_type": prop.property_type or "house",
            "department": prop.department or "San Salvador",
            "municipio": prop.municipio or "",
            "municipio_id": muni_id,
            "price_usd": prop.price_usd,
            "bedrooms": prop.bedrooms,
            "bathrooms": prop.bathrooms,
            "area_m2": prop.area_m2,
            "lot_size_m2": prop.lot_size_m2,
            "latitude": lat,
            "longitude": lng,
            "images": images,
            "features": prop.features[:20] if prop.features else [],
            "source": prop.source,
            "listing_url": prop.source_url,
            "is_active": True,
            "is_featured": False,
            "neighborhood_score": prop.quality_score * 10,  # 0-10 scale
            "updated_at": datetime.utcnow(),
        }

        if existing:
            # Update existing record
            prop_id = existing[0]
            await session.execute(
                text(
                    "UPDATE properties SET "
                    "title = :title, title_es = :title_es, "
                    "description_es = :description_es, "
                    "price_usd = :price_usd, "
                    "bedrooms = :bedrooms, bathrooms = :bathrooms, "
                    "area_m2 = :area_m2, lot_size_m2 = :lot_size_m2, "
                    "latitude = :latitude, longitude = :longitude, "
                    "images = :images, features = :features, "
                    "neighborhood_score = :neighborhood_score, "
                    "is_active = :is_active, "
                    "updated_at = :updated_at "
                    "WHERE id = :id"
                ),
                {
                    **{k: v for k, v in property_data.items() 
                       if k not in ("description", "municipio_id", "department", 
                                    "municipio", "property_type", "source", 
                                    "listing_url", "is_featured")},
                    "images": str(images).replace("'", '"'),  # JSONB
                    "features": str(property_data["features"]).replace("'", '"'),
                    "id": prop_id,
                },
            )
            return {"action": "updated", "id": prop_id}
        else:
            # Insert new record
            prop_id = uuid4()
            await session.execute(
                text("""
                    INSERT INTO properties (
                        id, title, title_es, description, description_es,
                        property_type, department, municipio, municipio_id,
                        price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
                        latitude, longitude, images, features,
                        source, listing_url, is_active, is_featured,
                        neighborhood_score, created_at, updated_at
                    ) VALUES (
                        :id, :title, :title_es, :description, :description_es,
                        :property_type, :department, :municipio, :municipio_id,
                        :price_usd, :bedrooms, :bathrooms, :area_m2, :lot_size_m2,
                        :latitude, :longitude, :images::jsonb, :features::jsonb,
                        :source, :listing_url, :is_active, :is_featured,
                        :neighborhood_score, :created_at, :updated_at
                    )
                """),
                {
                    "id": str(prop_id),
                    **property_data,
                    "images": str(images).replace("'", '"'),
                    "features": str(property_data["features"]).replace("'", '"'),
                    "created_at": datetime.utcnow(),
                },
            )
            return {"action": "inserted", "id": prop_id}

    async def ingest(self, result: ScrapeResult) -> dict:
        """
        Ingest all properties from a ScrapeResult.
        Returns aggregate stats.
        """
        stats = {
            "source": result.source,
            "total": len(result.properties),
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "error_details": [],
        }

        async with self._session_factory() as session:
            for i, prop in enumerate(result.properties):
                try:
                    result_action = await self.ingest_property(session, prop)
                    stats[result_action["action"]] = stats.get(result_action["action"], 0) + 1

                    if (i + 1) % 50 == 0:
                        logger.info(
                            f"  Progress: {i + 1}/{stats['total']} "
                            f"(+{stats['inserted']} new, ~{stats['updated']} updated)"
                        )
                        await session.commit()

                except Exception as e:
                    stats["errors"] += 1
                    stats["error_details"].append(
                        f"{prop.source_url}: {str(e)[:100]}"
                    )
                    logger.error(f"  Error ingesting {prop.source_url}: {e}")
                    await session.rollback()
                    # Re-create session after rollback
                    continue

            # Final commit
            try:
                await session.commit()
            except Exception as e:
                logger.error(f"Final commit failed: {e}")
                await session.rollback()
                stats["errors"] += 1

        logger.info(
            f"Ingestion complete: {stats['inserted']} inserted, "
            f"{stats['updated']} updated, {stats['skipped']} skipped, "
            f"{stats['errors']} errors"
        )
        return stats

    async def ingest_properties(self, properties: Sequence[ScrapedProperty]) -> dict:
        """Convenience method to ingest a list of properties directly."""
        result = ScrapeResult(
            source=properties[0].source if properties else "unknown",
            department=None,
            municipio=None,
            started_at=datetime.utcnow(),
            properties=list(properties),
            total_found=len(properties),
        )
        result.finished_at = datetime.utcnow()
        return await self.ingest(result)

    async def mark_stale_listings(
        self, source: str, days_threshold: int = 30
    ) -> int:
        """Mark listings as inactive if they haven't been updated recently."""
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    UPDATE properties 
                    SET is_active = false, updated_at = NOW()
                    WHERE source = :source 
                    AND is_active = true
                    AND updated_at < NOW() - INTERVAL ':days days'
                """),
                {"source": source, "days": days_threshold},
            )
            await session.commit()
            count = result.rowcount
            logger.info(f"Marked {count} stale {source} listings as inactive")
            return count

    async def update_coverage_scores(self) -> None:
        """
        Recalculate coverage gap scores based on current property data.
        """
        async with self._session_factory() as session:
            # Get per-municipio stats
            result = await session.execute(
                text("""
                    SELECT 
                        municipio_id,
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE price_usd IS NOT NULL) as with_price,
                        COUNT(*) FILTER (WHERE images IS NOT NULL AND images != '[]'::jsonb) as with_images,
                        COUNT(*) FILTER (WHERE latitude IS NOT NULL AND longitude IS NOT NULL) as with_coords,
                        AVG(neighborhood_score) as avg_score
                    FROM properties
                    WHERE is_active = true AND municipio_id IS NOT NULL
                    GROUP BY municipio_id
                """)
            )

            rows = result.fetchall()
            for row in rows:
                muni_id, total, with_price, with_images, with_coords, avg_score = row
                
                # Calculate coverage score (0-1)
                score = min(
                    (min(total, 50) / 50) * 0.3
                    + (with_price / max(total, 1)) * 0.25
                    + (with_images / max(total, 1)) * 0.2
                    + (with_coords / max(total, 1)) * 0.15
                    + min((avg_score or 0) / 10, 1.0) * 0.1,
                    1.0,
                )

                await session.execute(
                    text("""
                        UPDATE data_coverage_gaps 
                        SET coverage_score = :score,
                            total_listings = :total,
                            listings_with_price = :with_price,
                            listings_with_images = :with_images,
                            listings_with_coordinates = :with_coords,
                            last_analyzed = NOW(),
                            updated_at = NOW()
                        WHERE municipio_id = :muni_id 
                        AND category = 'property_listings'
                    """),
                    {
                        "score": score,
                        "total": total,
                        "with_price": with_price,
                        "with_images": with_images,
                        "with_coords": with_coords,
                        "muni_id": muni_id,
                    },
                )

            await session.commit()
            logger.info(f"Updated coverage scores for {len(rows)} municipios")

    async def get_stats(self) -> dict:
        """Get current property database stats."""
        async with self._session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE is_active) as active,
                        COUNT(DISTINCT department) as departments,
                        COUNT(DISTINCT source) as sources,
                        COUNT(*) FILTER (WHERE price_usd IS NOT NULL) as with_price,
                        COUNT(*) FILTER (WHERE images IS NOT NULL AND images != '[]'::jsonb) as with_images,
                        AVG(price_usd) FILTER (WHERE price_usd IS NOT NULL) as avg_price,
                        MIN(created_at) as oldest,
                        MAX(updated_at) as newest
                    FROM properties
                """)
            )
            row = result.fetchone()
            return {
                "total": row[0],
                "active": row[1],
                "departments": row[2],
                "sources": row[3],
                "with_price": row[4],
                "with_images": row[5],
                "avg_price": float(row[6]) if row[6] else 0,
                "oldest_record": str(row[7]) if row[7] else None,
                "newest_update": str(row[8]) if row[8] else None,
            }
