"""
Bank Foreclosures (Bienes Adjudicados) — El Salvador
======================================================
Scrapes repossessed property listings from major Salvadoran banks.

Banks publish "bienes adjudicados" or "activos extraordinarios" — 
repossessed real estate priced by bank appraisers at assessed values.
These are high-quality price signals for the valuation model because
they reflect actual appraised values rather than aspirational asking prices.

Supported banks:
  - Banco Agrícola (largest bank in El Salvador)
  - Banco Cuscatlán
  - Banco Promerica
  - Davivienda El Salvador

Legal: All listings are publicly available on bank websites, 
no authentication required. We respect robots.txt and rate-limit.
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

# ── Department resolution ────────────────────────────

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
    "soyapango": "San Salvador",
    "mejicanos": "San Salvador",
    "apopa": "San Salvador",
    "ilopango": "San Salvador",
    "ciudad delgado": "San Salvador",
    "san marcos": "San Salvador",
    "ayutuxtepeque": "San Salvador",
    "cuscatancingo": "San Salvador",
    "tonacatepeque": "San Salvador",
    "san martin": "San Salvador",
    "san martín": "San Salvador",
    "colón": "La Libertad",
    "colon": "La Libertad",
    "zaragoza": "La Libertad",
    "quezaltepeque": "La Libertad",
    "metapan": "Santa Ana",
    "metapán": "Santa Ana",
    "sensuntepeque": "Cabañas",
    "zacatecoluca": "La Paz",
}


def _resolve_department(text: str) -> str:
    """Resolve department from location text."""
    text_lower = text.lower()
    for keyword, name in DEPARTMENT_KEYWORDS.items():
        if keyword in text_lower:
            return name
    return ""


def _parse_price(text: str) -> tuple[float | None, str]:
    """Parse USD price from text."""
    if not text:
        return None, ""
    text = text.strip()
    clean = re.sub(r"[^\d.]", "", text.replace(",", ""))
    try:
        price = float(clean)
        return (price, text) if price > 0 else (None, text)
    except (ValueError, TypeError):
        return None, text


def _parse_area(text: str) -> float | None:
    """Parse area in m² from text. Converts varas² to m² if needed."""
    if not text:
        return None
    # Try m² first
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|mts²|metros)", text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    # Try varas²
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:v²|v2|varas)", text, re.IGNORECASE)
    if m:
        try:
            return round(float(m.group(1).replace(",", "")) * 0.6987, 2)
        except ValueError:
            pass
    return None


# ══════════════════════════════════════════════════════
# Banco Agrícola
# ══════════════════════════════════════════════════════

class BancoAgricolaScraper(BaseScraper):
    """
    Scrapes repossessed properties from Banco Agrícola.
    
    Banco Agrícola is the largest bank in El Salvador (Bancolombia Group).
    They publish bienes adjudicados on their website. Listings are typically
    structured HTML pages with property cards showing price, location,
    area, and basic specs.
    
    URL: https://www.bancoagricola.com/bienes-adjudicados
    """

    source_name = "banco_agricola"
    base_url = "https://www.bancoagricola.com"
    requests_per_second = 0.3  # Very conservative — bank site

    # Known listing page paths (banks sometimes restructure)
    LISTING_PATHS = [
        "/bienes-adjudicados",
        "/bienes-adjudicados/inmuebles",
        "/activos-extraordinarios",
    ]

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse a bank foreclosure listing page."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            # Bank sites use varied card layouts — try multiple selectors
            cards = tree.css(
                ".bien-item, .property-card, .listing-card, .card, "
                "[class*='bien'], [class*='activo'], [class*='inmueble'], "
                "[class*='propiedad'], article, .item, .result-item, "
                "tr[class], .row[class*='bien'], [data-id]"
            )

            # If no cards found, try table rows (banks often use tables)
            if not cards:
                cards = tree.css("table tbody tr")

            # If still no cards, try broad container divs with links
            if not cards:
                cards = tree.css(
                    "a[href*='bien'], a[href*='activo'], a[href*='inmueble'], "
                    "a[href*='propiedad'], a[href*='detalle']"
                )

            for card in cards:
                try:
                    # Extract link
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    href = ""
                    if link_el:
                        href = link_el.attributes.get("href", "")

                    detail_url = urljoin(page_url, href) if href else page_url

                    # Skip navigation links
                    if any(skip in detail_url.lower() for skip in [
                        "/contacto", "/nosotros", "/login", "/registro",
                        "javascript:", "#", "/buscar", "/sucursales",
                        "/productos", "/servicios", "/personas", "/empresas",
                    ]):
                        continue

                    # Title
                    title_el = card.css_first(
                        "h2, h3, h4, h5, [class*='title'], [class*='titulo'], "
                        "[class*='nombre'], strong, b"
                    )
                    title = title_el.text(strip=True) if title_el else ""

                    # Price  
                    price_el = card.css_first(
                        "[class*='precio'], [class*='price'], [class*='valor'], "
                        "[class*='monto'], [data-price]"
                    )
                    price_text = price_el.text(strip=True) if price_el else ""
                    if not price_text:
                        # Try to find price in any element with $ sign
                        for el in card.css("span, p, td, div"):
                            t = el.text(strip=True)
                            if "$" in t and re.search(r"\d", t):
                                price_text = t
                                break
                    price_usd, price_raw = _parse_price(price_text)

                    # Location
                    loc_el = card.css_first(
                        "[class*='ubicacion'], [class*='location'], "
                        "[class*='direccion'], [class*='address'], "
                        "[class*='departamento'], [class*='zona']"
                    )
                    location = loc_el.text(strip=True) if loc_el else ""
                    if not location:
                        # Scan all text elements for department keywords
                        for el in card.css("span, p, td, small, div"):
                            t = el.text(strip=True)
                            if _resolve_department(t):
                                location = t
                                break

                    department = _resolve_department(location) or _resolve_department(title)

                    # Specs
                    bedrooms = None
                    bathrooms = None
                    area_m2 = None

                    full_text = card.text(strip=True).lower() if card.text(strip=True) else ""
                    bed_m = re.search(r"(\d+)\s*(?:rec[aá]mara|habitaci[oó]n|dormitorio|cuarto|bedroom|bed)", full_text)
                    if bed_m:
                        bedrooms = int(bed_m.group(1))
                    bath_m = re.search(r"(\d+)\s*(?:ba[ñn]o|bathroom|bath|sanitario)", full_text)
                    if bath_m:
                        bathrooms = int(bath_m.group(1))
                    area_m2 = _parse_area(full_text)

                    # Property type
                    prop_type = self._guess_type(title + " " + full_text)

                    # Images
                    images = []
                    for img in card.css("img[src], img[data-src], img[data-lazy-src]"):
                        src = (
                            img.attributes.get("data-lazy-src")
                            or img.attributes.get("data-src")
                            or img.attributes.get("src", "")
                        )
                        if src and not any(skip in src.lower() for skip in [
                            "placeholder", "logo", "icon", "no-image", "banner",
                            "spinner", "loading", "avatar"
                        ]):
                            images.append(urljoin(page_url, src))

                    # Must have at least title or price to be a valid listing
                    if not title and not price_usd:
                        continue

                    prop = ScrapedProperty(
                        title=title or f"Bien Adjudicado — {location or 'El Salvador'}",
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
                        features=["foreclosure", "bienes_adjudicados", "banco_agricola"],
                    )
                    properties.append(prop)

                except Exception as e:
                    logger.debug(f"Error parsing card: {e}")
                    continue

        except ImportError:
            # Regex fallback for when selectolax is not installed
            links = re.findall(
                r'href=["\']([^"\']*(?:bien|activo|inmueble|propiedad|detalle)[^"\']*)["\']',
                html, re.IGNORECASE,
            )
            seen = set()
            for href in links:
                url = urljoin(page_url, href)
                if url in seen:
                    continue
                seen.add(url)
                prop = ScrapedProperty(
                    title="Bien Adjudicado — Banco Agrícola",
                    source=self.source_name,
                    source_url=url,
                    department=_resolve_department(url),
                    features=["foreclosure", "bienes_adjudicados", "banco_agricola"],
                )
                properties.append(prop)

        return properties

    def _guess_type(self, text: str) -> str:
        text_lower = text.lower()
        for keyword, ptype in [
            ("casa", "house"), ("house", "house"), ("vivienda", "house"),
            ("residencia", "house"), ("chalet", "house"),
            ("apartamento", "apartment"), ("apartment", "apartment"), ("apto", "apartment"),
            ("terreno", "land"), ("land", "land"), ("lote", "land"), ("finca", "land"),
            ("local", "commercial"), ("oficina", "commercial"), ("bodega", "commercial"),
            ("commercial", "commercial"), ("nave", "commercial"), ("galera", "commercial"),
        ]:
            if keyword in text_lower:
                return ptype
        return ""

    async def _enrich_from_detail(self, prop: ScrapedProperty) -> ScrapedProperty:
        """Fetch detail page and extract additional fields."""
        resp = await self.fetch(prop.source_url)
        if not resp:
            return prop

        html = resp.text

        # Attempt JSON-LD extraction
        jsonld_match = re.search(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.DOTALL | re.IGNORECASE,
        )
        if jsonld_match:
            try:
                ld = json.loads(jsonld_match.group(1))
                if isinstance(ld, list):
                    ld = ld[0]
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
                        prop.images = imgs[:8]
            except (json.JSONDecodeError, KeyError):
                pass

        # Description from page content
        if not prop.description:
            desc_match = re.search(
                r'(?:class=["\'][^"\']*(?:descripci[oó]n|description|detalle|contenido)[^"\']*["\'][^>]*>)\s*(.*?)\s*</(?:div|p|section)',
                html, re.DOTALL | re.IGNORECASE,
            )
            if desc_match:
                prop.description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()[:2000]

        # Specs fallback from detail page
        if prop.bedrooms is None:
            m = re.search(r"(\d+)\s*(?:rec[aá]mara|habitaci|dormitorio|cuarto|bedroom)", html, re.IGNORECASE)
            if m:
                prop.bedrooms = int(m.group(1))
        if prop.bathrooms is None:
            m = re.search(r"(\d+)\s*(?:ba[ñn]o|bathroom|sanitario)", html, re.IGNORECASE)
            if m:
                prop.bathrooms = int(m.group(1))
        if not prop.area_m2:
            prop.area_m2 = _parse_area(html)

        # Additional images from detail page
        if not prop.images or len(prop.images) < 2:
            img_urls = re.findall(
                r'(?:src|data-src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\']',
                html, re.IGNORECASE,
            )
            new_images = [
                urljoin(prop.source_url, u)
                for u in img_urls
                if not any(skip in u.lower() for skip in [
                    "logo", "icon", "placeholder", "banner", "avatar", "spinner"
                ])
            ][:8]
            if len(new_images) > len(prop.images):
                prop.images = new_images

        return prop

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 10,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape foreclosure listings from Banco Agrícola."""

        for path in self.LISTING_PATHS:
            logger.info(f"[{self.source_name}] Trying: {self.base_url}{path}")

            for page_num in range(1, max_pages + 1):
                if page_num == 1:
                    url = f"{self.base_url}{path}"
                else:
                    url = f"{self.base_url}{path}?page={page_num}"

                resp = await self.fetch(url)
                if not resp:
                    logger.info(f"[{self.source_name}] No response for {path}, trying next path")
                    break

                if resp.status_code == 404:
                    logger.info(f"[{self.source_name}] 404 for {path}, trying next path")
                    break

                properties = await self._parse_listing_page(resp.text, url)

                if not properties:
                    if page_num == 1:
                        logger.info(f"[{self.source_name}] No listings found at {path}")
                        break
                    else:
                        logger.info(f"[{self.source_name}] No more listings on page {page_num}")
                        break

                for prop in properties:
                    if department and prop.department and prop.department != department:
                        continue
                    if prop.source_url in self._seen_urls:
                        continue
                    self._seen_urls.add(prop.source_url)

                    if fetch_details and prop.source_url != url:
                        prop = await self._enrich_from_detail(prop)

                    yield prop

                logger.info(f"[{self.source_name}] Page {page_num}: {len(properties)} foreclosures")
                await asyncio.sleep(2)  # Extra polite to bank sites


