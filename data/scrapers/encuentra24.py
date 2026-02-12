"""
Encuentra24 El Salvador — Property Scraper
=============================================
Scrapes real estate listings from encuentra24.com/el-salvador-es
using Playwright for JavaScript-rendered content.

URL patterns:
  - Houses:      /el-salvador-es/bienes-raices-venta-de-casas
  - Apartments:  /el-salvador-es/bienes-raices-venta-de-apartamentos
  - Land:        /el-salvador-es/bienes-raices-venta-de-terrenos
  - Commercial:  /el-salvador-es/bienes-raices-venta-de-locales-comerciales
  - Offices:     /el-salvador-es/bienes-raices-venta-de-oficinas
  - Rentals:     /el-salvador-es/bienes-raices-alquiler-de-*
  Pagination: ?o=1, ?o=2, ...
  
Respects robots.txt — only scrapes allowed listing/detail pages.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import AsyncGenerator
from urllib.parse import urljoin

from base import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)

# ── Department mapping (Encuentra24 slugs → canonical names) ──

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

CATEGORY_SLUGS = {
    "house": "bienes-raices-venta-de-casas",
    "apartment": "bienes-raices-venta-de-apartamentos",
    "land": "bienes-raices-venta-de-terrenos",
    "commercial": "bienes-raices-venta-de-locales-comerciales",
    "office": "bienes-raices-venta-de-oficinas",
    "warehouse": "bienes-raices-venta-de-bodegas",
}

# Map category slugs back to our property_type
SLUG_TO_TYPE = {
    "bienes-raices-venta-de-casas": "house",
    "bienes-raices-venta-de-apartamentos": "apartment",
    "bienes-raices-venta-de-terrenos": "land",
    "bienes-raices-venta-de-locales-comerciales": "commercial",
    "bienes-raices-venta-de-oficinas": "commercial",
    "bienes-raices-venta-de-bodegas": "commercial",
    "bienes-raices-alquiler-de-casas": "house",
    "bienes-raices-alquiler-de-apartamentos": "apartment",
}


class Encuentra24Scraper(BaseScraper):
    """
    Scrapes property listings from Encuentra24 El Salvador.
    
    Uses Playwright to render JavaScript-heavy pages, then extracts
    listing data from the rendered DOM or embedded JSON-LD / data attributes.
    """

    source_name = "encuentra24"
    base_url = "https://www.encuentra24.com"
    requests_per_second = 0.3  # ~1 request every 3 seconds (very conservative)
    max_retries = 3
    timeout = 45.0

    # Playwright-specific settings
    headless = True
    page_load_timeout = 30_000  # ms
    viewport = {"width": 1280, "height": 900}

    def __init__(self):
        super().__init__()
        self._browser = None
        self._playwright = None
        self._page = None

    async def __aenter__(self):
        """Initialize Playwright browser alongside httpx client."""
        await super().__aenter__()
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ]
            )
            logger.info("Playwright browser launched")
        except ImportError:
            logger.warning(
                "Playwright not installed. Install with: "
                "pip install playwright && python -m playwright install chromium"
            )
            raise
        return self

    async def __aexit__(self, *args):
        """Close browser and Playwright."""
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        await super().__aexit__(*args)

    async def _new_page(self):
        """Create a new browser page with stealth settings."""
        context = await self._browser.new_context(
            viewport=self.viewport,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ),
            locale="es-SV",
        )
        page = await context.new_page()
        page.set_default_timeout(self.page_load_timeout)

        # Block unnecessary resources to speed up loading
        await page.route(
            "**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,ttf,otf}",
            lambda route: route.abort(),
        )
        await page.route(
            re.compile(r"(google-analytics|facebook|doubleclick|adsense|adservice|creativecdn)"),
            lambda route: route.abort(),
        )

        return page

    def _build_listing_url(
        self,
        category: str = "house",
        department: str | None = None,
        page_num: int = 1,
    ) -> str:
        """Build a listing page URL."""
        slug = CATEGORY_SLUGS.get(category, CATEGORY_SLUGS["house"])
        url = f"{self.base_url}/el-salvador-es/{slug}"
        
        if department:
            # Encuentra24 uses department slugs in URL for filtering
            dept_slug = None
            for slug_key, name in DEPARTMENT_SLUGS.items():
                if name.lower() == department.lower():
                    dept_slug = slug_key
                    break
            if dept_slug:
                url += f"/{dept_slug}"
        
        if page_num > 1:
            url += f"?o={page_num}"
        
        return url

    async def _extract_listings_from_page(self, page) -> list[dict]:
        """
        Extract listing data from a rendered Encuentra24 search results page.
        
        Encuentra24 typically embeds listing data as:
        1. JSON-LD structured data in <script type="application/ld+json">
        2. Data attributes on listing card elements
        3. Or in JavaScript variables / __NEXT_DATA__ / window.__data
        """
        listings = []

        # Strategy 1: Try to find JSON-LD structured data
        try:
            json_ld_scripts = await page.query_selector_all(
                'script[type="application/ld+json"]'
            )
            for script in json_ld_scripts:
                text = await script.inner_text()
                try:
                    data = json.loads(text)
                    if isinstance(data, dict) and data.get("@type") == "ItemList":
                        for item in data.get("itemListElement", []):
                            if "item" in item:
                                listings.append(item["item"])
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("@type") in (
                                "Product", "RealEstateListing", "Offer", "Place"
                            ):
                                listings.append(item)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.debug(f"JSON-LD extraction failed: {e}")

        # Strategy 2: Try embedded JavaScript data (window.__data, __NEXT_DATA__, etc.)
        if not listings:
            try:
                data = await page.evaluate("""
                    () => {
                        // Check for common embedded data patterns
                        if (window.__NEXT_DATA__) return window.__NEXT_DATA__;
                        if (window.__data) return window.__data;
                        if (window.__INITIAL_STATE__) return window.__INITIAL_STATE__;
                        if (window.pageData) return window.pageData;
                        if (window.searchResults) return window.searchResults;
                        return null;
                    }
                """)
                if data:
                    listings = self._parse_embedded_data(data)
            except Exception as e:
                logger.debug(f"Embedded data extraction failed: {e}")

        # Strategy 3: Parse listing cards from the DOM (most reliable fallback)
        if not listings:
            listings = await self._parse_listing_cards(page)

        return listings

    def _parse_embedded_data(self, data: dict) -> list[dict]:
        """Parse listings from embedded JavaScript data."""
        listings = []

        # Navigate nested structures looking for listing arrays
        def find_listings(obj, depth=0):
            if depth > 5:
                return
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and any(
                        k in item for k in ("price", "titulo", "title", "ubicacion", "location")
                    ):
                        listings.append(item)
                    elif isinstance(item, dict):
                        find_listings(item, depth + 1)
            elif isinstance(obj, dict):
                for key, val in obj.items():
                    if key in ("listings", "results", "items", "ads", "anuncios", "data"):
                        find_listings(val, depth + 1)
                    elif isinstance(val, (dict, list)):
                        find_listings(val, depth + 1)

        find_listings(data)
        return listings

    async def _parse_listing_cards(self, page) -> list[dict]:
        """Parse listing cards from the rendered DOM."""
        listings = []

        # Encuentra24 typically uses listing card components
        # Try multiple CSS selectors that Encuentra24 has used historically
        card_selectors = [
            "div[class*='listing-card']",
            "div[class*='ann-box']",
            "div[class*='result-item']",
            "div[class*='classified-item']",
            "article[class*='listing']",
            "a[class*='listing']",
            "div[data-listing-id]",
            "div[data-ad-id]",
            ".lc-data",
            ".lc-item",
            "[data-qa='listing-card']",
            ".search-result-item",
        ]

        cards = []
        for selector in card_selectors:
            cards = await page.query_selector_all(selector)
            if cards:
                logger.debug(f"Found {len(cards)} cards with selector: {selector}")
                break

        if not cards:
            # Last resort: look for any <a> tags pointing to listing detail pages
            all_links = await page.query_selector_all("a[href]")
            for link in all_links:
                href = await link.get_attribute("href") or ""
                # Encuentra24 detail pages have a numeric ID pattern  
                if re.search(r'/el-salvador-es/bienes-raices-.*/\d+', href):
                    text = await link.inner_text()
                    listings.append({
                        "url": href if href.startswith("http") else urljoin(self.base_url, href),
                        "title": text.strip()[:200] if text else "",
                        "_needs_detail_fetch": True,
                    })
            return listings

        for card in cards:
            try:
                listing = {}

                # Extract URL
                link = await card.query_selector("a[href]")
                if link:
                    href = await link.get_attribute("href") or ""
                    listing["url"] = (
                        href if href.startswith("http")
                        else urljoin(self.base_url, href)
                    )

                # Extract title
                for sel in ["h2", "h3", ".title", "[class*='title']", "a"]:
                    el = await card.query_selector(sel)
                    if el:
                        text = await el.inner_text()
                        if text and len(text.strip()) > 5:
                            listing["title"] = text.strip()
                            break

                # Extract price
                for sel in [
                    "[class*='price']", ".price", "span[class*='amount']",
                    "[data-price]", ".lc-price",
                ]:
                    el = await card.query_selector(sel)
                    if el:
                        text = await el.inner_text()
                        if text:
                            listing["price_raw"] = text.strip()
                            price_match = re.search(r'[\$]?\s*([\d,]+(?:\.\d{2})?)', text)
                            if price_match:
                                listing["price_usd"] = float(
                                    price_match.group(1).replace(",", "")
                                )
                        break

                # Extract location
                for sel in [
                    "[class*='location']", ".location", "[class*='address']",
                    "[class*='ubicacion']", ".lc-address",
                ]:
                    el = await card.query_selector(sel)
                    if el:
                        text = await el.inner_text()
                        if text:
                            listing["location_text"] = text.strip()
                        break

                # Extract features (bedrooms, bathrooms, area)
                for sel in [
                    "[class*='feature']", "[class*='attribute']",
                    "[class*='detail']", ".lc-detail", ".lc-feature",
                ]:
                    els = await card.query_selector_all(sel)
                    for el in els:
                        text = (await el.inner_text()).strip().lower()
                        # Bedrooms
                        bed_match = re.search(r'(\d+)\s*(?:hab|rec|bed|dorm)', text)
                        if bed_match:
                            listing["bedrooms"] = int(bed_match.group(1))
                        # Bathrooms
                        bath_match = re.search(r'(\d+)\s*(?:ba[ñn]|bath)', text)
                        if bath_match:
                            listing["bathrooms"] = int(bath_match.group(1))
                        # Area
                        area_match = re.search(r'([\d,.]+)\s*(?:m²|m2|mts)', text)
                        if area_match:
                            listing["area_m2"] = float(
                                area_match.group(1).replace(",", "")
                            )

                # Extract image
                img = await card.query_selector("img[src]")
                if img:
                    src = await img.get_attribute("src") or ""
                    if src and not src.startswith("data:"):
                        listing["image"] = (
                            src if src.startswith("http")
                            else urljoin(self.base_url, src)
                        )

                if listing.get("url") or listing.get("title"):
                    listings.append(listing)

            except Exception as e:
                logger.debug(f"Error parsing card: {e}")
                continue

        return listings

    async def _fetch_detail_page(self, url: str) -> dict:
        """Fetch a single listing's detail page for full data extraction."""
        await self.rate_limiter.acquire()
        
        page = await self._new_page()
        detail = {"url": url}

        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)  # Wait for dynamic content

            # Extract title
            for sel in ["h1", "[class*='title']", ".ad-title"]:
                el = await page.query_selector(sel)
                if el:
                    text = await el.inner_text()
                    if text and len(text.strip()) > 3:
                        detail["title"] = text.strip()
                        break

            # Extract price
            for sel in [
                "[class*='price']", ".price", "h2[class*='price']",
                "[data-price]",
            ]:
                el = await page.query_selector(sel)
                if el:
                    text = await el.inner_text()
                    if text:
                        detail["price_raw"] = text.strip()
                        price_match = re.search(r'[\$]?\s*([\d,]+(?:\.\d{2})?)', text)
                        if price_match:
                            detail["price_usd"] = float(
                                price_match.group(1).replace(",", "")
                            )
                    break

            # Extract description
            for sel in [
                "[class*='description']", ".description", ".ad-description",
                "[class*='detail-desc']", "#description",
            ]:
                el = await page.query_selector(sel)
                if el:
                    text = await el.inner_text()
                    if text and len(text.strip()) > 10:
                        detail["description_es"] = text.strip()[:2000]
                        break

            # Extract all images
            images = []
            img_selectors = [
                "div[class*='gallery'] img",
                "div[class*='carousel'] img",
                "div[class*='slider'] img",
                "div[class*='photo'] img",
                "[class*='image-gallery'] img",
                "img[class*='ad-image']",
            ]
            for sel in img_selectors:
                img_elements = await page.query_selector_all(sel)
                if img_elements:
                    for img_el in img_elements:
                        for attr in ["src", "data-src", "data-lazy-src"]:
                            src = await img_el.get_attribute(attr) or ""
                            if src and not src.startswith("data:") and src not in images:
                                if not src.startswith("http"):
                                    src = urljoin(self.base_url, src)
                                images.append(src)
                    if images:
                        break
            
            # Fallback: get all reasonable images on page
            if not images:
                all_imgs = await page.query_selector_all("img[src]")
                for img_el in all_imgs:
                    src = await img_el.get_attribute("src") or ""
                    width = await img_el.get_attribute("width")
                    if (
                        src
                        and not src.startswith("data:")
                        and "logo" not in src.lower()
                        and "icon" not in src.lower()
                        and "avatar" not in src.lower()
                        and (width is None or int(width or 0) > 100)
                    ):
                        if not src.startswith("http"):
                            src = urljoin(self.base_url, src)
                        images.append(src)

            detail["images"] = images[:20]  # Cap at 20 images

            # Extract features/attributes table
            features = []
            attr_selectors = [
                "[class*='attribute'] li",
                "[class*='feature'] li",
                "table[class*='detail'] tr",
                "[class*='specs'] div",
                ".ad-attributes li",
            ]
            for sel in attr_selectors:
                els = await page.query_selector_all(sel)
                if els:
                    for el in els:
                        text = (await el.inner_text()).strip()
                        if text and len(text) < 100:
                            features.append(text)

                            # Parse structured data from features
                            text_lower = text.lower()
                            bed_match = re.search(r'(\d+)\s*(?:hab|rec|bed|dorm)', text_lower)
                            if bed_match and "bedrooms" not in detail:
                                detail["bedrooms"] = int(bed_match.group(1))
                            bath_match = re.search(r'(\d+)\s*(?:ba[ñn]|bath)', text_lower)
                            if bath_match and "bathrooms" not in detail:
                                detail["bathrooms"] = int(bath_match.group(1))
                            area_match = re.search(r'([\d,.]+)\s*(?:m²|m2|mts)', text_lower)
                            if area_match and "area_m2" not in detail:
                                detail["area_m2"] = float(
                                    area_match.group(1).replace(",", "")
                                )
                            lot_match = re.search(r'terreno[:\s]*([\d,.]+)\s*(?:m²|m2|v2|varas)', text_lower)
                            if lot_match and "lot_size_m2" not in detail:
                                detail["lot_size_m2"] = float(
                                    lot_match.group(1).replace(",", "")
                                )
                    if features:
                        break

            detail["features"] = features

            # Extract location from breadcrumbs or location section
            for sel in [
                "[class*='breadcrumb'] a",
                "[class*='location'] span",
                ".ad-location",
            ]:
                els = await page.query_selector_all(sel)
                if els:
                    texts = []
                    for el in els:
                        t = (await el.inner_text()).strip()
                        if t:
                            texts.append(t)
                    if texts:
                        detail["breadcrumb_texts"] = texts
                    break

            # Try to get coordinates from embedded map
            try:
                coords = await page.evaluate("""
                    () => {
                        // Check for Google Maps iframe
                        const mapIframe = document.querySelector('iframe[src*="maps"]');
                        if (mapIframe) {
                            const src = mapIframe.src;
                            const match = src.match(/[?&]q=([-\\d.]+),([-\\d.]+)/);
                            if (match) return { lat: parseFloat(match[1]), lng: parseFloat(match[2]) };
                            const match2 = src.match(/@([-\\d.]+),([-\\d.]+)/);
                            if (match2) return { lat: parseFloat(match2[1]), lng: parseFloat(match2[2]) };
                        }
                        // Check for data attributes
                        const mapEl = document.querySelector('[data-lat][data-lng]');
                        if (mapEl) return { 
                            lat: parseFloat(mapEl.dataset.lat), 
                            lng: parseFloat(mapEl.dataset.lng) 
                        };
                        return null;
                    }
                """)
                if coords and coords.get("lat") and coords.get("lng"):
                    detail["latitude"] = coords["lat"]
                    detail["longitude"] = coords["lng"]
            except Exception:
                pass

            # Try JSON-LD on detail page
            try:
                json_ld_scripts = await page.query_selector_all(
                    'script[type="application/ld+json"]'
                )
                for script in json_ld_scripts:
                    text = await script.inner_text()
                    try:
                        data = json.loads(text)
                        if isinstance(data, dict):
                            if data.get("@type") in ("Product", "RealEstateListing", "Offer"):
                                if "name" in data and "title" not in detail:
                                    detail["title"] = data["name"]
                                if "description" in data and "description_es" not in detail:
                                    detail["description_es"] = data["description"][:2000]
                                if "image" in data and not detail.get("images"):
                                    imgs = data["image"]
                                    if isinstance(imgs, str):
                                        imgs = [imgs]
                                    detail["images"] = imgs[:20]
                                offers = data.get("offers", {})
                                if isinstance(offers, dict) and "price" in offers:
                                    if "price_usd" not in detail:
                                        detail["price_usd"] = float(offers["price"])
                                geo = data.get("geo", {})
                                if isinstance(geo, dict):
                                    if "latitude" not in detail:
                                        detail["latitude"] = float(geo.get("latitude", 0))
                                        detail["longitude"] = float(geo.get("longitude", 0))
                    except (json.JSONDecodeError, ValueError):
                        continue
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error fetching detail page {url}: {e}")
        finally:
            await page.close()

        return detail

    def _parse_location(self, raw: dict) -> tuple[str, str]:
        """
        Parse department and municipio from location text or breadcrumbs.
        Returns (department, municipio).
        """
        department = ""
        municipio = ""

        # From breadcrumbs
        breadcrumbs = raw.get("breadcrumb_texts", [])
        for crumb in breadcrumbs:
            crumb_lower = crumb.lower().strip()
            for slug, name in DEPARTMENT_SLUGS.items():
                if name.lower() == crumb_lower or slug.replace("-", " ") == crumb_lower:
                    department = name
                    break

        # From location text
        location_text = raw.get("location_text", "")
        if location_text and not department:
            for slug, name in DEPARTMENT_SLUGS.items():
                if name.lower() in location_text.lower():
                    department = name
                    break

        # Try to extract municipio from location text
        if location_text:
            parts = [p.strip() for p in location_text.replace(",", "/").split("/")]
            if len(parts) >= 2:
                municipio = parts[0]  # Usually municipio comes first
            elif len(parts) == 1 and department:
                municipio = parts[0]

        # Fallback: from URL
        url = raw.get("url", "")
        if not department and url:
            for slug, name in DEPARTMENT_SLUGS.items():
                if f"/{slug}" in url.lower():
                    department = name
                    break

        return department, municipio

    def _infer_property_type(self, url: str) -> str:
        """Infer property type from the URL slug."""
        url_lower = url.lower()
        for slug, ptype in SLUG_TO_TYPE.items():
            if slug in url_lower:
                return ptype
        return "house"  # Default

    def _raw_to_scraped(self, raw: dict, default_type: str = "house") -> ScrapedProperty | None:
        """Convert raw extracted data dict to a ScrapedProperty."""
        url = raw.get("url", "")
        title = raw.get("title", "")

        if not url and not title:
            return None

        department, municipio = self._parse_location(raw)
        property_type = self._infer_property_type(url) if url else default_type

        images = raw.get("images", [])
        if not images and raw.get("image"):
            images = [raw["image"]]

        return ScrapedProperty(
            title=title or "Propiedad en El Salvador",
            source=self.source_name,
            source_url=url,
            department=department,
            municipio=municipio,
            address=raw.get("location_text", ""),
            latitude=raw.get("latitude"),
            longitude=raw.get("longitude"),
            price_usd=raw.get("price_usd"),
            price_raw=raw.get("price_raw", ""),
            property_type=property_type,
            bedrooms=raw.get("bedrooms"),
            bathrooms=raw.get("bathrooms"),
            area_m2=raw.get("area_m2"),
            lot_size_m2=raw.get("lot_size_m2"),
            description_es=raw.get("description_es", ""),
            images=images,
            features=raw.get("features", []),
        )

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 50,
        categories: list[str] | None = None,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """
        Yield property listings from Encuentra24 El Salvador.
        
        Args:
            department: Filter by department name (e.g., "San Salvador")
            municipio: Not directly supported by URL, used for post-filtering
            max_pages: Maximum pages to scrape per category
            categories: Property categories to scrape (defaults to all)
            fetch_details: Whether to fetch detail pages for richer data
        """
        if categories is None:
            categories = list(CATEGORY_SLUGS.keys())

        for category in categories:
            logger.info(
                f"Scraping {category} listings"
                f"{f' in {department}' if department else ''}"
            )

            for page_num in range(1, max_pages + 1):
                url = self._build_listing_url(category, department, page_num)
                logger.info(f"  Page {page_num}: {url}")

                # Use Playwright to load the page
                page = await self._new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded")
                    # Wait for listings to render
                    await page.wait_for_timeout(5000)

                    # Check if page has results
                    content = await page.content()
                    if "no se encontraron resultados" in content.lower() or \
                       "no results found" in content.lower():
                        logger.info(f"  No more results at page {page_num}")
                        await page.close()
                        break

                    # Extract listings from the page
                    raw_listings = await self._extract_listings_from_page(page)
                    await page.close()

                    if not raw_listings:
                        logger.info(f"  No listings found on page {page_num}, stopping")
                        break

                    logger.info(f"  Found {len(raw_listings)} listings on page {page_num}")

                    for raw in raw_listings:
                        # Optionally fetch detail page for richer data
                        if fetch_details and raw.get("url") and (
                            raw.get("_needs_detail_fetch") or
                            not raw.get("description_es")
                        ):
                            detail_url = raw["url"]
                            if detail_url in self._seen_urls:
                                continue

                            logger.debug(f"  Fetching detail: {detail_url}")
                            detail = await self._fetch_detail_page(detail_url)
                            # Merge detail into raw (detail overwrites)
                            merged = {**raw, **{k: v for k, v in detail.items() if v}}
                            merged.pop("_needs_detail_fetch", None)
                            prop = self._raw_to_scraped(merged, default_type=category)
                        else:
                            prop = self._raw_to_scraped(raw, default_type=category)

                        if prop and prop.source_url not in self._seen_urls:
                            yield prop

                except Exception as e:
                    logger.error(f"  Error on page {page_num}: {e}")
                    try:
                        await page.close()
                    except Exception:
                        pass
                    continue

                # Respect rate limits between pages
                await asyncio.sleep(2)

    async def scrape_all_departments(
        self,
        max_pages_per_dept: int = 25,
        categories: list[str] | None = None,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """
        Scrape all departments one by one for comprehensive coverage.
        """
        # First scrape without department filter (catches all)
        logger.info("=== Scraping all listings (no department filter) ===")
        async for prop in self.scrape_listings(
            max_pages=max_pages_per_dept * 2,
            categories=categories,
            fetch_details=fetch_details,
        ):
            yield prop

        # Then scrape each department individually to catch any missed
        for dept_slug, dept_name in DEPARTMENT_SLUGS.items():
            logger.info(f"=== Scraping department: {dept_name} ===")
            async for prop in self.scrape_listings(
                department=dept_name,
                max_pages=max_pages_per_dept,
                categories=categories,
                fetch_details=fetch_details,
            ):
                yield prop
