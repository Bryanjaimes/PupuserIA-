"""
CityMax El Salvador — Property Scraper
========================================
Scrapes real estate listings from citymax-sv.com.

CityMax is a Central American real estate franchise (Guatemala, El Salvador,
Costa Rica, Honduras) with strong presence in the Salvadoran market.
They tend to have premium and mid-range properties with good data quality.

URL: https://www.citymax-sv.com/propiedades
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
    "antiguo cuscatlan": "La Libertad",
    "antiguo cuscatlán": "La Libertad",
    "santa tecla": "La Libertad",
    "escalon": "San Salvador",
    "escalón": "San Salvador",
    "san benito": "San Salvador",
    "colonia san benito": "San Salvador",
}

BASE_URL = "https://www.citymax-sv.com"

LISTING_PATHS = [
    "/propiedades/venta",
    "/propiedades",
    "/properties/sale",
    "/properties",
    "/inmuebles",
]


class CityMaxScraper(BaseScraper):
    """Scrapes property listings from CityMax El Salvador."""

    source_name = "citymax"
    base_url = BASE_URL
    requests_per_second = 0.4

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

    def _guess_type(self, text: str) -> str:
        text_lower = text.lower()
        for keyword, ptype in [
            ("casa", "house"), ("house", "house"), ("vivienda", "house"),
            ("residencia", "house"), ("villa", "house"), ("townhouse", "house"),
            ("apartamento", "apartment"), ("apartment", "apartment"),
            ("condo", "apartment"), ("condominio", "apartment"), ("penthouse", "apartment"),
            ("terreno", "land"), ("land", "land"), ("lote", "land"), ("finca", "land"),
            ("local", "commercial"), ("oficina", "commercial"), ("bodega", "commercial"),
            ("commercial", "commercial"), ("nave", "commercial"),
        ]:
            if keyword in text_lower:
                return ptype
        return ""

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse a CityMax listing page."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            cards = tree.css(
                ".listing-card, .property-card, [class*='listing'], "
                "[class*='property-item'], [class*='PropertyCard'], "
                "article, .card, [data-listing], .result-item, "
                "[class*='inmueble'], [class*='propiedad']"
            )

            if not cards:
                cards = tree.css(
                    "a[href*='/propiedad/'], a[href*='/listing/'], "
                    "a[href*='/property/'], a[href*='/inmueble/'], "
                    "a[href*='/detalle/']"
                )

            for card in cards:
                try:
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    if not link_el:
                        continue
                    href = link_el.attributes.get("href", "")
                    if not href or len(href) < 5:
                        continue
                    detail_url = urljoin(page_url, href)

                    if any(skip in detail_url.lower() for skip in [
                        "/contacto", "/agente", "/agent", "/office",
                        "javascript:", "#", "/buscar", "/blog",
                        "/about", "/nosotros",
                    ]):
                        continue

                    title_el = card.css_first(
                        "h2, h3, h4, [class*='title'], [class*='address'], [class*='name']"
                    )
                    title = title_el.text(strip=True) if title_el else ""

                    price_el = card.css_first("[class*='price'], [class*='precio'], [data-price]")
                    price_text = price_el.text(strip=True) if price_el else ""
                    price_usd, price_raw = self._parse_price(price_text)

                    loc_el = card.css_first(
                        "[class*='location'], [class*='address'], "
                        "[class*='ubicacion'], [class*='city']"
                    )
                    location = loc_el.text(strip=True) if loc_el else ""
                    department = self._resolve_department(location) or self._resolve_department(title)

                    bedrooms = None
                    bathrooms = None
                    area_m2 = None

                    for spec in card.css("[class*='spec'], [class*='detail'], [class*='feature'], span, li"):
                        text = spec.text(strip=True).lower()
                        bed_m = re.search(r"(\d+)\s*(?:bed|rec|hab|dorm)", text)
                        if bed_m:
                            bedrooms = int(bed_m.group(1))
                        bath_m = re.search(r"(\d+)\s*(?:bath|bañ)", text)
                        if bath_m:
                            bathrooms = int(bath_m.group(1))
                        area_m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|sq)", text)
                        if area_m:
                            try:
                                val = float(area_m.group(1).replace(",", ""))
                                if "sq" in text and "ft" in text:
                                    val = round(val * 0.092903, 2)
                                area_m2 = val
                            except ValueError:
                                pass

                    prop_type = self._guess_type(title + " " + detail_url)

                    images = []
                    for img in card.css("img[src], img[data-src], img[data-original]"):
                        src = (
                            img.attributes.get("data-original")
                            or img.attributes.get("data-src")
                            or img.attributes.get("src", "")
                        )
                        if src and not any(s in src.lower() for s in [
                            "placeholder", "logo", "icon", "no-image", "avatar", "agent"
                        ]):
                            images.append(urljoin(page_url, src))

                    prop = ScrapedProperty(
                        title=title or f"CityMax Property in {location or 'El Salvador'}",
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
                    logger.debug(f"Error parsing CityMax card: {e}")
                    continue

        except ImportError:
            links = re.findall(
                r'href=["\']([^"\']*(?:/propiedad/|/listing/|/property/|/inmueble/)[^"\']*)["\']',
                html, re.IGNORECASE,
            )
            for href in set(links):
                url = urljoin(page_url, href)
                prop = ScrapedProperty(
                    title="CityMax Listing",
                    source=self.source_name,
                    source_url=url,
                    department=self._resolve_department(url),
                )
                properties.append(prop)

        return properties

    async def _enrich_from_detail(self, prop: ScrapedProperty) -> ScrapedProperty:
        """Fetch detail page and enrich the property."""
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
                    ld = next((x for x in ld if x.get("@type") in
                              ("Product", "RealEstateListing", "Residence", "House",
                               "Apartment", "SingleFamilyResidence")), ld[0])
                if not prop.description:
                    prop.description = ld.get("description", "")
                if "geo" in ld:
                    try:
                        prop.latitude = float(ld["geo"].get("latitude", 0))
                        prop.longitude = float(ld["geo"].get("longitude", 0))
                    except (ValueError, TypeError):
                        pass
                if "image" in ld:
                    imgs = ld["image"] if isinstance(ld["image"], list) else [ld["image"]]
                    if len(imgs) > len(prop.images):
                        prop.images = imgs[:10]
                if "offers" in ld:
                    offer = ld["offers"] if isinstance(ld["offers"], dict) else ld["offers"][0]
                    if not prop.price_usd:
                        try:
                            prop.price_usd = float(offer.get("price", 0))
                        except (ValueError, TypeError):
                            pass
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

        # Coordinates from map embeds
        if not prop.latitude:
            coord_match = re.search(r"(?:lat|latitude)[\"'\s:=]+(-?\d+\.\d+)", html, re.IGNORECASE)
            lng_match = re.search(r"(?:lng|longitude|lon)[\"'\s:=]+(-?\d+\.\d+)", html, re.IGNORECASE)
            if coord_match and lng_match:
                try:
                    lat = float(coord_match.group(1))
                    lng = float(lng_match.group(1))
                    if 13.0 < lat < 15.0 and -91.0 < lng < -87.0:
                        prop.latitude = lat
                        prop.longitude = lng
                except ValueError:
                    pass

        # Description fallback
        if not prop.description:
            desc_match = re.search(
                r'(?:class=["\'][^"\']*(?:descripci[oó]n|description|remarks|detalle)[^"\']*["\'][^>]*>)\s*(.*?)\s*</(?:div|p|section)',
                html, re.DOTALL | re.IGNORECASE,
            )
            if desc_match:
                prop.description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()[:2000]

        # Specs fallback
        if prop.bedrooms is None:
            m = re.search(r"(\d+)\s*(?:bed|rec[aá]mara|habitaci|dormitorio)", html, re.IGNORECASE)
            if m:
                prop.bedrooms = int(m.group(1))
        if prop.bathrooms is None:
            m = re.search(r"(\d+)\s*(?:bath|ba[ñn]o)", html, re.IGNORECASE)
            if m:
                prop.bathrooms = int(m.group(1))
        if not prop.area_m2:
            m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|metros)", html, re.IGNORECASE)
            if m:
                try:
                    prop.area_m2 = float(m.group(1).replace(",", ""))
                except ValueError:
                    pass

        return prop

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 20,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape listings from CityMax El Salvador."""

        for path in LISTING_PATHS:
            logger.info(f"[{self.source_name}] Trying: {BASE_URL}{path}")

            for page_num in range(1, max_pages + 1):
                if page_num == 1:
                    url = f"{BASE_URL}{path}"
                else:
                    url = f"{BASE_URL}{path}?page={page_num}"

                resp = await self.fetch(url)
                if not resp or resp.status_code == 404:
                    break

                properties = await self._parse_listing_page(resp.text, url)

                if not properties:
                    if page_num == 1:
                        logger.info(f"[{self.source_name}] No listings at {path}, trying next")
                        break
                    else:
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

                logger.info(f"[{self.source_name}] Page {page_num}: {len(properties)} listings")
                await asyncio.sleep(1.5)

            if self._seen_urls:
                break
