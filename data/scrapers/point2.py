"""
Point2 Homes — El Salvador Property Scraper
=============================================
Scrapes real estate listings from point2homes.com/SV.

Point2 is a US-based aggregator with clean HTML structure,
paginated results, and good structured data.

URL patterns:
  - All:  /SV/Real-Estate-Listings.html
  Pagination: /SV/Real-Estate-Listings.html/p{page}
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

BASE_URL = "https://www.point2homes.com"


class Point2Scraper(BaseScraper):
    """Scrapes property listings from Point2 Homes."""

    source_name = "point2"
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

    async def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedProperty]:
        """Parse a Point2 listing page."""
        properties = []

        try:
            from selectolax.parser import HTMLParser
            tree = HTMLParser(html)

            # Point2 uses .item-listing or similar card classes
            cards = tree.css(".item-listing, .listing-item, .property-item, .ic-property, article[class*='listing']")
            if not cards:
                cards = tree.css("a[href*='Real-Estate'], a[href*='listing']")

            for card in cards:
                try:
                    link_el = card.css_first("a[href]") if card.tag != "a" else card
                    if not link_el:
                        continue
                    href = link_el.attributes.get("href", "")
                    if not href or len(href) < 10:
                        continue
                    detail_url = urljoin(page_url, href)

                    # Skip navigation/pagination links
                    if any(skip in detail_url.lower() for skip in ["/blog", "/about", "/contact", "page=", "/p/"]):
                        continue

                    title_el = card.css_first("h2, h3, .item-title, [class*='title'], [class*='name'], .address")
                    title = title_el.text(strip=True) if title_el else ""

                    price_el = card.css_first("[class*='price'], .item-price, [data-price]")
                    price_text = price_el.text(strip=True) if price_el else ""
                    price_usd, price_raw = self._parse_price(price_text)

                    loc_el = card.css_first("[class*='address'], [class*='location'], .item-address")
                    location = loc_el.text(strip=True) if loc_el else title
                    department = self._resolve_department(location)

                    bedrooms = None
                    bathrooms = None
                    area_m2 = None

                    for spec in card.css("[class*='spec'], [class*='detail'], .ic-beds, .ic-baths, .ic-sqft, li, span"):
                        text = spec.text(strip=True).lower()
                        bed_m = re.search(r"(\d+)\s*(?:bed|bd|rec|hab)", text)
                        if bed_m:
                            bedrooms = int(bed_m.group(1))
                        bath_m = re.search(r"(\d+)\s*(?:bath|ba|bañ)", text)
                        if bath_m:
                            bathrooms = int(bath_m.group(1))
                        area_m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:m²|m2|sq\s*ft|sqft)", text)
                        if area_m:
                            val = float(area_m.group(1).replace(",", ""))
                            if "sq" in text and "ft" in text:
                                val = round(val * 0.0929, 2)  # sqft to m²
                            area_m2 = val

                    prop_type = ""
                    combined = (title + " " + detail_url).lower()
                    for keyword, ptype in [("house", "house"), ("casa", "house"),
                                           ("apartment", "apartment"), ("condo", "apartment"),
                                           ("land", "land"), ("lot", "land"), ("terreno", "land"),
                                           ("commercial", "commercial"), ("office", "commercial")]:
                        if keyword in combined:
                            prop_type = ptype
                            break

                    images = []
                    for img in card.css("img[src], img[data-src], img[data-lazy-src]"):
                        src = img.attributes.get("data-lazy-src") or img.attributes.get("data-src") or img.attributes.get("src", "")
                        if src and "placeholder" not in src and "logo" not in src and "icon" not in src:
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
            links = re.findall(
                r'href=["\']([^"\']*(?:Real-Estate|listing|property)[^"\']*\.html)["\']',
                html, re.IGNORECASE,
            )
            seen = set()
            for href in links:
                url = urljoin(page_url, href)
                if url in seen or url == page_url:
                    continue
                seen.add(url)
                prop = ScrapedProperty(
                    title="Property listing",
                    source=self.source_name,
                    source_url=url,
                    department=self._resolve_department(url),
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
        jsonld_matches = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, re.DOTALL | re.IGNORECASE,
        )
        for match in jsonld_matches:
            try:
                ld = json.loads(match)
                if isinstance(ld, list):
                    ld = ld[0]
                if ld.get("@type") not in ("Product", "RealEstateListing", "Residence",
                                            "House", "Apartment", "SingleFamilyResidence"):
                    continue

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
                break
            except (json.JSONDecodeError, KeyError, IndexError):
                continue

        # Description
        if not prop.description:
            desc_match = re.search(
                r'(?:class=["\'][^"\']*(?:description|details-text|property-description)[^"\']*["\'][^>]*>)\s*(.*?)\s*</(?:div|p)',
                html, re.DOTALL | re.IGNORECASE,
            )
            if desc_match:
                prop.description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()[:2000]

        return prop

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 15,
        fetch_details: bool = True,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """Scrape listings from Point2 Homes."""

        for page_num in range(1, max_pages + 1):
            if page_num == 1:
                url = f"{BASE_URL}/SV/Real-Estate-Listings.html"
            else:
                url = f"{BASE_URL}/SV/Real-Estate-Listings.html/p{page_num}"

            logger.info(f"[point2] Page {page_num}: {url}")

            resp = await self.fetch(url)
            if not resp:
                logger.warning(f"[point2] Failed page {page_num}, stopping")
                break

            if resp.status_code == 404:
                break

            properties = await self._parse_listing_page(resp.text, url)

            if not properties:
                logger.info(f"[point2] No properties on page {page_num}, done")
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

            logger.info(f"[point2] Page {page_num}: {len(properties)} listings")
            await asyncio.sleep(1.5)
