"""
Encuentra24 El Salvador — AJAX API Scraper
==========================================
Scrapes property listings from Encuentra24's internal AJAX endpoint.

The site is server-rendered with jQuery + React hybrid, and listings are
loaded via an AJAX endpoint at:
    /el-salvador-en/ajax/real-estate-for-sale?page=N

This returns JSON with an HTML `listing` field containing ad tiles
with structured data attributes (data-adid, data-price, etc.) and
embedded ga4addata analytics objects with category/location metadata.

Verified counts (Feb 2026):
    - For sale: ~2,551 listings (86 pages × 30)
    - For rent: ~1,080 listings (37 pages × 30)
    - Total: ~3,600 listings

Legal basis:
    - Public website, no login required
    - Factual data (prices, locations, property specs) not copyrightable
    - Rate-limited to 0.4 req/sec (well below human browsing speed)
    - Respects robots.txt (these endpoints not disallowed)

Usage:
    python -m data.scrapers.encuentra24_ajax
    # or via run.py:
    python run.py encuentra24-ajax --max-pages 86 -o data/scraper_output
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import AsyncGenerator

import httpx

from base import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)

# ── Department mapping (URL slug → canonical name) ───

DEPARTMENT_MAP = {
    "ahuachapan": "Ahuachapán",
    "cabanas": "Cabañas",
    "chalatenango": "Chalatenango",
    "cuscatlan": "Cuscatlán",
    "la-libertad": "La Libertad",
    "la-paz": "La Paz",
    "la-union": "La Unión",
    "morazan": "Morazán",
    "san-miguel": "San Miguel",
    "san-salvador": "San Salvador",
    "san-vicente": "San Vicente",
    "santa-ana": "Santa Ana",
    "sonsonate": "Sonsonate",
    "usulutan": "Usulután",
}

# ── Property type mapping ────────────────────────────

PROPERTY_TYPE_MAP = {
    "houses-homes": "house",
    "apartments": "apartment",
    "lots-land": "land",
    "commercial": "commercial",
    "offices": "commercial",
    "farms-ranches": "land",
    "beach-properties": "house",
    "buildings": "commercial",
}

# ── Subcategories to scrape ──────────────────────────

CATEGORIES = [
    ("real-estate-for-sale", "sale"),
    ("real-estate-for-rent", "rent"),
]


class Encuentra24AjaxScraper(BaseScraper):
    """
    Scrapes Encuentra24 El Salvador via their internal AJAX API.
    No headless browser needed — the AJAX endpoint returns JSON
    with server-rendered HTML containing all listing data.
    """

    source_name = "encuentra24"
    base_url = "https://www.encuentra24.com"
    requests_per_second = 0.4  # ~2.5s between requests
    max_retries = 3
    timeout = 30.0

    def __init__(self, include_rentals: bool = False):
        super().__init__()
        self.include_rentals = include_rentals

    async def __aenter__(self):
        """Create HTTP client with browser-like headers for AJAX requests."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        return self

    async def _fetch_ajax_page(
        self, category: str, page: int
    ) -> dict | None:
        """
        Fetch a single page from the AJAX endpoint.
        Returns parsed JSON or None on failure.
        """
        url = f"{self.base_url}/el-salvador-en/ajax/{category}?page={page}"
        await self.rate_limiter.acquire()

        for attempt in range(1, self.max_retries + 1):
            try:
                if not self._client:
                    raise RuntimeError("Client not initialized")

                # Set Referer for this specific category
                resp = await self._client.get(
                    url,
                    headers={
                        "Referer": f"{self.base_url}/el-salvador-en/{category}",
                    },
                )
                resp.raise_for_status()

                data = resp.json()
                return data

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2 ** attempt * 5
                    logger.warning(f"Rate limited, waiting {wait}s")
                    await asyncio.sleep(wait)
                elif e.response.status_code >= 500:
                    logger.warning(
                        f"Server error {e.response.status_code}, retry {attempt}"
                    )
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"HTTP {e.response.status_code} for page {page}")
                    return None
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"JSON decode error on page {page}: {e}")
                return None
            except httpx.RequestError as e:
                logger.warning(f"Request error page {page}: {e}, retry {attempt}")
                await asyncio.sleep(2 ** attempt)

        logger.error(f"Failed after {self.max_retries} retries: page {page}")
        return None

    @staticmethod
    def _strip_province_prefix(province: str) -> str:
        """Strip locale prefix from province slug (handles both en/es)."""
        # Handles: "el-salvador-en-la-libertad", "el-salvador-es-la-paz"
        province = re.sub(r'^el-salvador-e[ns]-', '', province)
        return province

    def _parse_listing_html(
        self, html: str, category_slug: str, listing_type: str
    ) -> list[ScrapedProperty]:
        """
        Parse the HTML listing string from the AJAX response.

        Strategy:
        1. Extract ga4addata analytics (province, location, subcategory)
        2. Split HTML into per-tile chunks using data-adid boundaries
        3. For each tile, extract: price, URL, images, title, location,
           and detail items (beds/baths/area via SVG sprite icons)
        """
        properties = []

        # ── Extract ga4addata analytics objects ──
        ga4_data: dict[str, dict] = {}
        for m in re.finditer(
            r'ga4addata\[(\d+)\]\s*=\s*(\{[^}]+\})', html
        ):
            ad_id = m.group(1)
            try:
                obj = json.loads(m.group(2))
                ga4_data[ad_id] = obj
            except json.JSONDecodeError:
                pass

        # ── Split HTML into per-tile chunks ──
        # Each tile starts with data-adid="NNNNN"
        tile_starts = [
            (m.start(), m.group(1))
            for m in re.finditer(r'data-adid="(\d+)"\s+data-price="(\d+)"', html)
        ]
        # Deduplicate — data-adid appears twice per tile (in fav link + tile root)
        seen_ids: set[str] = set()
        unique_starts: list[tuple[int, str]] = []
        for pos, ad_id in tile_starts:
            if ad_id not in seen_ids:
                seen_ids.add(ad_id)
                unique_starts.append((pos, ad_id))

        for idx, (start_pos, ad_id) in enumerate(unique_starts):
            # Determine tile chunk boundaries
            end_pos = unique_starts[idx + 1][0] if idx + 1 < len(unique_starts) else len(html)
            tile = html[start_pos:end_pos]

            # ── Price ──
            price_m = re.search(r'data-price="(\d+)"', tile)
            price_str = price_m.group(1) if price_m else ""
            try:
                price_usd = float(price_str) if price_str else None
            except ValueError:
                price_usd = None

            # ── Detail URL ──
            url_m = re.search(
                r'href="(/el-salvador-en/(?:real-estate[^"]*?)/(\d+))"', tile
            )
            url_path = url_m.group(1) if url_m else f"/el-salvador-en/{category_slug}/{ad_id}"
            full_url = f"{self.base_url}{url_path}"

            # ── Images ──
            # Featured listings use data-src in carousel; regular use data-original
            images = []
            for img_m in re.finditer(
                r'(?:data-src|data-original)="(https://photos\.encuentra24\.com/[^"]+)"', tile
            ):
                img_url = img_m.group(1)
                # Skip seal/badge images
                if "cnseal" in img_url or "badge" in img_url:
                    continue
                if img_url not in images:
                    images.append(img_url)

            # ── Title ──
            title_m = re.search(r'd3-ad-tile__title[^>]*>\s*([^<]+?)\s*<', tile)
            if not title_m:
                title_m = re.search(r'd3-ad-tile__short-description[^>]*>\s*([^<]+?)\s*<', tile)
            title = title_m.group(1).strip() if title_m else ""
            if not title:
                # Generate from URL slug
                parts = url_path.rstrip("/").split("/")
                slug = parts[-2] if len(parts) >= 2 else ""
                title = slug.replace("-", " ").title()

            # ── Location text ──
            loc_m = re.search(r'd3-ad-tile__location[^>]*>.*?</svg>\s*([^<]+?)\s*<', tile, re.S)
            address = loc_m.group(1).strip() if loc_m else ""

            # ── Detail items (beds, baths, area, parking) via SVG sprites ──
            bedrooms = None
            bathrooms = None
            area_m2 = None
            features = []
            for det_m in re.finditer(
                r'd3-ad-tile__details-item[^>]*>.*?#(\w+)".*?</svg>\s*([\d,.]+)\s*(?:m<sup>2</sup>)?\s*</li>',
                tile, re.S
            ):
                sprite = det_m.group(1)    # "bed", "bath", "resize", "parking"
                value_str = det_m.group(2) # "3", "2.5", "610"
                has_m2 = "m<sup>2</sup>" in det_m.group(0)
                try:
                    value = float(value_str.replace(",", ""))
                except ValueError:
                    continue

                if sprite == "bed":
                    bedrooms = int(value)
                    features.append(f"{int(value)} bed")
                elif sprite == "bath":
                    bathrooms = value if value != int(value) else int(value)
                    features.append(f"{value} bath")
                elif sprite == "resize" and has_m2:
                    area_m2 = value
                    features.append(f"{value} m²")
                elif sprite == "parking":
                    features.append(f"{int(value)} parking")

            # ── Department / Municipio from ga4 data ──
            department = ""
            municipio = ""
            ga4 = ga4_data.get(ad_id, {})
            if ga4:
                province = ga4.get("province", "")
                location = ga4.get("location", "")
                dept_slug = self._strip_province_prefix(province)
                department = DEPARTMENT_MAP.get(
                    dept_slug, dept_slug.replace("-", " ").title()
                )
                # location: "el-salvador-en-la-libertad-la-libertad"
                loc_slug = self._strip_province_prefix(location)
                muni_slug = loc_slug.replace(f"{dept_slug}-", "", 1)
                municipio = muni_slug.replace("-", " ").title() if muni_slug else ""

            # ── Property type from subcategory ──
            property_type = ""
            subcategory = ga4.get("subcategory", "")
            if subcategory:
                for key, ptype in PROPERTY_TYPE_MAP.items():
                    if key in subcategory:
                        property_type = ptype
                        break
            if not property_type:
                for key, ptype in PROPERTY_TYPE_MAP.items():
                    if key in url_path:
                        property_type = ptype
                        break

            prop = ScrapedProperty(
                title=title,
                source=self.source_name,
                source_url=full_url,
                department=department,
                municipio=municipio,
                address=address,
                price_usd=price_usd,
                price_currency="USD",
                price_raw=f"US${price_str}" if price_str else "",
                property_type=property_type,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                area_m2=area_m2,
                images=images,
                features=features,
                listing_date=None,
                scraped_at=datetime.utcnow(),
            )
            properties.append(prop)

        return properties

    def _get_max_page(self, html: str) -> int:
        """Extract the maximum page number from pagination in listing HTML."""
        pages = [
            int(m.group(1))
            for m in re.finditer(r'data-page="(\d+)"', html)
        ]
        return max(pages) if pages else 1

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 100,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """
        Scrape all Encuentra24 property listings via AJAX API.
        Automatically discovers total pages and paginates through all results.
        """
        categories = CATEGORIES if self.include_rentals else [CATEGORIES[0]]

        for category_slug, listing_type in categories:
            logger.info(f"Scraping Encuentra24 [{listing_type}]...")

            # Fetch first page to discover total pages
            data = await self._fetch_ajax_page(category_slug, page=1)
            if not data or "listing" not in data:
                logger.error(f"No data for {category_slug}")
                continue

            listing_html = data["listing"]
            total_pages = min(self._get_max_page(listing_html), max_pages)
            logger.info(
                f"  {category_slug}: {total_pages} pages to scrape"
            )

            # Parse first page
            props = self._parse_listing_html(
                listing_html, category_slug, listing_type
            )
            for prop in props:
                # Filter by department if specified
                if department and prop.department.lower() != department.lower():
                    continue
                if municipio and prop.municipio.lower() != municipio.lower():
                    continue
                yield prop

            logger.info(f"  Page 1/{total_pages}: {len(props)} listings")

            # Paginate through remaining pages
            for page in range(2, total_pages + 1):
                data = await self._fetch_ajax_page(category_slug, page=page)
                if not data or "listing" not in data:
                    logger.warning(f"  Page {page} returned no data, stopping")
                    break

                listing_html = data["listing"]
                props = self._parse_listing_html(
                    listing_html, category_slug, listing_type
                )

                if not props:
                    logger.info(f"  Page {page}: no listings, end of results")
                    break

                for prop in props:
                    if department and prop.department.lower() != department.lower():
                        continue
                    if municipio and prop.municipio.lower() != municipio.lower():
                        continue
                    yield prop

                logger.info(f"  Page {page}/{total_pages}: {len(props)} listings")

        logger.info("Encuentra24 AJAX scrape complete")


