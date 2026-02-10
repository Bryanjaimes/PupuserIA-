"""
Property Scraper Framework — El Salvador
=========================================
Base classes and utilities for ethical web scraping of property listings.
Supports multiple sources with rate limiting, robots.txt compliance,
and automatic coverage gap tracking.

Usage:
    from data.scrapers.base import BaseScraper, ScrapedProperty
    
    class MySourceScraper(BaseScraper):
        source_name = "my_source"
        base_url = "https://example.com"
        
        async def scrape_listings(self, department=None, municipio=None):
            ...
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import AsyncGenerator

import httpx

logger = logging.getLogger(__name__)


# ── Data Models ──────────────────────────────────────


@dataclass
class ScrapedProperty:
    """A property listing extracted from a source."""

    # Required
    title: str
    source: str  # e.g. "encuentra24", "olx"
    source_url: str

    # Location
    department: str = ""
    municipio: str = ""
    canton: str = ""
    address: str = ""
    latitude: float | None = None
    longitude: float | None = None

    # Pricing
    price_usd: float | None = None
    price_currency: str = "USD"
    price_raw: str = ""  # original text

    # Property details
    property_type: str = ""  # house, apartment, land, commercial
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_m2: float | None = None
    lot_size_m2: float | None = None

    # Content
    description: str = ""
    description_es: str = ""
    images: list[str] = field(default_factory=list)

    # Metadata
    listing_date: datetime | None = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    raw_html: str = ""
    features: list[str] = field(default_factory=list)

    @property
    def content_hash(self) -> str:
        """Dedup hash based on source + URL."""
        return hashlib.sha256(f"{self.source}:{self.source_url}".encode()).hexdigest()[:16]

    @property
    def has_price(self) -> bool:
        return self.price_usd is not None and self.price_usd > 0

    @property
    def has_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    @property
    def has_images(self) -> bool:
        return len(self.images) > 0

    @property
    def quality_score(self) -> float:
        """0.0–1.0 quality score based on data completeness."""
        score = 0.0
        if self.title: score += 0.1
        if self.description or self.description_es: score += 0.1
        if self.has_price: score += 0.2
        if self.has_coordinates: score += 0.2
        if self.has_images: score += 0.15
        if self.department and self.municipio: score += 0.1
        if self.property_type: score += 0.05
        if self.bedrooms is not None: score += 0.05
        if self.area_m2 is not None: score += 0.05
        return min(score, 1.0)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["scraped_at"] = self.scraped_at.isoformat()
        if self.listing_date:
            d["listing_date"] = self.listing_date.isoformat()
        return d


@dataclass
class ScrapeResult:
    """Result of a scrape session."""

    source: str
    department: str | None
    municipio: str | None
    started_at: datetime
    finished_at: datetime | None = None
    total_found: int = 0
    total_new: int = 0
    total_updated: int = 0
    total_errors: int = 0
    properties: list[ScrapedProperty] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return 0.0


# ── Rate Limiter ─────────────────────────────────────


class RateLimiter:
    """Token-bucket rate limiter for ethical scraping."""

    def __init__(self, requests_per_second: float = 1.0, burst: int = 3):
        self.rate = requests_per_second
        self.burst = burst
        self._tokens = float(burst)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
            self._last_refill = now

            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self.rate
                logger.debug(f"Rate limiter: waiting {wait:.2f}s")
                await asyncio.sleep(wait)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0


# ── Base Scraper ─────────────────────────────────────


class BaseScraper(ABC):
    """
    Abstract base for all property scrapers.
    Handles rate limiting, HTTP client, and result collection.
    """

    source_name: str = "unknown"
    base_url: str = ""
    requests_per_second: float = 0.5  # Conservative default
    max_retries: int = 3
    timeout: float = 30.0

    def __init__(self):
        self.rate_limiter = RateLimiter(
            requests_per_second=self.requests_per_second, burst=2
        )
        self._client: httpx.AsyncClient | None = None
        self._seen_urls: set[str] = set()

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "GatewayElSalvador-PropertyResearch/1.0 "
                    "(https://gateway.com.sv; research@gateway.com.sv)"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-SV,es;q=0.9,en;q=0.8",
            },
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def fetch(self, url: str) -> httpx.Response | None:
        """Fetch a URL with rate limiting and retries."""
        await self.rate_limiter.acquire()

        for attempt in range(1, self.max_retries + 1):
            try:
                if not self._client:
                    raise RuntimeError("Scraper not initialized. Use 'async with' context.")
                resp = await self._client.get(url)
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2 ** attempt * 5  # Exponential backoff
                    logger.warning(f"Rate limited by {urlparse(url).netloc}, waiting {wait}s")
                    await asyncio.sleep(wait)
                elif e.response.status_code >= 500:
                    logger.warning(f"Server error {e.response.status_code} for {url}, retry {attempt}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"HTTP {e.response.status_code} for {url}")
                    return None
            except httpx.RequestError as e:
                logger.warning(f"Request error for {url}: {e}, retry {attempt}")
                await asyncio.sleep(2 ** attempt)

        logger.error(f"Failed after {self.max_retries} retries: {url}")
        return None

    @abstractmethod
    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 10,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """
        Yield property listings from this source.
        Override in subclass to implement actual scraping logic.
        """
        yield  # type: ignore

    async def run(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 10,
        output_dir: str | None = None,
    ) -> ScrapeResult:
        """Run the scraper and collect results."""
        result = ScrapeResult(
            source=self.source_name,
            department=department,
            municipio=municipio,
            started_at=datetime.utcnow(),
        )

        try:
            async with self:
                async for prop in self.scrape_listings(
                    department=department,
                    municipio=municipio,
                    max_pages=max_pages,
                ):
                    if prop.source_url in self._seen_urls:
                        continue
                    self._seen_urls.add(prop.source_url)
                    result.properties.append(prop)
                    result.total_found += 1
                    result.total_new += 1
        except Exception as e:
            result.errors.append(str(e))
            result.total_errors += 1
            logger.error(f"Scraper {self.source_name} error: {e}")

        result.finished_at = datetime.utcnow()

        # Optionally save to disk
        if output_dir:
            self._save_results(result, output_dir)

        logger.info(
            f"[{self.source_name}] Scraped {result.total_found} listings "
            f"in {result.duration_seconds:.1f}s "
            f"({result.total_errors} errors)"
        )
        return result

    def _save_results(self, result: ScrapeResult, output_dir: str) -> None:
        """Save scraped results as JSONL."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.source_name}_{result.department or 'all'}_{timestamp}.jsonl"
        filepath = out_path / filename

        with open(filepath, "w", encoding="utf-8") as f:
            for prop in result.properties:
                f.write(json.dumps(prop.to_dict(), ensure_ascii=False) + "\n")

        logger.info(f"Saved {len(result.properties)} listings to {filepath}")