# ══════════════════════════════════════════════════════
# Banco Cuscatlán
# ══════════════════════════════════════════════════════

class BancoCuscatlanScraper(BaseScraper):
    """
    Scrapes repossessed properties from Banco Cuscatlán.
    URL: https://www.bancocuscatlan.com/bienes-adjudicados
    """

    source_name = "banco_cuscatlan"
    base_url = "https://www.bancocuscatlan.com"
    requests_per_second = 0.3

    LISTING_PATHS = [
        "/bienes-adjudicados",
        "/bienes-en-venta",
        "/activos-extraordinarios",
    ]

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse listings from Banco Cuscatlán."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            cards = tree.css(
                ".bien-item, .property-card, .listing-card, .card, "
                "[class*='bien'], [class*='activo'], [class*='inmueble'], "
                "article, .item, tr[class], [data-id], "
                ".row[class*='bien'], .grid-item"
            )

            if not cards:
                cards = tree.css("table tbody tr")

            if not cards:
                cards = tree.css(
                    "a[href*='bien'], a[href*='activo'], a[href*='inmueble']"
                )

            for card in cards:
                try:
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    href = ""
                    if link_el:
                        href = link_el.attributes.get("href", "")
                    detail_url = urljoin(page_url, href) if href else page_url

                    if any(skip in detail_url.lower() for skip in [
                        "/contacto", "/nosotros", "/login", "/registro",
                        "javascript:", "#", "/sucursales", "/productos",
                    ]):
                        continue

                    title_el = card.css_first("h2, h3, h4, h5, [class*='title'], [class*='titulo'], strong")
                    title = title_el.text(strip=True) if title_el else ""

                    price_text = ""
                    price_el = card.css_first("[class*='precio'], [class*='price'], [class*='valor']")
                    if price_el:
                        price_text = price_el.text(strip=True)
                    else:
                        for el in card.css("span, p, td, div"):
                            t = el.text(strip=True)
                            if "$" in t and re.search(r"\d", t):
                                price_text = t
                                break
                    price_usd, price_raw = _parse_price(price_text)

                    loc_el = card.css_first(
                        "[class*='ubicacion'], [class*='location'], "
                        "[class*='direccion'], [class*='departamento']"
                    )
                    location = loc_el.text(strip=True) if loc_el else ""
                    if not location:
                        for el in card.css("span, p, td, small"):
                            t = el.text(strip=True)
                            if _resolve_department(t):
                                location = t
                                break

                    department = _resolve_department(location) or _resolve_department(title)

                    full_text = card.text(strip=True).lower()
                    bedrooms = None
                    bathrooms = None
                    bed_m = re.search(r"(\d+)\s*(?:rec[aá]mara|habitaci|dormitorio|cuarto|bed)", full_text)
                    if bed_m:
                        bedrooms = int(bed_m.group(1))
                    bath_m = re.search(r"(\d+)\s*(?:ba[ñn]o|bath|sanitario)", full_text)
                    if bath_m:
                        bathrooms = int(bath_m.group(1))
                    area_m2 = _parse_area(full_text)

                    prop_type = _guess_property_type(title + " " + full_text)

                    images = []
                    for img in card.css("img[src], img[data-src]"):
                        src = img.attributes.get("data-src") or img.attributes.get("src", "")
                        if src and not any(s in src.lower() for s in ["logo", "icon", "placeholder", "banner"]):
                            images.append(urljoin(page_url, src))

                    if not title and not price_usd:
                        continue

                    prop = ScrapedProperty(
                        title=title or f"Bien Adjudicado — {location or 'El Salvador'}",
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
                        features=["foreclosure", "bienes_adjudicados", "banco_cuscatlan"],
                    )
                    properties.append(prop)
                except Exception as e:
                    logger.debug(f"Error parsing card: {e}")
                    continue

        except ImportError:
            links = re.findall(
                r'href=["\']([^"\']*(?:bien|activo|inmueble)[^"\']*)["\']',
                html, re.IGNORECASE,
            )
            for href in set(links):
                url = urljoin(page_url, href)
                prop = ScrapedProperty(
                    title="Bien Adjudicado — Banco Cuscatlán",
                    source=self.source_name,
                    source_url=url,
                    features=["foreclosure", "bienes_adjudicados", "banco_cuscatlan"],
                )
                properties.append(prop)

        return properties

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 10,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape foreclosure listings from Banco Cuscatlán."""

        for path in self.LISTING_PATHS:
            logger.info(f"[{self.source_name}] Trying: {self.base_url}{path}")

            for page_num in range(1, max_pages + 1):
                url = f"{self.base_url}{path}" if page_num == 1 else f"{self.base_url}{path}?page={page_num}"

                resp = await self.fetch(url)
                if not resp or resp.status_code == 404:
                    break

                properties = await self._parse_listing_page(resp.text, url)
                if not properties:
                    break

                for prop in properties:
                    if department and prop.department and prop.department != department:
                        continue
                    if prop.source_url in self._seen_urls:
                        continue
                    self._seen_urls.add(prop.source_url)
                    yield prop

                logger.info(f"[{self.source_name}] Page {page_num}: {len(properties)} foreclosures")
                await asyncio.sleep(2)


# ══════════════════════════════════════════════════════
# Banco Promerica
# ══════════════════════════════════════════════════════

class BancoPromericaScraper(BaseScraper):
    """
    Scrapes repossessed properties from Banco Promerica El Salvador.
    URL: https://www.promerica.com.sv/bienes-en-venta
    """

    source_name = "banco_promerica"
    base_url = "https://www.promerica.com.sv"
    requests_per_second = 0.3

    LISTING_PATHS = [
        "/bienes-en-venta",
        "/bienes-adjudicados",
        "/activos-extraordinarios",
    ]

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse listings from Banco Promerica."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            cards = tree.css(
                ".bien-item, .property-card, .card, "
                "[class*='bien'], [class*='activo'], [class*='inmueble'], "
                "article, .item, tr[class], [data-id], .grid-item"
            )
            if not cards:
                cards = tree.css("table tbody tr")
            if not cards:
                cards = tree.css("a[href*='bien'], a[href*='activo'], a[href*='inmueble']")

            for card in cards:
                try:
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    href = link_el.attributes.get("href", "") if link_el else ""
                    detail_url = urljoin(page_url, href) if href else page_url

                    if any(skip in detail_url.lower() for skip in [
                        "/contacto", "/login", "javascript:", "#", "/sucursales",
                    ]):
                        continue

                    title_el = card.css_first("h2, h3, h4, h5, [class*='title'], [class*='titulo'], strong")
                    title = title_el.text(strip=True) if title_el else ""

                    price_text = ""
                    price_el = card.css_first("[class*='precio'], [class*='price'], [class*='valor']")
                    if price_el:
                        price_text = price_el.text(strip=True)
                    else:
                        for el in card.css("span, p, td"):
                            t = el.text(strip=True)
                            if "$" in t and re.search(r"\d", t):
                                price_text = t
                                break
                    price_usd, price_raw = _parse_price(price_text)

                    loc_el = card.css_first("[class*='ubicacion'], [class*='direccion'], [class*='location']")
                    location = loc_el.text(strip=True) if loc_el else ""
                    if not location:
                        for el in card.css("span, p, td, small"):
                            t = el.text(strip=True)
                            if _resolve_department(t):
                                location = t
                                break

                    department = _resolve_department(location) or _resolve_department(title)

                    full_text = card.text(strip=True).lower()
                    bedrooms = None
                    bathrooms = None
                    bed_m = re.search(r"(\d+)\s*(?:rec[aá]mara|habitaci|dormitorio|bed)", full_text)
                    if bed_m:
                        bedrooms = int(bed_m.group(1))
                    bath_m = re.search(r"(\d+)\s*(?:ba[ñn]o|bath)", full_text)
                    if bath_m:
                        bathrooms = int(bath_m.group(1))
                    area_m2 = _parse_area(full_text)

                    prop_type = _guess_property_type(title + " " + full_text)

                    images = []
                    for img in card.css("img[src], img[data-src]"):
                        src = img.attributes.get("data-src") or img.attributes.get("src", "")
                        if src and "logo" not in src.lower() and "icon" not in src.lower():
                            images.append(urljoin(page_url, src))

                    if not title and not price_usd:
                        continue

                    prop = ScrapedProperty(
                        title=title or f"Bien Adjudicado — {location or 'El Salvador'}",
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
                        features=["foreclosure", "bienes_adjudicados", "banco_promerica"],
                    )
                    properties.append(prop)
                except Exception as e:
                    logger.debug(f"Error parsing card: {e}")
                    continue

        except ImportError:
            pass

        return properties

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 10,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape foreclosure listings from Banco Promerica."""

        for path in self.LISTING_PATHS:
            logger.info(f"[{self.source_name}] Trying: {self.base_url}{path}")

            for page_num in range(1, max_pages + 1):
                url = f"{self.base_url}{path}" if page_num == 1 else f"{self.base_url}{path}?page={page_num}"

                resp = await self.fetch(url)
                if not resp or resp.status_code == 404:
                    break

                properties = await self._parse_listing_page(resp.text, url)
                if not properties:
                    break

                for prop in properties:
                    if department and prop.department and prop.department != department:
                        continue
                    if prop.source_url in self._seen_urls:
                        continue
                    self._seen_urls.add(prop.source_url)
                    yield prop

                logger.info(f"[{self.source_name}] Page {page_num}: {len(properties)} foreclosures")
                await asyncio.sleep(2)


