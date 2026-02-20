"""
Properstar — El Salvador Property Scraper
============================================
Scrapes real estate listings from properstar.com/el-salvador.

Properstar is an aggregator that pulls from multiple international
MLS feeds. Server-rendered HTML, clean structure.

URL patterns:
  - Buy:  /el-salvador/buy
  - Rent: /el-salvador/rent
  Pagination: ?page=1, ?page=2, ...
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

BASE_URL = "https://www.properstar.com"


class ProperstarScraper(BaseScraper):
    """Scrapes property listings from Properstar."""

    source_name = "properstar"
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

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse a Properstar listing page."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            cards = tree.css(".listing-card, .property-card, [class*='ListingCard'], [data-listing-id], article")
            if not cards:
                # Broader fallback
                cards = tree.css("a[href*='/listing/'], a[href*='/property/']")

            for card in cards:
                try:
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    if not link_el:
                        continue
                    href = link_el.attributes.get("href", "")
                    if not href:
                        continue
                    detail_url = urljoin(page_url, href)

                    # Skip non-listing links
                    if any(skip in detail_url for skip in ["/blog", "/about", "/contact", "/faq"]):
                        continue

                    title_el = card.css_first("h2, h3, [class*='title'], [class*='name']")
                    title = title_el.text(strip=True) if title_el else ""

                    price_el = card.css_first("[class*='price'], [data-price]")
                    price_text = price_el.text(strip=True) if price_el else ""
                    price_usd, price_raw = self._parse_price(price_text)

                    loc_el = card.css_first("[class*='location'], [class*='address'], [class*='city']")
                    location = loc_el.text(strip=True) if loc_el else ""
                    department = self._resolve_department(location) or self._resolve_department(title)

                    bedrooms = None
                    bathrooms = None
                    area_m2 = None

                    specs = card.css("[class*='spec'], [class*='detail'], [class*='feature'], span, li")
                    for spec in specs:
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
                                area_m2 = float(area_m.group(1).replace(",", ""))
                            except ValueError:
                                pass

                    prop_type = ""
                    for keyword, ptype in [("house", "house"), ("casa", "house"),
                                           ("apartment", "apartment"), ("apart", "apartment"),
                                           ("land", "land"), ("terreno", "land"),
                                           ("commercial", "commercial"), ("office", "commercial")]:
                        if keyword in (title + " " + detail_url).lower():
                            prop_type = ptype
                            break

                    images = []
                    for img in card.css("img[src], img[data-src]"):
                        src = img.attributes.get("data-src") or img.attributes.get("src", "")
                        if src and "placeholder" not in src and "logo" not in src:
                            images.append(urljoin(page_url, src))

                    prop = ScrapedProperty(
                        title=title or f"Property in {location or 'El Salvador'}",
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

        except ImportError:
            # Regex fallback
            detail_links = re.findall(
                r'href=["\']([^"\']*(?:/listing/|/property/)[^"\']*)["\']',
                html,
                re.IGNORECASE,
            )
            seen = set()
            for href in detail_links:
                url = urljoin(page_url, href)
                if url in seen:
                    continue
                seen.add(url)
                prop = ScrapedProperty(
                    title=f"Listing from {self.source_name}",
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
                              ("Product", "RealEstateListing", "Residence", "House", "Apartment")), ld[0])

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

                if "offers" in ld:
                    offer = ld["offers"] if isinstance(ld["offers"], dict) else ld["offers"][0]
                    try:
                        prop.price_usd = float(offer.get("price", 0))
                    except (ValueError, TypeError):
                        pass

            except (json.JSONDecodeError, KeyError, IndexError):
                pass

        # Description fallback
        if not prop.description:
            desc_match = re.search(
                r'(?:class=["\'][^"\']*description[^"\']*["\'][^>]*>)\s*(.*?)\s*</(?:div|p)',
                html, re.DOTALL | re.IGNORECASE,
            )
            if desc_match:
                prop.description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()[:2000]

        # Specs fallback
        if prop.bedrooms is None:
            m = re.search(r"(\d+)\s*(?:bed|rec|hab|dorm)", html, re.IGNORECASE)
            if m:
                prop.bedrooms = int(m.group(1))
        if prop.bathrooms is None:
            m = re.search(r"(\d+)\s*(?:bath|bañ)", html, re.IGNORECASE)
            if m:
                prop.bathrooms = int(m.group(1))
        if not prop.area_m2:
            m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2)", html, re.IGNORECASE)
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
        """Scrape listings from Properstar."""

        for page_num in range(1, max_pages + 1):
            url = f"{BASE_URL}/el-salvador/buy?page={page_num}"
            logger.info(f"[properstar] Page {page_num}: {url}")

            resp = await self.fetch(url)
            if not resp:
                logger.warning(f"[properstar] Failed page {page_num}, stopping")
                break

            if resp.status_code == 404:
                break

            properties = await self._parse_listing_page(resp.text, url)

            if not properties:
                logger.info(f"[properstar] No properties on page {page_num}, done")
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

            logger.info(f"[properstar] Page {page_num}: {len(properties)} listings")
            await asyncio.sleep(1.5)