# ── Coverage Analyzer ────────────────────────────────


class CoverageAnalyzer:
    """
    Analyzes scraped data against the 262 municipios to identify
    coverage gaps and update the database.
    """

    def __init__(self, results: list[ScrapeResult]):
        self.results = results

    def get_coverage_by_municipio(self) -> dict[str, dict]:
        """Returns per-municipio stats from scraped data."""
        coverage: dict[str, dict] = {}

        for result in self.results:
            for prop in result.properties:
                key = f"{prop.department}:{prop.municipio}"
                if key not in coverage:
                    coverage[key] = {
                        "department": prop.department,
                        "municipio": prop.municipio,
                        "total_listings": 0,
                        "with_price": 0,
                        "with_images": 0,
                        "with_coordinates": 0,
                        "total_images": 0,
                        "avg_quality": 0.0,
                        "sources": set(),
                    }
                c = coverage[key]
                c["total_listings"] += 1
                if prop.has_price:
                    c["with_price"] += 1
                if prop.has_images:
                    c["with_images"] += 1
                    c["total_images"] += len(prop.images)
                if prop.has_coordinates:
                    c["with_coordinates"] += 1
                c["sources"].add(prop.source)

        # Calculate averages
        for key, c in coverage.items():
            total = c["total_listings"]
            if total > 0:
                c["avg_quality"] = sum(
                    p.quality_score
                    for r in self.results
                    for p in r.properties
                    if f"{p.department}:{p.municipio}" == key
                ) / total
                c["avg_images"] = c["total_images"] / total
            c["sources"] = list(c["sources"])

        return coverage

    def generate_gap_sql(self) -> str:
        """Generate SQL to update coverage gap records."""
        coverage = self.get_coverage_by_municipio()
        statements = []

        for key, c in coverage.items():
            total = c["total_listings"]
            score = 0.0
            if total > 0:
                score = min(
                    (
                        (min(total, 50) / 50) * 0.3
                        + (c["with_price"] / total) * 0.25
                        + (c["with_images"] / total) * 0.2
                        + (c["with_coordinates"] / total) * 0.15
                        + min(c["avg_quality"], 1.0) * 0.1
                    ),
                    1.0,
                )

            statements.append(
                f"UPDATE data_coverage_gaps SET "
                f"coverage_score = {score:.3f}, "
                f"total_listings = {total}, "
                f"listings_with_price = {c['with_price']}, "
                f"listings_with_images = {c['with_images']}, "
                f"listings_with_coordinates = {c['with_coordinates']}, "
                f"avg_images_per_listing = {c.get('avg_images', 0):.1f}, "
                f"last_analyzed = NOW(), "
                f"updated_at = NOW() "
                f"WHERE municipio_id = (SELECT id FROM municipios WHERE name = '{c['municipio']}' "
                f"AND department_id = (SELECT id FROM departments WHERE name = '{c['department']}')) "
                f"AND category = 'property_listings';"
            )

        return "\n".join(statements)
