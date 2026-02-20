"""
Lamudi El Salvador — Property Scraper
=======================================
Scrapes real estate listings from lamudi.com.sv.

URL patterns:
  - Buy:  /venta/
  - Rent: /alquiler/
  Pagination: ?page=1, ?page=2, ...

Lamudi uses server-rendered HTML with good structure.
Property cards have data attributes and JSON-LD on detail pages.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import AsyncGenerator
from urllib.parse import urljoin, urlencode

from base import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)

# Department mapping — Lamudi uses slug-based URLs
DEPARTMENT_SLUGS = {
    "san-salvador": "San Salvador",
    "la-libertad": "La Libertad",
    "santa-ana": "Santa Ana",
    "san-miguel": "San Miguel",
    "sonsonate": "Sonsonate",
    "usulutan": "Usulután",
    "ahuachapan": "Ahuachapán",
    "la-paz": "La Paz",
    "cuscatlan": "Cuscatlán",
    "chalatenango": "Chalatenango",
    "la-union": "La Unión",
    "morazan": "Morazán",
    "cabanas": "Cabañas",
    "san-vicente": "San Vicente",
}

PROPERTY_CATEGORIES = [
    ("casa", "house"),
    ("apartamento", "apartment"),
    ("terreno", "land"),
    ("local-comercial", "commercial"),
    ("oficina", "commercial"),
]

BASE_URL = "https://www.lamudi.com.sv"


class LamudiScraper(BaseScraper):
    """Scrapes property listings from Lamudi El Salvador."""

    source_name = "lamudi"
    base_url = BASE_URL
    requests_per_second = 0.5  # Be polite

    def _resolve_department(self, text: str) -> str:
        """Resolve department name from text."""
        text_lower = text.lower().replace(" ", "-")
        for slug, name in DEPARTMENT_SLUGS.items():
            if slug in text_lower:
                return name
        return ""

    def _parse_price(self, text: str) -> tuple[float | None, str]:
        """Parse price from text, return (usd_amount, raw_text)."""
        if not text:
            return None, ""
        text = text.strip()
        # Remove currency symbols and commas
        clean = re.sub(r"[^\d.]", "", text.replace(",", ""))
        try:
            price = float(clean)
            if price > 0:
                return price, text
        except (ValueError, TypeError):
            pass
        return None, text

    def _parse_area(self, text: str) -> float | None:
        """Parse area in m² from text."""
        if not text:
            return None
        match = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|mts)", text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                pass
        return None

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse a listing page and extract property cards."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
        except ImportError:
            logger.warning("selectolax not installed, using regex fallback")
            return await self._parse_listing_page_regex(html, page_url)

        tree = HTMLParser(html)

        # Lamudi typically uses listing card containers
        cards = tree.css("[data-listing-id], .listing-card, .ListingCard, .listing-item, .property-card")
        if not cards:
            # Fallback: look for links that look like listing detail pages
            cards = tree.css("a[href*='/detalle/'], a[href*='/venta/'], a[href*='listing']")

        for card in cards:
            try:
                # Get link
                link_el = card.css_first("a[href]") if card.tag != "a" else card
                if not link_el:
                    continue
                href = link_el.attributes.get("href", "")
                if not href or "/detalle/" not in href and "listing" not in href.lower():
                    continue
                detail_url = urljoin(page_url, href)

                # Title
                title_el = card.css_first("h2, h3, .listing-title, .ListingCard-title, [class*='title']")
                title = title_el.text(strip=True) if title_el else ""

                # Price
                price_el = card.css_first(".listing-price, .ListingCard-price, [class*='price'], [data-price]")
                price_text = price_el.text(strip=True) if price_el else ""
                price_usd, price_raw = self._parse_price(price_text)

                # Location
                loc_el = card.css_first(".listing-location, .ListingCard-location, [class*='location'], [class*='address']")
                location = loc_el.text(strip=True) if loc_el else ""
                department = self._resolve_department(location)

                # Specs (beds, baths, area)
                bedrooms = None
                bathrooms = None
                area_m2 = None

                spec_els = card.css("[class*='spec'], [class*='attribute'], [class*='feature'], li")
                for spec in spec_els:
                    text = spec.text(strip=True).lower()
                    bed_match = re.search(r"(\d+)\s*(?:rec|hab|dorm|bed|cuarto)", text)
                    if bed_match:
                        bedrooms = int(bed_match.group(1))
                    bath_match = re.search(r"(\d+)\s*(?:bañ|bath)", text)
                    if bath_match:
                        bathrooms = int(bath_match.group(1))
                    area_val = self._parse_area(text)
                    if area_val:
                        area_m2 = area_val

                # Property type from URL or card classes
                prop_type = ""
                for cat_slug, cat_type in PROPERTY_CATEGORIES:
                    if cat_slug in detail_url.lower() or cat_slug in title.lower():
                        prop_type = cat_type
                        break

                # Images
                images = []
                img_els = card.css("img[src], img[data-src]")
                for img in img_els:
                    src = img.attributes.get("data-src") or img.attributes.get("src", "")
                    if src and "placeholder" not in src and "logo" not in src:
                        images.append(urljoin(page_url, src))

                prop = ScrapedProperty(
                    title=title or f"Property in {location}",
                    source=self.source_name,
                    source_url=detail_url,
                    department=department,
                    address=location,
                    price_usd=price_usd,
                    price_raw=price_raw,
                    property_type=prop_type,
                    bedrooms=bedrooms,
                    bathrooms=bathrooms,
                    area_m2=area_m2,
                    images=images[:5],
                )
                properties.append(prop)
            except Exception as e:
                logger.debug(f"Error parsing card: {e}")
                continue

        return properties

    async def _parse_listing_page_regex(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Regex-based fallback parser for listing pages."""
        properties = []

        # Find all detail page links
        detail_links = re.findall(
            r'href=["\']([^"\']*(?:/detalle/|/listing/)[^"\']*)["\']',
            html,
            re.IGNORECASE,
        )

        seen = set()
        for href in detail_links:
            url = urljoin(page_url, href)
            if url in seen:
                continue
            seen.add(url)

            # Try to extract title from nearby text
            title_match = re.search(
                re.escape(href) + r'[^>]*>([^<]+)',
                html,
            )
            title = title_match.group(1).strip() if title_match else f"Listing from {self.source_name}"

            # Try to find price nearby
            price_usd = None
            price_raw = ""
            context_start = html.find(href)
            if context_start > 0:
                context = html[max(0, context_start - 500):context_start + 1000]
                price_match = re.search(
                    r'\$\s*([\d,]+(?:\.\d{2})?)',
                    context,
                )
                if price_match:
                    price_usd, price_raw = self._parse_price(price_match.group(0))

            department = self._resolve_department(url)

            prop = ScrapedProperty(
                title=title,
                source=self.source_name,
                source_url=url,
                department=department,
                price_usd=price_usd,
                price_raw=price_raw,
            )
            properties.append(prop)

        return properties

    async def _enrich_from_detail(self, prop: ScrapedProperty) -> ScrapedProperty:
        """Fetch detail page and enrich property data."""
        resp = await self.fetch(prop.source_url)
        if not resp:
            return prop

        html = resp.text

        # Try JSON-LD first (most reliable)
        jsonld_match = re.search(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        if jsonld_match:
            try:
                ld = json.loads(jsonld_match.group(1))
                if isinstance(ld, list):
                    ld = ld[0]

                prop.title = ld.get("name", prop.title)
                prop.description = ld.get("description", prop.description)

                if "geo" in ld:
                    try:
                        prop.latitude = float(ld["geo"].get("latitude", 0))
                        prop.longitude = float(ld["geo"].get("longitude", 0))
                    except (ValueError, TypeError):
                        pass

                if "image" in ld:
                    imgs = ld["image"]
                    if isinstance(imgs, str):
                        imgs = [imgs]
                    prop.images = imgs[:8]

                if "offers" in ld:
                    offer = ld["offers"]
                    if isinstance(offer, list):
                        offer = offer[0]
                    try:
                        prop.price_usd = float(offer.get("price", 0))
                        prop.price_raw = f"{offer.get('priceCurrency', 'USD')} {offer.get('price', '')}"
                    except (ValueError, TypeError):
                        pass

                addr = ld.get("address", {})
                if isinstance(addr, dict):
                    prop.address = addr.get("streetAddress", prop.address)
                    region = addr.get("addressRegion", "")
                    if region:
                        prop.department = self._resolve_department(region) or prop.department

            except (json.JSONDecodeError, KeyError):
                pass

        # Parse description from HTML if not found in JSON-LD
        if not prop.description:
            desc_match = re.search(
                r'(?:class=["\'][^"\']*description[^"\']*["\'][^>]*>)\s*(.*?)\s*</(?:div|p|section)',
                html,
                re.DOTALL | re.IGNORECASE,
            )
            if desc_match:
                prop.description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()[:2000]

        # Parse additional specs
        if prop.bedrooms is None:
            bed_match = re.search(r"(\d+)\s*(?:recámaras|habitaciones|dormitorios|bedrooms)", html, re.IGNORECASE)
            if bed_match:
                prop.bedrooms = int(bed_match.group(1))

        if prop.bathrooms is None:
            bath_match = re.search(r"(\d+)\s*(?:baños|bathrooms)", html, re.IGNORECASE)
            if bath_match:
                prop.bathrooms = int(bath_match.group(1))

        if not prop.area_m2:
            area_match = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|metros cuadrados)", html, re.IGNORECASE)
            if area_match:
                try:
                    prop.area_m2 = float(area_match.group(1).replace(",", ""))
                except ValueError:
                    pass

        # Images from page
        if not prop.images:
            img_urls = re.findall(
                r'(?:src|data-src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\']',
                html,
                re.IGNORECASE,
            )
            prop.images = [
                urljoin(prop.source_url, u)
                for u in img_urls
                if "logo" not in u and "icon" not in u and "placeholder" not in u
            ][:8]

        return prop

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 30,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape property listings from Lamudi SV."""

        categories = PROPERTY_CATEGORIES

        for cat_slug, cat_type in categories:
            logger.info(f"[lamudi] Scraping category: {cat_slug}")

            for page_num in range(1, max_pages + 1):
                url = f"{BASE_URL}/venta/{cat_slug}/?page={page_num}"
                logger.info(f"[lamudi] Page {page_num}: {url}")

                resp = await self.fetch(url)
                if not resp:
                    logger.warning(f"[lamudi] Failed to fetch page {page_num}, stopping category")
                    break

                if resp.status_code == 404:
                    logger.info(f"[lamudi] Page {page_num} returned 404, done with {cat_slug}")
                    break

                html = resp.text
                properties = await self._parse_listing_page(html, url)

                if not properties:
                    logger.info(f"[lamudi] No properties on page {page_num}, done with {cat_slug}")
                    break

                for prop in properties:
                    prop.property_type = prop.property_type or cat_type

                    if department and prop.department and prop.department != department:
                        continue

                    if prop.source_url in self._seen_urls:
                        continue
                    self._seen_urls.add(prop.source_url)

                    # Enrich from detail page
                    if fetch_details:
                        prop = await self._enrich_from_detail(prop)

                    yield prop

                logger.info(f"[lamudi] Page {page_num}: {len(properties)} listings")
                # Small delay between pages
                await asyncio.sleep(1)
