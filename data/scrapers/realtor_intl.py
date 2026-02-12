"""
Realtor.com International — El Salvador Scraper
=================================================
Scrapes property listings from realtor.com/international/sv/.
Uses Playwright for JavaScript-rendered pages.

Source characteristics:
  - ~22 pages x ~25 listings ≈ 500+ properties
  - Good structured data: price, bedrooms, bathrooms, area, property type
  - Detail pages have descriptions, images, agent info, coordinates
  - Cards wrapped in <a> tags with full listing URLs
  - Pagination: /international/sv/p{n}
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

from base import BaseScraper, ScrapedProperty, ScrapeResult

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────

BASE_URL = "https://www.realtor.com/international/sv/"
DETAIL_BASE = "https://www.realtor.com"

# Department name resolution from URL slugs
DEPARTMENT_KEYWORDS = {
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
    # Also match department suffixes from breadcrumbs
    "la-libertad-department": "La Libertad",
    "san-salvador-department": "San Salvador",
    "santa-ana-department": "Santa Ana",
    "san-miguel-department": "San Miguel",
    "sonsonate-department": "Sonsonate",
    "usulutan-department": "Usulután",
    "ahuachapan-department": "Ahuachapán",
    "la-paz-department": "La Paz",
    "la-union-department": "La Unión",
    "chalatenango-department": "Chalatenango",
    "cuscatlan-department": "Cuscatlán",
    "morazan-department": "Morazán",
    "san-vicente-department": "San Vicente",
    "cabanas-department": "Cabañas",
}

# Map English property type strings to our standard types
PROPERTY_TYPE_MAP = {
    "house": "house",
    "apartment": "apartment",
    "condo": "apartment",
    "condominium": "apartment",
    "land": "land",
    "lot": "land",
    "commercial": "commercial",
    "office": "commercial",
    "industrial": "commercial",
    "industrial/warehouse": "commercial",
    "warehouse": "commercial",
    "villa": "house",
    "townhouse": "house",
    "farm": "land",
    "ranch": "land",
}

SQ_FT_TO_M2 = 0.092903


def parse_price(text: str) -> float | None:
    """Extract numeric price from text like 'USD $2,700,000'."""
    if not text:
        return None
    m = re.search(r"[\$]?\s*([\d,]+(?:\.\d+)?)", text.replace(",", ""))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def parse_area_sqft(text: str) -> float | None:
    """Extract sq ft value and convert to m²."""
    if not text:
        return None
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*sq\s*ft", text, re.IGNORECASE)
    if m:
        try:
            sqft = float(m.group(1).replace(",", ""))
            return round(sqft * SQ_FT_TO_M2, 2)
        except ValueError:
            pass
    return None


def detect_property_type(text: str) -> str:
    """Detect property type from feature text."""
    lower = text.lower().strip().rstrip(".")
    for keyword, ptype in PROPERTY_TYPE_MAP.items():
        if keyword in lower:
            return ptype
    return ""


def extract_department(url: str, address: str) -> str:
    """Try to extract department from URL slug or address text."""
    combined = f"{url.lower()} {address.lower()}"
    # Check longest keys first to avoid partial matches
    for slug, dept in sorted(DEPARTMENT_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if slug in combined:
            return dept
    return ""


def extract_municipio(address: str) -> str:
    """
    Extract municipio from the address text.
    Format is usually: 'Title, Municipio, Department, ...'
    We take the second-to-last distinct location segment.
    """
    if not address:
        return ""
    parts = [p.strip() for p in address.split(",") if p.strip()]
    if len(parts) >= 3:
        # The second-to-last segment is usually the municipio
        return parts[-2]
    return ""


class RealtorInternationalScraper(BaseScraper):
    """
    Scraper for realtor.com/international/sv/ listings.
    Uses Playwright to render JavaScript-heavy pages.
    """

    source_name = "realtor_intl"
    base_url = "https://www.realtor.com/international/sv/"
    requests_per_second = 0.3  # Conservative: 1 request per 3 seconds

    def __init__(
        self,
        headless: bool = True,
        fetch_details: bool = True,
        max_detail_workers: int = 2,
    ):
        super().__init__()
        self.headless = headless
        self.fetch_details = fetch_details
        self.max_detail_workers = max_detail_workers
        self._browser = None
        self._context = None

    async def _launch_browser(self):
        """Launch Playwright Chromium with stealth settings."""
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        logger.info("Playwright browser launched")

    async def _close_browser(self):
        """Close browser and Playwright."""
        if self._browser:
            await self._browser.close()
        if hasattr(self, "_pw") and self._pw:
            await self._pw.stop()
        logger.info("Playwright browser closed")

    # ── Page Extraction ──────────────────────────────────

    async def _extract_listing_cards(self, page) -> list[dict]:
        """
        Extract all listing cards from a search results page.
        Each card is wrapped in an <a> tag with href to the detail page.
        returns list of dicts with: url, price_raw, title, beds, baths,
        area_sqft, property_type, images, tag.
        """
        await page.wait_for_timeout(3000)

        cards = await page.evaluate("""() => {
            const results = [];
            
            // Find all <a> links pointing to El Salvador listing detail pages
            const allLinks = document.querySelectorAll('a[href*="/international/sv/"]');
            
            for (const link of allLinks) {
                const href = link.href || '';
                
                // Only listing detail links (long URLs with property slugs)
                if (href.length < 80) continue;
                // Skip pagination links
                if (/\\/sv\\/p\\d+\\/?$/.test(href)) continue;
                
                // Walk up to find listing card wrapper
                let card = link;
                let depth = 0;
                while (card && depth < 5 && !card.className?.includes?.('listing-card')) {
                    card = card.parentElement;
                    depth++;
                }
                const container = (card && card.className?.includes?.('listing-card')) ? card : link;
                
                // Price
                const priceEl = container.querySelector('.displayListingPrice');
                const priceRaw = priceEl?.innerText?.trim() || '';
                
                // Features: typically [bedrooms, bathrooms, area, type]
                const featureEls = container.querySelectorAll('.feature-item');
                const features = Array.from(featureEls).map(f => f.innerText.trim());
                
                // Full text for fallback parsing
                const fullText = container.innerText.trim();
                
                // Images
                const imgs = container.querySelectorAll('img[src*="rea.global"]');
                const images = Array.from(imgs)
                    .map(img => {
                        let src = img.src || '';
                        if (src.startsWith('//')) src = 'https:' + src;
                        // Use larger image size
                        return src.replace('/400x320-fit/', '/800x600-fit/')
                                  .replace('/78x104-fit', '/800x600-fit');
                    })
                    .filter(s => s.includes('/sv/'));
                
                // Tag (LATEST, etc.)
                const tagEl = container.querySelector('[class*="new-tag"]');
                const tag = tagEl?.innerText?.trim() || '';
                
                results.push({
                    url: href,
                    priceRaw,
                    fullText: fullText.substring(0, 600),
                    features,
                    images,
                    tag,
                });
            }
            
            // Deduplicate by URL
            const seen = new Set();
            return results.filter(r => {
                if (seen.has(r.url)) return false;
                seen.add(r.url);
                return true;
            });
        }""")

        return cards

    def _parse_card(self, card: dict) -> ScrapedProperty | None:
        """Parse a raw card dict into a ScrapedProperty."""
        url = card.get("url", "")
        if not url:
            return None

        price_raw = card.get("priceRaw", "")
        price = parse_price(price_raw)
        features = card.get("features", [])
        full_text = card.get("fullText", "")
        images = card.get("images", [])

        # Parse features: numbers are beds/baths, "X sq ft" is area, text is type
        beds = None
        baths = None
        area_m2 = None
        property_type = ""
        area_sqft_raw = ""

        numeric_features = []
        for f in features:
            f_clean = f.strip().strip("|").strip()
            if not f_clean:
                continue

            # Check for area
            if "sq ft" in f_clean.lower():
                area_m2 = parse_area_sqft(f_clean)
                area_sqft_raw = f_clean
                continue

            # Check for property type keyword
            pt = detect_property_type(f_clean)
            if pt:
                property_type = pt
                continue

            # Numeric value → beds then baths
            try:
                val = int(f_clean)
                numeric_features.append(val)
            except ValueError:
                # Could be property type text
                pt = detect_property_type(f_clean)
                if pt:
                    property_type = pt

        if len(numeric_features) >= 1:
            beds = numeric_features[0]
        if len(numeric_features) >= 2:
            baths = numeric_features[1]

        # If property type not from features, try from full text
        if not property_type:
            for line in full_text.split("\n"):
                pt = detect_property_type(line.strip())
                if pt:
                    property_type = pt
                    break

        # Extract title from full text (address line, usually after price)
        title_lines = [
            ln.strip() for ln in full_text.split("\n")
            if ln.strip()
            and not ln.strip().startswith("USD")
            and not ln.strip().startswith("LATEST")
            and not ln.strip().startswith("BOOST")
            and not ln.strip().startswith("View")
            and not ln.strip() in ("...", "|")
            and not re.match(r"^\d+$", ln.strip())
            and "sq ft" not in ln.strip().lower()
            and not detect_property_type(ln.strip())
        ]
        address = title_lines[0] if title_lines else ""

        # Extract agent name (usually first line before price)
        agent_line = ""
        for ln in full_text.split("\n"):
            ln = ln.strip()
            if ln and not ln.startswith("USD") and not ln.startswith("LATEST") and len(ln) < 60:
                # Could be agent name if it comes before the price
                if "USD" in full_text[full_text.find(ln) + len(ln):full_text.find(ln) + len(ln) + 30]:
                    agent_line = ln
                break

        # Department + municipio from URL and address
        department = extract_department(url, address)
        municipio = extract_municipio(address)

        # Build title
        title = address if address else url.split("/sv/")[-1].rstrip("/").replace("-", " ").title()

        return ScrapedProperty(
            title=title,
            source=self.source_name,
            source_url=url,
            department=department,
            municipio=municipio,
            address=address,
            price_usd=price,
            price_raw=price_raw,
            property_type=property_type,
            bedrooms=beds,
            bathrooms=baths,
            area_m2=area_m2,
            images=images,
            features=features,
        )

    # ── Detail Page ──────────────────────────────────────

    async def _fetch_detail(self, prop: ScrapedProperty, page) -> ScrapedProperty:
        """Enrich a property with detail page data."""
        try:
            await self.rate_limiter.acquire()
            await page.goto(prop.source_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            detail = await page.evaluate("""() => {
                const r = {};
                
                // Title from h1
                r.title = document.querySelector('h1')?.innerText?.trim() || '';
                
                // Price
                r.price = '';
                const priceEls = document.querySelectorAll('[class*="price"], [class*="Price"]');
                for (const p of priceEls) {
                    const t = p.innerText.trim();
                    if (t.match(/USD|\\$|\\d{3}/)) { r.price = t; break; }
                }
                
                // Description
                r.description = '';
                const descEl = document.querySelector('.listing-description, .property-description');
                if (descEl) {
                    r.description = descEl.innerText.trim();
                } else {
                    // Fallback: find longest <p>
                    const ps = document.querySelectorAll('p');
                    for (const p of ps) {
                        const t = p.innerText.trim();
                        if (t.length > 100 && t.length > r.description.length) {
                            r.description = t;
                        }
                    }
                }
                
                // Images (all high-res)
                r.images = Array.from(document.querySelectorAll('img[src*="rea.global"]'))
                    .map(img => {
                        let src = img.src || '';
                        if (src.startsWith('//')) src = 'https:' + src;
                        return src;
                    })
                    .filter(s => s.includes('/sv/'));  
                
                // Features/specs
                r.features = Array.from(document.querySelectorAll('.feature-item'))
                    .map(f => f.innerText.trim());
                
                // Breadcrumbs for location
                r.breadcrumbs = Array.from(
                    document.querySelectorAll('[class*="breadcrumb"] a, nav a')
                ).map(a => a.innerText.trim()).filter(t => t.length > 0);
                
                // Agent
                r.agent = document.querySelector('.agent-name')?.innerText?.trim() || '';
                
                // Property ID
                const idEl = document.querySelector('.property-id, .listing-id');
                r.propertyId = idEl?.innerText?.trim() || '';
                
                // Key property info (land size, floor area, etc.)
                const basicInfos = document.querySelectorAll('.basicInfoKey, .basicInfoValue');
                r.keyInfo = {};
                for (let i = 0; i < basicInfos.length - 1; i += 2) {
                    const key = basicInfos[i]?.innerText?.trim();
                    const val = basicInfos[i + 1]?.innerText?.trim();
                    if (key && val) r.keyInfo[key] = val;
                }
                
                // Published / updated dates
                const bodyText = document.body.innerText;
                const pubMatch = bodyText.match(/Published on:\\s*(.+?)\\n/);
                const updMatch = bodyText.match(/Last updated on:\\s*(.+?)\\n/);
                r.publishedDate = pubMatch ? pubMatch[1].trim() : '';
                r.updatedDate = updMatch ? updMatch[1].trim() : '';
                
                return r;
            }""")

            # Merge detail data into property
            if detail.get("title"):
                prop.title = detail["title"]
            
            if detail.get("description"):
                # Description is in English (from the site) or Spanish
                desc = detail["description"]
                if any(c in desc for c in "áéíóúñ¿¡"):
                    prop.description_es = desc
                else:
                    prop.description = desc

            if detail.get("images"):
                prop.images = detail["images"][:20]  # Cap at 20

            if detail.get("features"):
                prop.features = detail["features"]

            # Parse key info for land/floor area
            key_info = detail.get("keyInfo", {})
            for key, val in key_info.items():
                key_l = key.lower()
                if "land" in key_l and "sq ft" in val.lower():
                    lot_m2 = parse_area_sqft(val)
                    if lot_m2:
                        prop.lot_size_m2 = lot_m2
                elif "floor" in key_l and "sq ft" in val.lower():
                    floor_m2 = parse_area_sqft(val)
                    if floor_m2:
                        prop.area_m2 = floor_m2

            # Parse listing date
            pub_date = detail.get("publishedDate", "")
            if pub_date:
                try:
                    prop.listing_date = datetime.strptime(pub_date, "%d %b %Y")
                except (ValueError, TypeError):
                    pass

            # Breadcrumb → department
            breadcrumbs = detail.get("breadcrumbs", [])
            for bc in breadcrumbs:
                dept = extract_department(bc.lower().replace(" ", "-"), "")
                if dept:
                    prop.department = dept
                    break

            logger.debug(f"  Detail enriched: {prop.title[:60]}")

        except Exception as e:
            logger.warning(f"  Detail fetch failed for {prop.source_url[:80]}: {e}")

        return prop

    # ── Main Scraping Logic ──────────────────────────────

    async def scrape_listings(
        self,
        department: str | None = None,
        municipio: str | None = None,
        max_pages: int = 25,
        start_page: int = 1,
    ) -> AsyncGenerator[ScrapedProperty, None]:
        """
        Scrape property listing pages from realtor.com/international/sv/.
        Yields ScrapedProperty objects as they are found.
        
        Args:
            start_page: Page number to start from (for resuming interrupted scrapes).
        """
        await self._launch_browser()

        try:
            page = await self._context.new_page()
            total_scraped = 0
            empty_pages = 0

            for page_num in range(start_page, max_pages + 1):
                if page_num == 1:
                    url = BASE_URL
                else:
                    url = f"{BASE_URL}p{page_num}/"

                logger.info(f"[Page {page_num}/{max_pages}] {url}")

                try:
                    await self.rate_limiter.acquire()
                    resp = await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                    if resp and resp.status >= 400:
                        logger.warning(f"  HTTP {resp.status} — stopping pagination")
                        break

                    cards = await self._extract_listing_cards(page)
                    logger.info(f"  Found {len(cards)} listing cards")

                    if not cards:
                        empty_pages += 1
                        if empty_pages >= 2:
                            logger.info("  2 consecutive empty pages — stopping")
                            break
                        continue
                    else:
                        empty_pages = 0

                    for card in cards:
                        prop = self._parse_card(card)
                        if not prop:
                            continue

                        # Skip if already seen
                        if prop.source_url in self._seen_urls:
                            continue
                        self._seen_urls.add(prop.source_url)

                        # Optionally enrich from detail page
                        if self.fetch_details:
                            detail_page = await self._context.new_page()
                            try:
                                prop = await self._fetch_detail(prop, detail_page)
                            finally:
                                await detail_page.close()

                        total_scraped += 1
                        logger.info(
                            f"  [{total_scraped}] {prop.title[:50]} — "
                            f"${prop.price_usd:,.0f} — {prop.department}"
                            if prop.price_usd
                            else f"  [{total_scraped}] {prop.title[:50]} — No price"
                        )

                        # Filter by department if requested
                        if department and prop.department.lower() != department.lower():
                            continue

                        yield prop

                except Exception as e:
                    logger.error(f"  Error on page {page_num}: {e}")
                    continue

            logger.info(f"Scraping complete. Total: {total_scraped} properties")

        finally:
            await self._close_browser()

    async def scrape_all(
        self,
        max_pages: int = 25,
        fetch_details: bool = True,
        output_dir: str | None = None,
    ) -> ScrapeResult:
        """
        Convenience method: scrape all pages and return a ScrapeResult.
        """
        self.fetch_details = fetch_details
        return await self.run(max_pages=max_pages, output_dir=output_dir)


# ── Quick Test ───────────────────────────────────────────

async def _test():
    """Quick test: scrape 2 pages without detail pages."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    scraper = RealtorInternationalScraper(
        headless=True,
        fetch_details=False,  # Fast test without details
    )

    properties = []
    async with scraper:
        async for prop in scraper.scrape_listings(max_pages=2):
            properties.append(prop)
            print(
                f"  {prop.title[:60]:60s} | "
                f"${prop.price_usd:>12,.0f} | " if prop.price_usd else f"  {'No price':>12s} | ",
                f"{prop.property_type:12s} | "
                f"{prop.department:15s} | "
                f"beds={prop.bedrooms} baths={prop.bathrooms} area={prop.area_m2}"
            )

    print(f"\n{'=' * 60}")
    print(f"Total properties: {len(properties)}")
    print(f"With price: {sum(1 for p in properties if p.price_usd)}")
    print(f"With images: {sum(1 for p in properties if p.images)}")
    print(f"With department: {sum(1 for p in properties if p.department)}")
    print(f"Property types: {set(p.property_type for p in properties if p.property_type)}")

    # Department breakdown
    depts = {}
    for p in properties:
        d = p.department or "Unknown"
        depts[d] = depts.get(d, 0) + 1
    print(f"\nBy department:")
    for d, c in sorted(depts.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")


if __name__ == "__main__":
    asyncio.run(_test())