# ══════════════════════════════════════════════════════
# Davivienda El Salvador
# ══════════════════════════════════════════════════════

class DaviviendaScraper(BaseScraper):
    """
    Scrapes repossessed properties from Davivienda El Salvador.
    URL: https://www.davivienda.com.sv/bienes-adjudicados
    """

    source_name = "davivienda"
    base_url = "https://www.davivienda.com.sv"
    requests_per_second = 0.3

    LISTING_PATHS = [
        "/bienes-adjudicados",
        "/bienes-en-venta",
        "/activos-extraordinarios",
        "/activos-especiales",
    ]

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse listings from Davivienda."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            cards = tree.css(
                ".bien-item, .property-card, .card, "
                "[class*='bien'], [class*='activo'], [class*='inmueble'], "
                "article, .item, tr[class], .grid-item"
            )
            if not cards:
                cards = tree.css("table tbody tr")
            if not cards:
                cards = tree.css("a[href*='bien'], a[href*='activo'], a[href*='inmueble']")

            for card in cards:
                try:
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    href = link_el.attributes.get("href", "") if link_el else ""
                    detail_url = urljoin(page_url, href) if href else page_url

                    if any(skip in detail_url.lower() for skip in [
                        "/contacto", "/login", "javascript:", "#", "/sucursales",
                    ]):
                        continue

                    title_el = card.css_first("h2, h3, h4, h5, [class*='title'], [class*='titulo'], strong")
                    title = title_el.text(strip=True) if title_el else ""

                    price_text = ""
                    price_el = card.css_first("[class*='precio'], [class*='price'], [class*='valor']")
                    if price_el:
                        price_text = price_el.text(strip=True)
                    else:
                        for el in card.css("span, p, td"):
                            t = el.text(strip=True)
                            if "$" in t and re.search(r"\d", t):
                                price_text = t
                                break
                    price_usd, price_raw = _parse_price(price_text)

                    loc_el = card.css_first("[class*='ubicacion'], [class*='direccion'], [class*='location']")
                    location = loc_el.text(strip=True) if loc_el else ""
                    if not location:
                        for el in card.css("span, p, td, small"):
                            t = el.text(strip=True)
                            if _resolve_department(t):
                                location = t
                                break

                    department = _resolve_department(location) or _resolve_department(title)

                    full_text = card.text(strip=True).lower()
                    bedrooms = None
                    bathrooms = None
                    bed_m = re.search(r"(\d+)\s*(?:rec[aá]mara|habitaci|dormitorio|bed)", full_text)
                    if bed_m:
                        bedrooms = int(bed_m.group(1))
                    bath_m = re.search(r"(\d+)\s*(?:ba[ñn]o|bath)", full_text)
                    if bath_m:
                        bathrooms = int(bath_m.group(1))
                    area_m2 = _parse_area(full_text)

                    prop_type = _guess_property_type(title + " " + full_text)

                    images = []
                    for img in card.css("img[src], img[data-src]"):
                        src = img.attributes.get("data-src") or img.attributes.get("src", "")
                        if src and "logo" not in src.lower() and "icon" not in src.lower():
                            images.append(urljoin(page_url, src))

                    if not title and not price_usd:
                        continue

                    prop = ScrapedProperty(
                        title=title or f"Bien Adjudicado — {location or 'El Salvador'}",
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
                        features=["foreclosure", "bienes_adjudicados", "davivienda"],
                    )
                    properties.append(prop)
                except Exception as e:
                    logger.debug(f"Error parsing card: {e}")
                    continue

        except ImportError:
            pass

        return properties

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 10,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape foreclosure listings from Davivienda."""

        for path in self.LISTING_PATHS:
            logger.info(f"[{self.source_name}] Trying: {self.base_url}{path}")

            for page_num in range(1, max_pages + 1):
                url = f"{self.base_url}{path}" if page_num == 1 else f"{self.base_url}{path}?page={page_num}"

                resp = await self.fetch(url)
                if not resp or resp.status_code == 404:
                    break

                properties = await self._parse_listing_page(resp.text, url)
                if not properties:
                    break

                for prop in properties:
                    if department and prop.department and prop.department != department:
                        continue
                    if prop.source_url in self._seen_urls:
                        continue
                    self._seen_urls.add(prop.source_url)
                    yield prop

                logger.info(f"[{self.source_name}] Page {page_num}: {len(properties)} foreclosures")
                await asyncio.sleep(2)


# ══════════════════════════════════════════════════════
# Shared helper
# ══════════════════════════════════════════════════════

def _guess_property_type(text: str) -> str:
    """Guess property type from text."""
    text_lower = text.lower()
    for keyword, ptype in [
        ("casa", "house"), ("house", "house"), ("vivienda", "house"),
        ("residencia", "house"), ("chalet", "house"),
        ("apartamento", "apartment"), ("apartment", "apartment"), ("apto", "apartment"),
        ("terreno", "land"), ("land", "land"), ("lote", "land"), ("finca", "land"),
        ("local", "commercial"), ("oficina", "commercial"), ("bodega", "commercial"),
        ("commercial", "commercial"), ("nave", "commercial"), ("galera", "commercial"),
    ]:
        if keyword in text_lower:
            return ptype
    return ""


# ══════════════════════════════════════════════════════
# Unified runner
# ══════════════════════════════════════════════════════

ALL_BANK_SCRAPERS = [
    ("Banco Agrícola", BancoAgricolaScraper),
    ("Banco Cuscatlán", BancoCuscatlanScraper),
    ("Banco Promerica", BancoPromericaScraper),
    ("Davivienda", DaviviendaScraper),
]


async def scrape_all_banks(
    department: str | None = None,
    max_pages: int = 10,
    fetch_details: bool = True,
) -> list[ScrapedProperty]:
    """Run all bank foreclosure scrapers and return combined results."""
    all_properties = []

    for bank_name, scraper_cls in ALL_BANK_SCRAPERS:
        logger.info(f"\n{'─' * 40}")
        logger.info(f"Scraping: {bank_name}")
        logger.info(f"{'─' * 40}")

        try:
            scraper = scraper_cls()
            async with scraper:
                async for prop in scraper.scrape_listings(
                    department=department,
                    max_pages=max_pages,
                    fetch_details=fetch_details,
                ):
                    all_properties.append(prop)
        except Exception as e:
            logger.error(f"[{bank_name}] Scraper failed: {e}")
            continue

    logger.info(f"\nTotal bank foreclosures collected: {len(all_properties)}")
    return all_properties
