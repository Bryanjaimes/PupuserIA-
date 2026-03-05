#!/usr/bin/env python3
"""
Stale Data Checker — PupuserIA
Validates listing source URLs are still active. Marks sold/removed as inactive.

How it works:
  1. Reads all listings from JSON (or Supabase)
  2. Does HTTP HEAD requests on source_url
  3. If 404 / "Vendido" / "Inactivo" → marks is_active = false
  4. Saves a report + updated JSON

Usage:
    python check_stale.py [--limit 100] [--workers 10]
    python check_stale.py --supabase   # Check against Supabase DB

Designed to run as a weekly CRON via GitHub Actions (see .github/workflows/stale-check.yml)
"""
from __future__ import annotations

import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

INPUT = Path("data/scraper_output/all_listings_scored.json")
OUTPUT = Path("data/scraper_output/all_listings_freshness.json")
REPORT = Path("data/scraper_output/_stale_report.txt")

STALE_KEYWORDS = [
    "vendido", "sold", "inactivo", "inactive", "no disponible",
    "not available", "expired", "removed", "eliminado", "listing not found",
    "página no encontrada", "404",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PupuserIA-FreshnessBot/1.0)",
    "Accept": "text/html,application/xhtml+xml",
}


try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    import urllib.request


def check_url(url: str) -> tuple[str, int, str]:
    """
    Check if a URL is still active.
    Returns: (status, http_code, detail)
      status: 'active' | 'stale' | 'error'
    """
    if not url or not url.startswith("http"):
        return "error", 0, "no url"

    try:
        if HAS_HTTPX:
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                # Try HEAD first (faster)
                try:
                    resp = client.head(url, headers=HEADERS)
                except:
                    resp = client.get(url, headers=HEADERS)

                code = resp.status_code

                if code == 404:
                    return "stale", code, "404 not found"
                if code == 410:
                    return "stale", code, "410 gone"
                if code >= 400:
                    return "error", code, f"HTTP {code}"

                # Check body for stale keywords (GET only if HEAD succeeded)
                if resp.request.method == "HEAD":
                    resp = client.get(url, headers=HEADERS)

                body = resp.text[:5000].lower()
                for keyword in STALE_KEYWORDS:
                    if keyword in body:
                        return "stale", code, f"keyword: {keyword}"

                return "active", code, "ok"
        else:
            req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    code = resp.getcode()
            except urllib.error.HTTPError as e:
                if e.code in (404, 410):
                    return "stale", e.code, f"HTTP {e.code}"
                return "error", e.code, f"HTTP {e.code}"

            if code == 404:
                return "stale", code, "404"
            return "active", code, "ok"

    except Exception as e:
        err_str = str(e)[:60]
        if "timeout" in err_str.lower() or "timed out" in err_str.lower():
            return "error", 0, "timeout"
        return "error", 0, err_str


def main():
    parser = argparse.ArgumentParser(description="Check stale listings")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--input", type=str, default=str(INPUT))
    args = parser.parse_args()

    input_path = Path(args.input)
    print(f"🔍 PupuserIA Stale Data Checker")
    print(f"   Input:   {input_path}")
    print(f"   Workers: {args.workers}")
    print()

    with open(input_path, "r", encoding="utf-8") as f:
        listings = json.load(f)
    if args.limit:
        listings = listings[:args.limit]
    print(f"  Loaded {len(listings)} listings")

    # Extract source URLs
    url_map = {}
    for listing in listings:
        url = listing.get("source_url") or listing.get("url") or ""
        if url:
            url_map[listing.get("id", "")] = url

    print(f"  {len(url_map)} listings have source URLs")
    if not url_map:
        print("  ⚠ No source URLs found (data may have been stripped)")
        print("  Tip: Keep source_url in your scored data for freshness checks")
        return

    # Check URLs
    results = {}
    active = stale = errors = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(check_url, url): lid
            for lid, url in url_map.items()
        }

        for i, future in enumerate(as_completed(futures)):
            lid = futures[future]
            status, code, detail = future.result()
            results[lid] = {"status": status, "code": code, "detail": detail}

            if status == "active":
                active += 1
            elif status == "stale":
                stale += 1
            else:
                errors += 1

            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(url_map)}] Active: {active}, Stale: {stale}, Error: {errors}")

    elapsed = time.time() - start
    print(f"\n✅ Done in {elapsed:.1f}s")
    print(f"   Active: {active}")
    print(f"   Stale:  {stale}")
    print(f"   Error:  {errors}")

    # Update listings
    for listing in listings:
        lid = listing.get("id", "")
        if lid in results:
            r = results[lid]
            listing["is_active"] = r["status"] == "active"
            listing["freshness_check"] = {
                "status": r["status"],
                "code": r["code"],
                "detail": r["detail"],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
        else:
            listing["is_active"] = True  # assume active if no URL to check

    # Save
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False)
    print(f"   Output: {OUTPUT}")

    # Report
    report_lines = [
        f"PupuserIA Freshness Report — {datetime.now(timezone.utc).isoformat()}",
        f"Total checked: {len(url_map)}",
        f"Active: {active}, Stale: {stale}, Error: {errors}",
        "",
        "STALE LISTINGS:",
    ]
    for lid, r in results.items():
        if r["status"] == "stale":
            report_lines.append(f"  {lid}: {url_map[lid]} — {r['detail']}")

    report_lines.append("\nERRORS:")
    for lid, r in results.items():
        if r["status"] == "error":
            report_lines.append(f"  {lid}: {url_map[lid]} — {r['detail']}")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"   Report: {REPORT}")


if __name__ == "__main__":
    main()
