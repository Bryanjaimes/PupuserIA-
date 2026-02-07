"""
Property Listing Scraper — El Salvador
=======================================
Scrapes property listings from existing ES real estate sites
to build the training dataset for the AI Valuation Engine.

Target sources (ethical scraping with rate limiting):
  - Encuentra24 El Salvador
  - OLX El Salvador
  - Corotos El Salvador
  - Facebook Marketplace (manual collection)
  - Government cadastral records (CNR)

Data collected per listing:
  - Title, description (ES)
  - Price (USD)
  - Location (department, municipio, coordinates)
  - Property type, bedrooms, bathrooms, area
  - Images
  - Listing date
  - Source URL
"""

# TODO: Implement scrapers using httpx + BeautifulSoup or Playwright
# TODO: Add rate limiting and robots.txt compliance
# TODO: Store raw data in PostgreSQL
# TODO: Build feature extraction pipeline for AI model training
