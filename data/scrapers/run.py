#!/usr/bin/env python3
"""
Property Scraper CLI
=====================
Command-line interface to run property scrapers and ingest results
into the PostgreSQL database.

Usage:
    # Scrape realtor.com international (all pages)
    python run.py realtor --max-pages 25
    
    # Quick test (2 pages, no detail pages)
    python run.py realtor --max-pages 2 --no-details
    
    # Scrape only a specific department
    python run.py realtor --department "San Salvador" --max-pages 25
    
    # Scrape Encuentra24 (all categories, all departments)
    python run.py encuentra24 --all
    
    # Scrape only houses in San Salvador
    python run.py encuentra24 --category house --department "San Salvador"
    
    # Scrape with limited pages (for testing)
    python run.py encuentra24 --max-pages 3 --no-details
    
    # Just ingest from a previous JSONL output
    python run.py ingest --file data/scraper_output/encuentra24_all_20260209.jsonl
    
    # Show current DB stats
    python run.py stats
    
    # Update coverage scores
    python run.py coverage
    
    # Mark stale listings
    python run.py stale --source encuentra24 --days 30
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Ensure imports work from data/scrapers/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base import ScrapedProperty, ScrapeResult
from ingestion import PropertyIngester

# Default database URL (matches apps/api/app/config.py)
DEFAULT_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/gateway_es"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scraper-cli")


async def run_encuentra24(args) -> None:
    """Run the Encuentra24 scraper."""
    from encuentra24 import Encuentra24Scraper

    scraper = Encuentra24Scraper()
    scraper.headless = not args.visible
    if args.rate_limit:
        scraper.requests_per_second = args.rate_limit

    categories = None
    if args.category:
        categories = [args.category]

    logger.info("=" * 60)
    logger.info("Encuentra24 Property Scraper")
    logger.info("=" * 60)
    logger.info(f"  Department:    {args.department or 'ALL'}")
    logger.info(f"  Categories:    {categories or 'ALL'}")
    logger.info(f"  Max pages:     {args.max_pages}")
    logger.info(f"  Fetch details: {not args.no_details}")
    logger.info(f"  Headless:      {not args.visible}")
    logger.info(f"  Output dir:    {args.output}")
    logger.info("=" * 60)

    if args.all:
        # Full country scrape
        result = ScrapeResult(
            source="encuentra24",
            department=None,
            municipio=None,
            started_at=datetime.utcnow(),
        )
        async with scraper:
            async for prop in scraper.scrape_all_departments(
                max_pages_per_dept=args.max_pages,
                categories=categories,
                fetch_details=not args.no_details,
            ):
                result.properties.append(prop)
                result.total_found += 1
                result.total_new += 1
                if result.total_found % 10 == 0:
                    logger.info(f"  Collected {result.total_found} properties so far...")
        result.finished_at = datetime.utcnow()
    else:
        # Single department or default
        result = await scraper.run(
            department=args.department,
            municipio=args.municipio,
            max_pages=args.max_pages,
            output_dir=args.output,
        )

    logger.info(f"\nScraping complete!")
    logger.info(f"  Total found:  {result.total_found}")
    logger.info(f"  Duration:     {result.duration_seconds:.1f}s")
    logger.info(f"  Errors:       {result.total_errors}")

    # Save results to JSONL
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dept_label = args.department.replace(" ", "_") if args.department else "all"
        filepath = output_dir / f"encuentra24_{dept_label}_{timestamp}.jsonl"
        
        with open(filepath, "w", encoding="utf-8") as f:
            for prop in result.properties:
                f.write(json.dumps(prop.to_dict(), ensure_ascii=False) + "\n")
        logger.info(f"  Saved to:     {filepath}")

    # Ingest into database
    if not args.no_ingest and result.properties:
        logger.info(f"\nIngesting {len(result.properties)} properties into database...")
        ingester = PropertyIngester(args.db_url)
        async with ingester:
            stats = await ingester.ingest(result)
            logger.info(f"  Inserted:  {stats['inserted']}")
            logger.info(f"  Updated:   {stats['updated']}")
            logger.info(f"  Errors:    {stats['errors']}")

            # Update coverage scores
            logger.info("\nUpdating coverage scores...")
            await ingester.update_coverage_scores()

    logger.info("\nDone!")


async def run_cse(args) -> None:
    """Run the Encuentra24 CSE two-layer pipeline."""
    from encuentra24_cse import Encuentra24CSEScraper

    scraper = Encuentra24CSEScraper(
        api_key=args.api_key,
        cse_id=args.cse_id,
        max_queries=args.max_queries,
        max_enrichments=args.max_enrich,
        enrich=args.max_enrich > 0,
    )

    logger.info("=" * 60)
    logger.info("Encuentra24 — CSE Two-Layer Pipeline")
    logger.info("=" * 60)
    logger.info(f"  Department:      {args.department or 'ALL'}")
    logger.info(f"  CSE queries:     {args.max_queries}")
    logger.info(f"  Enrich up to:    {args.max_enrich}")
    logger.info(f"  Output dir:      {args.output}")
    logger.info("=" * 60)

    result = ScrapeResult(
        source="encuentra24",
        department=args.department,
        municipio=None,
        started_at=datetime.utcnow(),
    )

    async with scraper:
        async for prop in scraper.scrape_listings(
            department=args.department,
        ):
            result.properties.append(prop)
            result.total_found += 1
            result.total_new += 1
            if result.total_found % 25 == 0:
                logger.info(f"  Collected {result.total_found} properties so far...")

    result.finished_at = datetime.utcnow()

    logger.info(f"\nScraping complete!")
    logger.info(f"  Total found:  {result.total_found}")
    logger.info(f"  Duration:     {result.duration_seconds:.1f}s")

    # Save results to JSONL
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dept_label = args.department.replace(" ", "_") if args.department else "all"
        filepath = output_dir / f"encuentra24_cse_{dept_label}_{timestamp}.jsonl"

        with open(filepath, "w", encoding="utf-8") as f:
            for prop in result.properties:
                f.write(json.dumps(prop.to_dict(), ensure_ascii=False) + "\n")
        logger.info(f"  Saved to:     {filepath}")

    # Ingest into database
    if not args.no_ingest and result.properties:
        logger.info(f"\nIngesting {len(result.properties)} properties into database...")
        ingester = PropertyIngester(args.db_url)
        async with ingester:
            stats = await ingester.ingest(result)
            logger.info(f"  Inserted:  {stats['inserted']}")
            logger.info(f"  Updated:   {stats['updated']}")
            logger.info(f"  Errors:    {stats['errors']}")

            logger.info("\nUpdating coverage scores...")
            await ingester.update_coverage_scores()

    logger.info("\nDone!")


async def run_realtor(args) -> None:
    """Run the Realtor.com International scraper."""
    from realtor_intl import RealtorInternationalScraper

    scraper = RealtorInternationalScraper(
        headless=not args.visible,
        fetch_details=not args.no_details,
    )
    if args.rate_limit:
        scraper.requests_per_second = args.rate_limit

    logger.info("=" * 60)
    logger.info("Realtor.com International — El Salvador Scraper")
    logger.info("=" * 60)
    logger.info(f"  Department:    {args.department or 'ALL'}")
    logger.info(f"  Start page:    {args.start_page}")
    logger.info(f"  Max pages:     {args.max_pages}")
    logger.info(f"  Fetch details: {not args.no_details}")
    logger.info(f"  Headless:      {not args.visible}")
    logger.info(f"  Output dir:    {args.output}")
    logger.info("=" * 60)

    result = ScrapeResult(
        source="realtor_intl",
        department=args.department,
        municipio=None,
        started_at=datetime.utcnow(),
    )

    async with scraper:
        async for prop in scraper.scrape_listings(
            department=args.department,
            max_pages=args.max_pages,
            start_page=args.start_page,
        ):
            result.properties.append(prop)
            result.total_found += 1
            result.total_new += 1
            if result.total_found % 25 == 0:
                logger.info(f"  Collected {result.total_found} properties so far...")

    result.finished_at = datetime.utcnow()

    logger.info(f"\nScraping complete!")
    logger.info(f"  Total found:  {result.total_found}")
    logger.info(f"  Duration:     {result.duration_seconds:.1f}s")

    # Save results to JSONL
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dept_label = args.department.replace(" ", "_") if args.department else "all"
        filepath = output_dir / f"realtor_{dept_label}_{timestamp}.jsonl"

        with open(filepath, "w", encoding="utf-8") as f:
            for prop in result.properties:
                f.write(json.dumps(prop.to_dict(), ensure_ascii=False) + "\n")
        logger.info(f"  Saved to:     {filepath}")

    # Ingest into database
    if not args.no_ingest and result.properties:
        logger.info(f"\nIngesting {len(result.properties)} properties into database...")
        ingester = PropertyIngester(args.db_url)
        async with ingester:
            stats = await ingester.ingest(result)
            logger.info(f"  Inserted:  {stats['inserted']}")
            logger.info(f"  Updated:   {stats['updated']}")
            logger.info(f"  Errors:    {stats['errors']}")

            logger.info("\nUpdating coverage scores...")
            await ingester.update_coverage_scores()

    logger.info("\nDone!")


async def run_ingest(args) -> None:
    """Ingest properties from a JSONL file."""
    filepath = Path(args.file)
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        sys.exit(1)

    properties = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            prop = ScrapedProperty(
                title=data.get("title", ""),
                source=data.get("source", "unknown"),
                source_url=data.get("source_url", ""),
                department=data.get("department", ""),
                municipio=data.get("municipio", ""),
                canton=data.get("canton", ""),
                address=data.get("address", ""),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                price_usd=data.get("price_usd"),
                price_raw=data.get("price_raw", ""),
                property_type=data.get("property_type", ""),
                bedrooms=data.get("bedrooms"),
                bathrooms=data.get("bathrooms"),
                area_m2=data.get("area_m2"),
                lot_size_m2=data.get("lot_size_m2"),
                description=data.get("description", ""),
                description_es=data.get("description_es", ""),
                images=data.get("images", []),
                features=data.get("features", []),
            )
            properties.append(prop)

    logger.info(f"Loaded {len(properties)} properties from {filepath}")

    ingester = PropertyIngester(args.db_url)
    async with ingester:
        stats = await ingester.ingest_properties(properties)
        logger.info(f"  Inserted:  {stats['inserted']}")
        logger.info(f"  Updated:   {stats['updated']}")
        logger.info(f"  Errors:    {stats['errors']}")

        logger.info("\nUpdating coverage scores...")
        await ingester.update_coverage_scores()

    logger.info("Done!")


async def run_stats(args) -> None:
    """Show current database stats."""
    ingester = PropertyIngester(args.db_url)
    async with ingester:
        stats = await ingester.get_stats()

    logger.info("=" * 50)
    logger.info("Property Database Statistics")
    logger.info("=" * 50)
    logger.info(f"  Total properties:    {stats['total']}")
    logger.info(f"  Active:              {stats['active']}")
    logger.info(f"  Departments:         {stats['departments']}")
    logger.info(f"  Sources:             {stats['sources']}")
    logger.info(f"  With price:          {stats['with_price']}")
    logger.info(f"  With images:         {stats['with_images']}")
    logger.info(f"  Average price:       ${stats['avg_price']:,.0f}")
    logger.info(f"  Oldest record:       {stats['oldest_record']}")
    logger.info(f"  Most recent update:  {stats['newest_update']}")
    logger.info("=" * 50)


async def run_coverage(args) -> None:
    """Update coverage gap scores."""
    ingester = PropertyIngester(args.db_url)
    async with ingester:
        await ingester.update_coverage_scores()
    logger.info("Coverage scores updated!")


async def run_stale(args) -> None:
    """Mark stale listings as inactive."""
    ingester = PropertyIngester(args.db_url)
    async with ingester:
        count = await ingester.mark_stale_listings(args.source, args.days)
    logger.info(f"Marked {count} stale listings as inactive")


def main():
    parser = argparse.ArgumentParser(
        description="Gateway El Salvador — Property Scraper CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py encuentra24 --max-pages 3 --no-details    # Quick test
  python run.py encuentra24 --all                         # Full scrape
  python run.py encuentra24 --department "San Salvador"    # Single dept
  python run.py stats                                     # DB stats
  python run.py ingest --file output.jsonl                # Load from file
  python run.py coverage                                  # Update scores
  python run.py stale --source encuentra24 --days 30      # Cleanup
        """,
    )
    parser.add_argument(
        "--db-url",
        default=DEFAULT_DB_URL,
        help="PostgreSQL connection URL",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # ── realtor ──
    rea_parser = subparsers.add_parser("realtor", help="Scrape realtor.com/international/sv/")
    rea_parser.add_argument("--department", "-d", help="Filter by department name")
    rea_parser.add_argument("--start-page", type=int, default=1, help="Page number to start from (for resuming)")
    rea_parser.add_argument("--max-pages", type=int, default=25, help="Max listing pages to scrape")
    rea_parser.add_argument("--no-details", action="store_true", help="Skip fetching detail pages")
    rea_parser.add_argument("--no-ingest", action="store_true", help="Don't write to database")
    rea_parser.add_argument("--visible", action="store_true", help="Show browser (non-headless)")
    rea_parser.add_argument("--rate-limit", type=float, help="Requests per second")
    rea_parser.add_argument(
        "--output", "-o",
        default="data/scraper_output",
        help="Output directory for JSONL files",
    )

    # ── encuentra24 ──
    enc_parser = subparsers.add_parser("encuentra24", help="Scrape Encuentra24")
    enc_parser.add_argument("--department", "-d", help="Department to scrape")
    enc_parser.add_argument("--municipio", "-m", help="Municipio filter")
    enc_parser.add_argument(
        "--category", "-c",
        choices=["house", "apartment", "land", "commercial", "office", "warehouse"],
        help="Property category",
    )
    enc_parser.add_argument("--max-pages", type=int, default=50, help="Max pages per category")
    enc_parser.add_argument("--all", action="store_true", help="Scrape all departments")
    enc_parser.add_argument("--no-details", action="store_true", help="Skip fetching detail pages")
    enc_parser.add_argument("--no-ingest", action="store_true", help="Don't write to database")
    enc_parser.add_argument("--visible", action="store_true", help="Show browser (non-headless)")
    enc_parser.add_argument("--rate-limit", type=float, help="Requests per second")
    enc_parser.add_argument(
        "--output", "-o",
        default="data/scraper_output",
        help="Output directory for JSONL files",
    )

    # ── cse ──
    cse_parser = subparsers.add_parser("cse", help="Encuentra24 via Google CSE two-layer pipeline")
    cse_parser.add_argument("--department", "-d", help="Filter by department name")
    cse_parser.add_argument("--api-key", help="Google CSE API key (or GOOGLE_CSE_API_KEY env)")
    cse_parser.add_argument("--cse-id", help="Google CSE ID (or GOOGLE_CSE_ID env)")
    cse_parser.add_argument("--max-queries", type=int, default=20, help="Max CSE search queries (default: 20)")
    cse_parser.add_argument("--max-enrich", type=int, default=0, help="Max listings to enrich (default: 0 = skip)")
    cse_parser.add_argument("--no-ingest", action="store_true", help="Don't write to database")
    cse_parser.add_argument(
        "--output", "-o",
        default="data/scraper_output",
        help="Output directory for JSONL files",
    )

    # ── ingest ──
    ing_parser = subparsers.add_parser("ingest", help="Ingest from JSONL file")
    ing_parser.add_argument("--file", "-f", required=True, help="JSONL file path")

    # ── stats ──
    subparsers.add_parser("stats", help="Show database statistics")

    # ── coverage ──
    subparsers.add_parser("coverage", help="Update coverage gap scores")

    # ── stale ──
    stale_parser = subparsers.add_parser("stale", help="Mark stale listings inactive")
    stale_parser.add_argument("--source", required=True, help="Source name")
    stale_parser.add_argument("--days", type=int, default=30, help="Days threshold")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "realtor":
        asyncio.run(run_realtor(args))
    elif args.command == "encuentra24":
        asyncio.run(run_encuentra24(args))
    elif args.command == "cse":
        asyncio.run(run_cse(args))
    elif args.command == "ingest":
        asyncio.run(run_ingest(args))
    elif args.command == "stats":
        asyncio.run(run_stats(args))
    elif args.command == "coverage":
        asyncio.run(run_coverage(args))
    elif args.command == "stale":
        asyncio.run(run_stale(args))


if __name__ == "__main__":
    main()
