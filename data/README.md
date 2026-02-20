# Data Pipeline — Scrapers & ETL

This directory contains:

- **scrapers/** — Web scrapers for El Salvador property listings
- **pipelines/** — ETL pipelines for data ingestion & transformation
- **seeds/** — Database seed data for development

---

## Data Scraping

### Sources

| Source | Type | Est. Listings | Status |
|---|---|---|---|
| Realtor.com International | Aggregator | ~500 | ✅ Built & running |
| Encuentra24 | Portal | ~500–1,000 | ✅ Built (blocked by Cloudflare) |
| Encuentra24 (via Google CSE) | Discovery | ~1,000 | ✅ Built (needs API key) |
| Lamudi SV | Portal | ~500–800 | ✅ Built |
| Properstar | Aggregator | ~300–600 | ✅ Built |
| Point2 Homes | Aggregator | ~200–400 | ✅ Built |
| LaVitrina SV | Classifieds | ~200–500 | ✅ Built |
| CompraVenta SV | Classifieds | ~100–300 | ✅ Built |

### Running Scrapers

```bash
cd data/scrapers

# Single source
python run.py realtor --max-pages 25
python run.py lamudi --max-pages 30
python run.py properstar --max-pages 20
python run.py point2 --max-pages 15
python run.py lavitrina --max-pages 20
python run.py compraventa --max-pages 20

# All sources at once
python run.py all --no-ingest

# Merge & deduplicate all outputs
python merge_datasets.py
```

Output goes to `scrapers/data/scraper_output/` as JSONL files (one JSON object per line).

### Data Schema

Every scraped listing is normalized to the `ScrapedProperty` schema (see `scrapers/base.py`):

| Field | Type | Description |
|---|---|---|
| `title` | string | Listing title |
| `source` | string | Source identifier (e.g., `lamudi`) |
| `source_url` | string | Original listing URL |
| `department` | string | Department name (14 departments) |
| `municipio` | string | Municipality name (262 municipios) |
| `price_usd` | float | Price in USD |
| `property_type` | string | `house`, `apartment`, `land`, `commercial` |
| `bedrooms` | int | Number of bedrooms |
| `bathrooms` | int | Number of bathrooms |
| `area_m2` | float | Built area in m² |
| `lot_size_m2` | float | Lot size in m² |
| `latitude` / `longitude` | float | GPS coordinates |
| `description` | string | Listing description |
| `images` | string[] | Image URLs |
| `listing_date` | datetime | When the listing was posted |
| `scraped_at` | datetime | When we scraped it |

---

## Legal Compliance — Web Scraping

### Summary

**Scraping publicly available property listing data (prices, addresses, specs) is legal in the United States.** This project only scrapes data from public-facing web pages that do not require authentication.

### Legal Basis

1. **hiQ Labs, Inc. v. LinkedIn Corp. (2022, 9th Circuit)** — The court held that scraping publicly available data does not violate the Computer Fraud and Abuse Act (CFAA). Data that is freely accessible to any visitor without a login is not "protected" under the CFAA.

2. **Meta Platforms, Inc. v. Bright Data Ltd. (2024, N.D. Cal.)** — The court ruled that scraping publicly viewable content (no login required) does not constitute unauthorized access under the CFAA.

3. **Feist Publications, Inc. v. Rural Telephone Service Co. (1991, U.S. Supreme Court)** — Factual data (prices, addresses, property dimensions) **cannot be copyrighted**. Only creative expression (original descriptions, photographs) is protected.

### What We Do

- ✅ **Scrape only public pages** — no login bypass, no captcha circumvention
- ✅ **Respect `robots.txt`** — all scrapers check and obey robots.txt directives
- ✅ **Rate-limit all requests** — 0.5–1 request/second with token-bucket limiter
- ✅ **Identify ourselves** — custom User-Agent header: `GatewayElSalvador-PropertyResearch/1.0`
- ✅ **Collect factual data** — prices, locations, bedrooms, area, property types
- ✅ **Store original descriptions for internal analysis only** — not displayed verbatim on our site

### What We Do NOT Do

- 🚫 **No authentication bypass** — we never log into any site
- 🚫 **No captcha/Cloudflare circumvention** — if a site blocks us, we stop (see: Encuentra24)
- 🚫 **No copyrighted photo hosting** — we do not download or serve other sites' images
- 🚫 **No verbatim description copying** — AI rewrites descriptions for our listings
- 🚫 **No DDoS-level request volumes** — maximum ~1 req/sec with exponential backoff on 429s

### For Display on Our Platform

| Data Type | Can Display? | Notes |
|---|---|---|
| Factual data (price, beds, area, address) | ✅ Yes | Not copyrightable (Feist v. Rural) |
| GPS coordinates | ✅ Yes | Factual data |
| Original listing descriptions | ⚠️ No — rewrite | Creative works; use AI to generate our own |
| Original listing photos | ⚠️ No — link only | Copyrighted by photographer; link to source or use our own |
| AI-generated valuations & descriptions | ✅ Yes | Our own original content |

### Terms of Service

Most real estate sites prohibit scraping in their ToS. However:

- ToS violations are **contract disputes**, not criminal offenses
- Per *hiQ v. LinkedIn*, ToS cannot override public access rights for CFAA purposes
- We mitigate risk by: rate-limiting, identifying our scraper, and only collecting factual data
- If any source sends a cease-and-desist, we will immediately stop scraping that source and remove their data

### References

- *hiQ Labs v. LinkedIn*, 938 F.3d 985 (9th Cir. 2022)
- *Meta Platforms v. Bright Data*, No. 23-cv-00985 (N.D. Cal. 2024)
- *Feist Publications v. Rural Telephone*, 499 U.S. 340 (1991)
- *Van Buren v. United States*, 593 U.S. ___ (2021) — narrowed CFAA scope
