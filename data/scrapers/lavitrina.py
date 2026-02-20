"""
LaVitrina El Salvador — Property Scraper
==========================================
Scrapes real estate listings from lavitrina.com.sv.

LaVitrina is a local Salvadoran classifieds site with good coverage
of mid-range and rural properties.

URL patterns:
  - Houses:      /inmuebles/casas-en-venta
  - Apartments:  /inmuebles/apartamentos-en-venta
  - Land:        /inmuebles/terrenos-en-venta
  - Commercial:  /inmuebles/locales-en-venta
  Pagination: ?page=2, ?page=3, ...
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

DEPARTMENT_KEYWORDS = {
    "san salvador": "San Salvador",
    "la libertad": "La Libertad",
    "santa ana": "Santa Ana",
    "san miguel": "San Miguel",
    "sonsonate": "Sonsonate",
    "usulutan": "Usulután",
    "usulután": "Usulután",
    "ahuachapan": "Ahuachapán",
    "ahuachapán": "Ahuachapán",
    "la paz": "La Paz",
    "cuscatlan": "Cuscatlán",
    "cuscatlán": "Cuscatlán",
    "chalatenango": "Chalatenango",
    "la union": "La Unión",
    "la unión": "La Unión",
    "morazan": "Morazán",
    "morazán": "Morazán",
    "cabanas": "Cabañas",
    "cabañas": "Cabañas",
    "san vicente": "San Vicente",
}

CATEGORIES = [
    ("casas-en-venta", "house"),
    ("apartamentos-en-venta", "apartment"),
    ("terrenos-en-venta", "land"),
    ("locales-en-venta", "commercial"),
]

BASE_URL = "https://www.lavitrina.com.sv"


class LaVitrinaScraper(BaseScraper):
    """Scrapes property listings from LaVitrina SV."""

    source_name = "lavitrina"
    base_url = BASE_URL
    requests_per_second = 0.5

    def _resolve_department(self, text: str) -> str:
        text_lower = text.lower()
        for keyword, name in DEPARTMENT_KEYWORDS.items():
            if keyword in text_lower:
                return name
        return ""

    def _parse_price(self, text: str) -> tuple[float | None, str]:
        if not text:
            return None, ""
        text = text.strip()
        clean = re.sub(r"[^\d.]", "", text.replace(",", ""))
        try:
            price = float(clean)
            return (price, text) if price > 0 else (None, text)
        except (ValueError, TypeError):
            return None, text

    async def _parse_listing_page(self, html: str, page_url: str, category_type: str) -> list[ScrapedProperty]:
        """Parse a LaVitrina listing page."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            # LaVitrina typically uses card-based layouts
            cards = tree.css(
                ".anuncio, .listing-card, .property-card, .ad-card, "
                ".card, article, [class*='anuncio'], [class*='listing'], "
                "[class*='result-item'], [class*='classified']"
            )

            if not cards:
                # Try links as fallback
                cards = tree.css("a[href*='/inmueble'], a[href*='/anuncio'], a[href*='/propiedad']")

            for card in cards:
                try:
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    if not link_el:
                        continue
                    href = link_el.attributes.get("href", "")
                    if not href or len(href) < 5:
                        continue
                    detail_url = urljoin(page_url, href)

                    # Skip non-property links
                    if any(skip in detail_url for skip in [
                        "/contacto", "/nosotros", "/registro", "/login",
                        "page=", "/categoria", "/buscar", "javascript:"
                    ]):
                        continue

                    title_el = card.css_first("h2, h3, h4, .title, [class*='title'], [class*='nombre']")
                    title = title_el.text(strip=True) if title_el else ""

                    price_el = card.css_first("[class*='precio'], [class*='price'], .price")
                    price_text = price_el.text(strip=True) if price_el else ""
                    price_usd, price_raw = self._parse_price(price_text)

                    loc_el = card.css_first(
                        "[class*='ubicacion'], [class*='location'], "
                        "[class*='direccion'], [class*='address'], .location"
                    )
                    location = loc_el.text(strip=True) if loc_el else ""
                    department = self._resolve_department(location) or self._resolve_department(title)

                    bedrooms = None
                    bathrooms = None
                    area_m2 = None

                    for spec in card.css("[class*='spec'], [class*='detail'], [class*='caract'], li, span"):
                        text = spec.text(strip=True).lower()
                        bed_m = re.search(r"(\d+)\s*(?:rec|hab|dorm|cuarto|bed)", text)
                        if bed_m:
                            bedrooms = int(bed_m.group(1))
                        bath_m = re.search(r"(\d+)\s*(?:bañ|bath|sanitario)", text)
                        if bath_m:
                            bathrooms = int(bath_m.group(1))
                        area_m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|mts|v²|v2|varas)", text)
                        if area_m:
                            val = float(area_m.group(1).replace(",", ""))
                            if "vara" in text or "v²" in text or "v2" in text:
                                val = round(val * 0.6987, 2)  # varas² to m²
                            area_m2 = val

                    images = []
                    for img in card.css("img[src], img[data-src], img[data-lazy]"):
                        src = img.attributes.get("data-lazy") or img.attributes.get("data-src") or img.attributes.get("src", "")
                        if src and "placeholder" not in src and "logo" not in src and "no-image" not in src:
                            images.append(urljoin(page_url, src))

                    prop = ScrapedProperty(
                        title=title or f"Property in {location or 'El Salvador'}",
                        source=self.source_name,
                        source_url=detail_url,
                        department=department,
                        address=location,
                        price_usd=price_usd,
                        price_raw=price_raw,
                        property_type=category_type,
                        bedrooms=bedrooms,
                        bathrooms=bathrooms,
                        area_m2=area_m2,
                        images=images[:5],
                    )
                    properties.append(prop)
                except Exception as e:
                    logger.debug(f"Error parsing card: {e}")
                    continue

        except ImportError:
            # Regex fallback
            links = re.findall(
                r'href=["\']([^"\']*(?:/inmueble|/anuncio|/propiedad)[^"\']*)["\']',
                html, re.IGNORECASE,
            )
            seen = set()
            for href in links:
                url = urljoin(page_url, href)
                if url in seen:
                    continue
                seen.add(url)
                prop = ScrapedProperty(
                    title="Property listing",
                    source=self.source_name,
                    source_url=url,
                    department=self._resolve_department(url),
                    property_type=category_type,
                )
                properties.append(prop)

        return properties

    async def _enrich_from_detail(self, prop: ScrapedProperty) -> ScrapedProperty:
        """Enrich from detail page."""
        resp = await self.fetch(prop.source_url)
        if not resp:
            return prop

        html = resp.text

        # JSON-LD
        jsonld_match = re.search(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.DOTALL | re.IGNORECASE,
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
                    imgs = ld["image"] if isinstance(ld["image"], list) else [ld["image"]]
                    prop.images = imgs[:8]
            except (json.JSONDecodeError, KeyError):
                pass

        # Description
        if not prop.description:
            desc_match = re.search(
                r'(?:class=["\'][^"\']*(?:descripcion|description|detalle)[^"\']*["\'][^>]*>)\s*(.*?)\s*</(?:div|p|section)',
                html, re.DOTALL | re.IGNORECASE,
            )
            if desc_match:
                prop.description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()[:2000]

        # Specs
        if prop.bedrooms is None:
            m = re.search(r"(\d+)\s*(?:recámara|habitaci|dormitorio|cuarto|bedroom)", html, re.IGNORECASE)
            if m:
                prop.bedrooms = int(m.group(1))
        if prop.bathrooms is None:
            m = re.search(r"(\d+)\s*(?:baño|bathroom|sanitario)", html, re.IGNORECASE)
            if m:
                prop.bathrooms = int(m.group(1))
        if not prop.area_m2:
            m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|metros cuadrados)", html, re.IGNORECASE)
            if m:
                try:
                    prop.area_m2 = float(m.group(1).replace(",", ""))
                except ValueError:
                    pass

        # Images
        if not prop.images:
            img_urls = re.findall(
                r'(?:src|data-src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\']',
                html, re.IGNORECASE,
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
        max_pages: int = 20,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape listings from LaVitrina."""

        for cat_slug, cat_type in CATEGORIES:
            logger.info(f"[lavitrina] Scraping category: {cat_slug}")

            for page_num in range(1, max_pages + 1):
                if page_num == 1:
                    url = f"{BASE_URL}/inmuebles/{cat_slug}"
                else:
                    url = f"{BASE_URL}/inmuebles/{cat_slug}?page={page_num}"

                logger.info(f"[lavitrina] Page {page_num}: {url}")

                resp = await self.fetch(url)
                if not resp:
                    logger.warning(f"[lavitrina] Failed page {page_num}, stopping category")
                    break

                if resp.status_code == 404:
                    break

                properties = await self._parse_listing_page(resp.text, url, cat_type)

                if not properties:
                    logger.info(f"[lavitrina] No properties on page {page_num}, done with {cat_slug}")
                    break

                for prop in properties:
                    if department and prop.department and prop.department != department:
                        continue
                    if prop.source_url in self._seen_urls:
                        continue
                    self._seen_urls.add(prop.source_url)

                    if fetch_details:
                        prop = await self._enrich_from_detail(prop)

                    yield prop

                logger.info(f"[lavitrina] Page {page_num}: {len(properties)} listings")
                await asyncio.sleep(1)