# ── CLI entry point ──────────────────────────────────


async def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape Encuentra24 El Salvador via AJAX API"
    )
    parser.add_argument(
        "--max-pages", type=int, default=100,
        help="Max pages per category (default: 100, ~86 pages for all sales)"
    )
    parser.add_argument(
        "--include-rentals", action="store_true",
        help="Also scrape rental listings (adds ~37 more pages)"
    )
    parser.add_argument(
        "--department", "-d", type=str, default=None,
        help="Filter by department name"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="data/scraper_output",
        help="Output directory for JSONL files"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    scraper = Encuentra24AjaxScraper(include_rentals=args.include_rentals)
    result = await scraper.run(
        department=args.department,
        max_pages=args.max_pages,
        output_dir=args.output,
    )

    print(f"\n{'='*60}")
    print(f"Encuentra24 AJAX Scrape Results")
    print(f"{'='*60}")
    print(f"Total listings: {result.total_found}")
    print(f"Duration: {result.duration_seconds:.1f}s")
    print(f"Errors: {result.total_errors}")

    if result.properties:
        # Stats
        with_price = sum(1 for p in result.properties if p.has_price)
        with_images = sum(1 for p in result.properties if p.has_images)
        avg_quality = sum(p.quality_score for p in result.properties) / len(result.properties)

        depts = {}
        types = {}
        for p in result.properties:
            depts[p.department] = depts.get(p.department, 0) + 1
            types[p.property_type or "unknown"] = types.get(p.property_type or "unknown", 0) + 1

        print(f"\nWith price: {with_price} ({100*with_price/len(result.properties):.0f}%)")
        print(f"With images: {with_images} ({100*with_images/len(result.properties):.0f}%)")
        print(f"Avg quality: {avg_quality:.2f}")

        print(f"\nBy department:")
        for dept, count in sorted(depts.items(), key=lambda x: -x[1]):
            print(f"  {dept or 'Unknown'}: {count}")

        print(f"\nBy property type:")
        for ptype, count in sorted(types.items(), key=lambda x: -x[1]):
            print(f"  {ptype}: {count}")

        if result.properties:
            prices = [p.price_usd for p in result.properties if p.price_usd and p.price_usd > 0]
            if prices:
                print(f"\nPrice range: ${min(prices):,.0f} – ${max(prices):,.0f}")
                print(f"Median price: ${sorted(prices)[len(prices)//2]:,.0f}")


if __name__ == "__main__":
    asyncio.run(main())
