#!/usr/bin/env python3
"""
Encuentra24 — Two-Layer CSE Pipeline
======================================
Bypasses Cloudflare by using Google Custom Search Engine as a discovery
layer, then selectively enriches high-priority listings.

Layer 1 (Discovery):
  Google CSE → URLs + slug-parsed metadata + snippet text.
  Free: 100 queries/day × 10 results = 1,000 listings/day.
  Paid: $5 per 1,000 queries via googleapis.com.

Layer 2 (Enrichment):
  Targeted fetches on individual listing pages using stealth headers
  and cookie persistence. Rate-limited to 50-100 pages/day with
  random delays. Since we already have the URLs, this is directed
  lookups — lighter footprint, harder to detect.

Setup:
  1. Create a Programmable Search Engine at:
     https://programmablesearchengine.google.com/
     Restrict to: encuentra24.com
  2. Get an API key from Google Cloud Console.
  3. Set env vars:
     GOOGLE_CSE_API_KEY=AIza...
     GOOGLE_CSE_ID=abc123...

Usage:
  python run.py cse --max-queries 20               # Discovery only
  python run.py cse --max-queries 50 --enrich 100   # + enrichment
  python run.py cse --enrich-file cse_output.jsonl  # Enrich existing
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from base import BaseScraper, ScrapedProperty, ScrapeResult

logger = logging.getLogger(__name__)


# ── Slug → canonical name maps ───────────────────────

DEPARTMENT_SLUGS = {
    "san-salvador": "San Salvador",
    "la-libertad": "La Libertad",
    "santa-ana": "Santa Ana",
    "san-miguel": "San Miguel",
    "sonsonate": "Sonsonate",
    "usulutan": "Usulután",
    "ahuachapan": "Ahuachapán",
    "la-paz": "La Paz",
    "la-union": "La Unión",
    "chalatenango": "Chalatenango",
    "cuscatlan": "Cuscatlán",
    "morazan": "Morazán",
    "san-vicente": "San Vicente",
    "cabanas": "Cabañas",
}

CATEGORY_SLUGS_TO_TYPE = {
    "venta-de-casas": "house",
    "venta-de-apartamentos": "apartment",
    "venta-de-terrenos": "land",
    "venta-de-locales-comerciales": "commercial",
    "venta-de-oficinas": "commercial",
    "venta-de-bodegas": "commercial",
    "alquiler-de-casas": "house",
    "alquiler-de-apartamentos": "apartment",
    "alquiler-de-terrenos": "land",
}


# ── URL Parser ───────────────────────────────────────

@dataclass
class ParsedListingURL:
    """Structured data extracted from an Encuentra24 listing URL."""
    url: str
    listing_id: str = ""
    department: str = ""
    property_type: str = ""
    is_detail_page: bool = False

    @classmethod
    def from_url(cls, url: str) -> ParsedListingURL:
        """
        Parse an Encuentra24 URL and extract metadata from its slug.

        Example URLs:
          https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-casas/casa-en-residencial-san-salvador/18293847
          https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-casas
        """
        parsed = urlparse(url)
        path = unquote(parsed.path).strip("/")
        parts = path.split("/")

        result = cls(url=url)

        # Check for listing ID (numeric at end)
        if parts and re.match(r'^\d{5,}$', parts[-1]):
            result.listing_id = parts[-1]
            result.is_detail_page = True

        # Extract property type from bienes-raices-* slug
        for part in parts:
            if part.startswith("bienes-raices-"):
                category_slug = part.replace("bienes-raices-", "")
                result.property_type = CATEGORY_SLUGS_TO_TYPE.get(
                    category_slug, ""
                )
                break

        # Extract department from URL path
        path_lower = path.lower()
        for slug, name in DEPARTMENT_SLUGS.items():
            if f"/{slug}" in path_lower or f"-{slug}" in path_lower:
                result.department = name
                break

        return result


# ── Layer 1: CSE Discovery ───────────────────────────

# Search queries covering all categories and departments
CSE_QUERIES = [
    # By property type
    "site:encuentra24.com/el-salvador-es bienes raices venta casas",
    "site:encuentra24.com/el-salvador-es bienes raices venta apartamentos",
    "site:encuentra24.com/el-salvador-es bienes raices venta terrenos",
    "site:encuentra24.com/el-salvador-es bienes raices locales comerciales",
    # By major department
    "site:encuentra24.com/el-salvador-es bienes raices San Salvador",
    "site:encuentra24.com/el-salvador-es bienes raices La Libertad",
    "site:encuentra24.com/el-salvador-es bienes raices Santa Ana",
    "site:encuentra24.com/el-salvador-es bienes raices San Miguel",
    "site:encuentra24.com/el-salvador-es bienes raices Sonsonate",
    "site:encuentra24.com/el-salvador-es bienes raices Ahuachapán",
    "site:encuentra24.com/el-salvador-es bienes raices Chalatenango",
    "site:encuentra24.com/el-salvador-es bienes raices La Paz",
    "site:encuentra24.com/el-salvador-es bienes raices Usulután",
    # Price ranges
    "site:encuentra24.com/el-salvador-es venta casa $50,000",
    "site:encuentra24.com/el-salvador-es venta casa $100,000",
    "site:encuentra24.com/el-salvador-es venta casa $200,000",
    "site:encuentra24.com/el-salvador-es venta terreno lote",
    # Long-tail for smaller departments
    "site:encuentra24.com/el-salvador-es bienes raices Cabañas OR Morazán OR La Unión",
    "site:encuentra24.com/el-salvador-es bienes raices Cuscatlán OR San Vicente",
]


class CSEDiscovery:
    """
    Layer 1: Google Custom Search Engine discovery.
    
    Harvests listing URLs + snippet metadata from Google's index
    of Encuentra24 pages.
    """

    SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(
        self,
        api_key: str | None = None,
        cse_id: str | None = None,
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_CSE_API_KEY", "")
        self.cse_id = cse_id or os.environ.get("GOOGLE_CSE_ID", "")
        if not self.api_key or not self.cse_id:
            raise ValueError(
                "Google CSE credentials required. Set GOOGLE_CSE_API_KEY and "
                "GOOGLE_CSE_ID environment variables, or pass them directly."
            )
        self._client: httpx.AsyncClient | None = None
        self._queries_used = 0

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def search(
        self,
        query: str,
        start: int = 1,
        num: int = 10,
    ) -> list[dict]:
        """
        Execute a single CSE search.
        
        Returns raw result items from Google's API.
        Each item has: title, link, snippet, pagemap (if available).
        """
        if not self._client:
            raise RuntimeError("Use 'async with' context manager.")

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "start": start,
            "num": min(num, 10),  # Google CSE max is 10 per request
            "lr": "lang_es",
            "gl": "sv",  # El Salvador geolocation bias
        }

        try:
            resp = await self._client.get(self.SEARCH_URL, params=params)
            self._queries_used += 1
            resp.raise_for_status()
            data = resp.json()

            items = data.get("items", [])
            total = int(
                data.get("searchInformation", {}).get("totalResults", 0)
            )
            logger.info(
                f"  CSE query [{self._queries_used}]: "
                f"'{query[:50]}...' → {len(items)} results "
                f"(~{total} total)"
            )
            return items

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("CSE rate limit hit (100/day free tier)")
                return []
            logger.error(f"CSE API error: {e.response.status_code} {e.response.text[:200]}")
            return []
        except Exception as e:
            logger.error(f"CSE search error: {e}")
            return []

    def parse_result(self, item: dict) -> dict:
        """
        Parse a single CSE result item into our property schema.
        
        Extracts:
          - URL metadata (department, property_type, listing_id)
          - Snippet text → price, bedrooms, bathrooms, area
          - Page metadata from metatags if available
        """
        url = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        
        # Clean up title — remove " | Encuentra24" suffix
        title = re.sub(r'\s*[\|–—-]\s*Encuentra24.*$', '', title).strip()
        
        # Parse URL structure
        parsed = ParsedListingURL.from_url(url)

        record: dict = {
            "title": title,
            "source": "encuentra24",
            "source_url": url,
            "department": parsed.department,
            "property_type": parsed.property_type,
            "listing_id": parsed.listing_id,
            "snippet": snippet,
            "discovery_layer": "cse",
            "needs_enrichment": True,
        }

        # ── Extract data from snippet text ───────────────
        combined = f"{title} {snippet}".lower()

        # Price
        price_match = re.search(
            r'(?:us?\$|usd)\s*([\d,]+(?:\.\d{2})?)', combined
        )
        if not price_match:
            price_match = re.search(
                r'\$([\d,]+(?:\.\d{2})?)', combined
            )
        if price_match:
            try:
                record["price_usd"] = float(
                    price_match.group(1).replace(",", "")
                )
            except ValueError:
                pass

        # Bedrooms
        bed_match = re.search(
            r'(\d+)\s*(?:habitaci[oó]n|rec[aá]mara|dormitorio|bed|hab)', combined
        )
        if bed_match:
            record["bedrooms"] = int(bed_match.group(1))

        # Bathrooms
        bath_match = re.search(
            r'(\d+)\s*(?:ba[ñn]o|bath)', combined
        )
        if bath_match:
            record["bathrooms"] = int(bath_match.group(1))

        # Area
        area_match = re.search(
            r'([\d,.]+)\s*(?:m²|m2|mt2|mts2|metros?\s*cuadrados?)', combined
        )
        if area_match:
            try:
                record["area_m2"] = float(
                    area_match.group(1).replace(",", "")
                )
            except ValueError:
                pass

        # Lot size (terreno)
        lot_match = re.search(
            r'terreno[:\s]*([\d,.]+)\s*(?:m²|m2|v2|varas)', combined
        )
        if lot_match:
            try:
                record["lot_size_m2"] = float(
                    lot_match.group(1).replace(",", "")
                )
            except ValueError:
                pass

        # ── Extract from pagemap metatags (richer) ───────
        pagemap = item.get("pagemap", {})
        metatags = pagemap.get("metatags", [{}])
        if metatags:
            meta = metatags[0]
            og_title = meta.get("og:title", "")
            og_desc = meta.get("og:description", "")
            og_image = meta.get("og:image", "")

            if og_title and not record.get("title"):
                record["title"] = og_title
            if og_desc:
                record["description_es"] = og_desc[:500]
                # Re-parse from OG description (often more structured)
                if not record.get("price_usd"):
                    pm = re.search(r'\$([\d,]+)', og_desc)
                    if pm:
                        try:
                            record["price_usd"] = float(pm.group(1).replace(",", ""))
                        except ValueError:
                            pass
            if og_image:
                record["images"] = [og_image]

        # Extract thumbnail from CSE result
        cse_image = pagemap.get("cse_image", [{}])
        if cse_image and cse_image[0].get("src"):
            img = cse_image[0]["src"]
            if "images" not in record:
                record["images"] = [img]
            elif img not in record["images"]:
                record["images"].insert(0, img)

        # Content hash for dedup
        record["content_hash"] = hashlib.sha256(
            f"encuentra24:{url}".encode()
        ).hexdigest()[:16]

        return record

    async def discover(
        self,
        max_queries: int = 20,
        queries: list[str] | None = None,
    ) -> list[dict]:
        """
        Run discovery across search queries.
        
        Returns deduplicated list of parsed property records.
        """
        if queries is None:
            queries = CSE_QUERIES

        # Limit to budget
        queries = queries[:max_queries]
        
        seen_urls: set[str] = set()
        results: list[dict] = []

        for query in queries:
            # First page
            items = await self.search(query)
            for item in items:
                url = item.get("link", "")
                if url in seen_urls:
                    continue
                # Only keep detail pages (with listing IDs)
                parsed_url = ParsedListingURL.from_url(url)
                if not parsed_url.is_detail_page:
                    continue
                seen_urls.add(url)
                record = self.parse_result(item)
                results.append(record)

            # Pagination: fetch page 2 if first page was full
            if len(items) == 10 and self._queries_used < max_queries:
                items2 = await self.search(query, start=11)
                for item in items2:
                    url = item.get("link", "")
                    if url in seen_urls:
                        continue
                    parsed_url = ParsedListingURL.from_url(url)
                    if not parsed_url.is_detail_page:
                        continue
                    seen_urls.add(url)
                    record = self.parse_result(item)
                    results.append(record)

            # Small pause between queries
            await asyncio.sleep(0.5)

            if self._queries_used >= max_queries:
                logger.info(f"  Reached query budget ({max_queries})")
                break

        logger.info(
            f"Discovery complete: {len(results)} unique listings "
            f"from {self._queries_used} queries"
        )
        return results


# ── Layer 2: Selective Enrichment ────────────────────

# Rotating user agents for stealth
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Referrers that look natural
REFERRERS = [
    "https://www.google.com/",
    "https://www.google.com.sv/",
    "https://www.google.com/search?q=casas+en+venta+el+salvador",
    "https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-casas",
    "",  # Direct visit
]


class ListingEnricher:
    """
    Layer 2: Selective enrichment via targeted HTTP fetches.
    
    Uses rotating headers, random delays, and cookie persistence
    to look like organic browsing. Rate-limited to stay under the radar.
    
    Priority logic: enriches listings that are most valuable to hydrate,
    based on a scoring heuristic (has price but missing details, etc.)
    """

    def __init__(
        self,
        max_per_session: int = 50,
        min_delay: float = 8.0,
        max_delay: float = 25.0,
        cookie_file: Path | None = None,
    ):
        self.max_per_session = max_per_session
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.cookie_file = cookie_file or Path(__file__).parent / "data" / ".e24_cookies.json"
        self._client: httpx.AsyncClient | None = None
        self._enriched = 0

    async def __aenter__(self):
        cookies = self._load_cookies()
        self._client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            cookies=cookies,
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            self._save_cookies()
            await self._client.aclose()

    def _load_cookies(self) -> dict:
        """Load persisted cookies from previous sessions."""
        if self.cookie_file.exists():
            try:
                data = json.loads(self.cookie_file.read_text())
                logger.debug(f"Loaded {len(data)} cookies from {self.cookie_file}")
                return data
            except Exception:
                pass
        return {}

    def _save_cookies(self) -> None:
        """Persist cookies for future sessions."""
        if not self._client:
            return
        try:
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
            cookies = dict(self._client.cookies)
            self.cookie_file.write_text(json.dumps(cookies))
            logger.debug(f"Saved {len(cookies)} cookies")
        except Exception as e:
            logger.debug(f"Could not save cookies: {e}")

    def _random_headers(self) -> dict:
        """Generate randomized but realistic browser headers."""
        ua = random.choice(USER_AGENTS)
        ref = random.choice(REFERRERS)
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-SV,es;q=0.9,en-US;q=0.7,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site" if ref else "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        if ref:
            headers["Referer"] = ref
        return headers

    @staticmethod
    def enrichment_priority(record: dict) -> float:
        """
        Score how much value enrichment would add. Higher = more valuable.
        
        Records with some data but missing key fields benefit most.
        Records with nothing (likely blocked pages) benefit least.
        """
        score = 0.0

        # Has price but missing details → high value
        if record.get("price_usd"):
            score += 2.0
            if not record.get("bedrooms"):
                score += 1.5
            if not record.get("area_m2"):
                score += 1.0
        else:
            score += 0.5  # Even getting a price is valuable

        # Missing description → worth enriching
        if not record.get("description_es"):
            score += 1.5

        # No images → worth it
        if not record.get("images"):
            score += 1.0

        # Has a department → we know where it is → more useful when enriched
        if record.get("department"):
            score += 0.5

        return score

    async def enrich(self, record: dict) -> dict:
        """
        Fetch a listing's detail page and extract full property data.
        
        Returns the record updated with any new fields discovered.
        """
        if not self._client:
            raise RuntimeError("Use 'async with' context manager.")

        url = record.get("source_url", "")
        if not url:
            return record

        # Random delay to simulate human browsing
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"  Waiting {delay:.1f}s before fetch...")
        await asyncio.sleep(delay)

        try:
            resp = await self._client.get(url, headers=self._random_headers())
            self._enriched += 1

            if resp.status_code == 403:
                logger.warning(f"  Blocked (403) on: {url}")
                record["_enrichment_status"] = "blocked"
                return record
            if resp.status_code == 429:
                logger.warning(f"  Rate limited (429). Stopping enrichment.")
                record["_enrichment_status"] = "rate_limited"
                return record
            if resp.status_code != 200:
                logger.warning(f"  HTTP {resp.status_code} for: {url}")
                record["_enrichment_status"] = f"http_{resp.status_code}"
                return record

            html = resp.text

            # Check if we got a real page or a Cloudflare challenge
            if self._is_challenge_page(html):
                logger.warning(f"  Cloudflare challenge detected. Stopping.")
                record["_enrichment_status"] = "cloudflare_challenge"
                return record

            # Parse the HTML for property data
            enriched = self._parse_detail_html(html, record)
            enriched["_enrichment_status"] = "success"
            enriched["needs_enrichment"] = False
            return enriched

        except Exception as e:
            logger.error(f"  Enrichment error for {url}: {e}")
            record["_enrichment_status"] = f"error: {e}"
            return record

    def _is_challenge_page(self, html: str) -> bool:
        """Detect Cloudflare or similar bot challenge pages."""
        indicators = [
            "cf-browser-verification",
            "challenge-platform",
            "jschl_vc",
            "jschl_answer",
            "Checking your browser",
            "cf_chl_opt",
            "turnstile",
            "_cf_chl_tk",
        ]
        html_lower = html.lower()
        return any(ind.lower() in html_lower for ind in indicators)

    def _parse_detail_html(self, html: str, record: dict) -> dict:
        """
        Parse HTML of a listing detail page into structured data.
        
        Uses regex-based extraction (no lxml/BS4 dependency) for the
        most common data patterns on Encuentra24 detail pages.
        """
        enriched = dict(record)

        # ── JSON-LD structured data (most reliable if present) ──
        json_ld_matches = re.findall(
            r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        for json_text in json_ld_matches:
            try:
                data = json.loads(json_text)
                if isinstance(data, dict):
                    self._merge_json_ld(enriched, data)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            self._merge_json_ld(enriched, item)
            except json.JSONDecodeError:
                continue

        # ── Title from <h1> ──
        if not enriched.get("title"):
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
            if h1:
                title = re.sub(r'<[^>]+>', '', h1.group(1)).strip()
                if title:
                    enriched["title"] = title

        # ── Description ──
        if not enriched.get("description_es"):
            desc_patterns = [
                r'class="[^"]*description[^"]*"[^>]*>(.*?)</(?:div|section|p)',
                r'id="description"[^>]*>(.*?)</(?:div|section)',
                r'class="[^"]*detail-desc[^"]*"[^>]*>(.*?)</(?:div|section)',
            ]
            for pattern in desc_patterns:
                dm = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if dm:
                    desc = re.sub(r'<[^>]+>', ' ', dm.group(1)).strip()
                    desc = re.sub(r'\s+', ' ', desc)
                    if len(desc) > 20:
                        enriched["description_es"] = desc[:2000]
                        break

        # ── Price ──
        if not enriched.get("price_usd"):
            price_patterns = [
                r'class="[^"]*price[^"]*"[^>]*>\s*\$?\s*([\d,]+(?:\.\d{2})?)',
                r'data-price="([\d,.]+)"',
                r'"price"\s*:\s*"?([\d,.]+)"?',
            ]
            for pattern in price_patterns:
                pm = re.search(pattern, html, re.IGNORECASE)
                if pm:
                    try:
                        enriched["price_usd"] = float(pm.group(1).replace(",", ""))
                        break
                    except ValueError:
                        continue

        # ── Images ──
        existing_images = enriched.get("images", [])
        img_patterns = [
            r'class="[^"]*(?:gallery|carousel|slider|photo)[^"]*"[^>]*>.*?(?:src|data-src)="(https?://[^"]+\.(?:jpg|jpeg|webp|png))',
            r'"image"\s*:\s*"(https?://[^"]+)"',
            r'og:image"\s+content="(https?://[^"]+)"',
        ]
        for pattern in img_patterns:
            img_urls = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for img_url in img_urls:
                if (
                    img_url not in existing_images
                    and "logo" not in img_url.lower()
                    and "icon" not in img_url.lower()
                    and "avatar" not in img_url.lower()
                ):
                    existing_images.append(img_url)
        enriched["images"] = existing_images[:20]

        # ── Bedrooms / Bathrooms / Area (from text) ──
        html_text = re.sub(r'<[^>]+>', ' ', html)
        html_text_lower = html_text.lower()

        if not enriched.get("bedrooms"):
            bed = re.search(r'(\d+)\s*(?:habitaci[oó]n|rec[aá]mara|dorm|bed|hab)', html_text_lower)
            if bed:
                enriched["bedrooms"] = int(bed.group(1))

        if not enriched.get("bathrooms"):
            bath = re.search(r'(\d+)\s*(?:ba[ñn]o|bath)', html_text_lower)
            if bath:
                enriched["bathrooms"] = int(bath.group(1))

        if not enriched.get("area_m2"):
            area = re.search(r'([\d,.]+)\s*(?:m²|m2|mt2|mts2)', html_text_lower)
            if area:
                try:
                    enriched["area_m2"] = float(area.group(1).replace(",", ""))
                except ValueError:
                    pass

        if not enriched.get("lot_size_m2"):
            lot = re.search(r'terreno[:\s]*([\d,.]+)\s*(?:m²|m2|v2|varas)', html_text_lower)
            if lot:
                try:
                    enriched["lot_size_m2"] = float(lot.group(1).replace(",", ""))
                except ValueError:
                    pass

        # ── Coordinates from embedded map ──
        if not enriched.get("latitude"):
            coord_patterns = [
                r'data-lat="([-\d.]+)"[^>]*data-lng="([-\d.]+)"',
                r'"latitude"\s*:\s*([-\d.]+)\s*,\s*"longitude"\s*:\s*([-\d.]+)',
                r'@([-\d.]+),([-\d.]+)',
                r'q=([-\d.]+),([-\d.]+)',
            ]
            for pattern in coord_patterns:
                cm = re.search(pattern, html)
                if cm:
                    lat = float(cm.group(1))
                    lng = float(cm.group(2))
                    # Validate within El Salvador bounds
                    if 13.0 <= lat <= 14.5 and -90.2 <= lng <= -87.5:
                        enriched["latitude"] = lat
                        enriched["longitude"] = lng
                        break

        # ── Features list ──
        if not enriched.get("features"):
            features = []
            feat_patterns = [
                r'class="[^"]*(?:attribute|feature|spec)[^"]*"[^>]*>\s*<li[^>]*>(.*?)</li>',
                r'class="[^"]*(?:attribute|feature|spec)[^"]*"[^>]*>(.*?)</(?:div|span)',
            ]
            for pattern in feat_patterns:
                feats = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
                for f in feats:
                    text = re.sub(r'<[^>]+>', '', f).strip()
                    if text and len(text) < 100:
                        features.append(text)
            if features:
                enriched["features"] = features

        # ── Location from breadcrumbs ──
        if not enriched.get("department"):
            breadcrumb_text = ""
            bc = re.search(
                r'class="[^"]*breadcrumb[^"]*"[^>]*>(.*?)</(?:nav|ol|ul|div)',
                html, re.DOTALL | re.IGNORECASE,
            )
            if bc:
                breadcrumb_text = re.sub(r'<[^>]+>', ' ', bc.group(1)).lower()
            for slug, name in DEPARTMENT_SLUGS.items():
                if name.lower() in breadcrumb_text:
                    enriched["department"] = name
                    break

        return enriched

    def _merge_json_ld(self, record: dict, data: dict) -> None:
        """Merge JSON-LD structured data into the record."""
        ld_type = data.get("@type", "")
        if ld_type not in ("Product", "RealEstateListing", "Offer", "Place", "Residence"):
            return

        if data.get("name") and not record.get("title"):
            record["title"] = data["name"]

        if data.get("description") and not record.get("description_es"):
            record["description_es"] = data["description"][:2000]

        if data.get("image") and not record.get("images"):
            imgs = data["image"]
            if isinstance(imgs, str):
                imgs = [imgs]
            record["images"] = imgs[:20]

        offers = data.get("offers", {})
        if isinstance(offers, dict) and offers.get("price"):
            if not record.get("price_usd"):
                try:
                    record["price_usd"] = float(offers["price"])
                except (ValueError, TypeError):
                    pass

        geo = data.get("geo", {})
        if isinstance(geo, dict):
            lat = geo.get("latitude")
            lng = geo.get("longitude")
            if lat and lng and not record.get("latitude"):
                try:
                    record["latitude"] = float(lat)
                    record["longitude"] = float(lng)
                except (ValueError, TypeError):
                    pass

    async def enrich_batch(
        self,
        records: list[dict],
        max_enrichments: int | None = None,
    ) -> list[dict]:
        """
        Enrich a batch of records, prioritized by enrichment value.
        
        Returns all records (enriched and unenriched).
        """
        limit = max_enrichments or self.max_per_session

        # Sort by enrichment priority (highest first)
        prioritized = sorted(
            range(len(records)),
            key=lambda i: self.enrichment_priority(records[i]),
            reverse=True,
        )

        enriched_count = 0
        blocked = False

        for idx in prioritized:
            if enriched_count >= limit or blocked:
                break

            record = records[idx]
            if not record.get("needs_enrichment", True):
                continue

            logger.info(
                f"  Enriching [{enriched_count + 1}/{limit}]: "
                f"{record.get('title', 'Unknown')[:50]}..."
            )

            enriched = await self.enrich(record)
            records[idx] = enriched

            status = enriched.get("_enrichment_status", "")
            if status in ("cloudflare_challenge", "rate_limited"):
                logger.warning(f"  Enrichment halted: {status}")
                blocked = True
            elif status == "success":
                enriched_count += 1

        logger.info(
            f"Enrichment complete: {enriched_count} successful "
            f"out of {limit} attempted"
        )
        return records


# ── Integrated Scraper ───────────────────────────────

class Encuentra24CSEScraper(BaseScraper):
    """
    Full two-layer scraper combining CSE discovery + selective enrichment.
    
    Implements BaseScraper interface so it plugs into run.py CLI.
    """

    source_name = "encuentra24"
    base_url = "https://www.encuentra24.com"
    requests_per_second = 0.1  # Very conservative for enrichment

    def __init__(
        self,
        api_key: str | None = None,
        cse_id: str | None = None,
        max_queries: int = 20,
        max_enrichments: int = 50,
        enrich: bool = True,
    ):
        super().__init__()
        self.api_key = api_key
        self.cse_id = cse_id
        self.max_queries = max_queries
        self.max_enrichments = max_enrichments
        self.do_enrich = enrich

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 10,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """
        Two-layer pipeline: discover via CSE, then enrich.
        """
        # ── Layer 1: Discovery ──
        queries = CSE_QUERIES
        if department:
            # Focus queries on the target department
            queries = [
                f"site:encuentra24.com/el-salvador-es bienes raices {department} casas",
                f"site:encuentra24.com/el-salvador-es bienes raices {department} apartamentos",
                f"site:encuentra24.com/el-salvador-es bienes raices {department} terrenos",
                f"site:encuentra24.com/el-salvador-es venta {department}",
            ]

        async with CSEDiscovery(self.api_key, self.cse_id) as cse:
            records = await cse.discover(
                max_queries=self.max_queries,
                queries=queries,
            )

        if not records:
            logger.warning("No listings discovered via CSE.")
            return

        logger.info(f"Layer 1 discovered {len(records)} listings")

        # ── Layer 2: Enrichment ──
        if self.do_enrich and self.max_enrichments > 0:
            logger.info(f"Layer 2: enriching up to {self.max_enrichments} listings...")
            async with ListingEnricher(max_per_session=self.max_enrichments) as enricher:
                records = await enricher.enrich_batch(records, self.max_enrichments)

        # ── Convert to ScrapedProperty and yield ──
        for record in records:
            prop = self._to_scraped_property(record)
            if prop and prop.source_url not in self._seen_urls:
                self._seen_urls.add(prop.source_url)
                yield prop

    def _to_scraped_property(self, record: dict) -> ScrapedProperty | None:
        """Convert a CSE record dict to ScrapedProperty."""
        url = record.get("source_url", "")
        title = record.get("title", "")
        if not url and not title:
            return None

        return ScrapedProperty(
            title=title or "Propiedad en El Salvador",
            source=self.source_name,
            source_url=url,
            department=record.get("department", ""),
            municipio=record.get("municipio", ""),
            address=record.get("address", ""),
            latitude=record.get("latitude"),
            longitude=record.get("longitude"),
            price_usd=record.get("price_usd"),
            price_raw=record.get("price_raw", ""),
            property_type=record.get("property_type", ""),
            bedrooms=record.get("bedrooms"),
            bathrooms=record.get("bathrooms"),
            area_m2=record.get("area_m2"),
            lot_size_m2=record.get("lot_size_m2"),
            description_es=record.get("description_es", ""),
            images=record.get("images", []),
            features=record.get("features", []),
        )


# ── Standalone CLI (for testing without run.py) ──────

async def main():
    """Quick standalone test."""
    import argparse

    parser = argparse.ArgumentParser(description="Encuentra24 CSE Pipeline")
    parser.add_argument("--api-key", help="Google CSE API key (or GOOGLE_CSE_API_KEY env)")
    parser.add_argument("--cse-id", help="Google CSE ID (or GOOGLE_CSE_ID env)")
    parser.add_argument("--max-queries", type=int, default=10, help="Max CSE queries (default: 10)")
    parser.add_argument("--max-enrich", type=int, default=0, help="Max pages to enrich (default: 0 = skip)")
    parser.add_argument("--output", "-o", default="data/scraper_output", help="Output directory")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    scraper = Encuentra24CSEScraper(
        api_key=args.api_key,
        cse_id=args.cse_id,
        max_queries=args.max_queries,
        max_enrichments=args.max_enrich,
        enrich=args.max_enrich > 0,
    )

    result = ScrapeResult(
        source="encuentra24",
        department=None,
        municipio=None,
        started_at=datetime.utcnow(),
    )

    async with scraper:
        async for prop in scraper.scrape_listings():
            result.properties.append(prop)
            result.total_found += 1
            result.total_new += 1

    result.finished_at = datetime.utcnow()

    # Save
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filepath = output_dir / f"encuentra24_cse_{timestamp}.jsonl"

    with open(filepath, "w", encoding="utf-8") as f:
        for prop in result.properties:
            f.write(json.dumps(prop.to_dict(), ensure_ascii=False) + "\n")

    print(f"\nResults: {result.total_found} listings in {result.duration_seconds:.1f}s")
    print(f"Saved to: {filepath}")

    # Quick stats
    with_price = sum(1 for p in result.properties if p.has_price)
    with_desc = sum(1 for p in result.properties if p.description_es)
    with_imgs = sum(1 for p in result.properties if p.has_images)
    with_beds = sum(1 for p in result.properties if p.bedrooms is not None)
    print(f"  With price:       {with_price}/{result.total_found}")
    print(f"  With description: {with_desc}/{result.total_found}")
    print(f"  With images:      {with_imgs}/{result.total_found}")
    print(f"  With bedrooms:    {with_beds}/{result.total_found}")


if __name__ == "__main__":
    asyncio.run(main())
