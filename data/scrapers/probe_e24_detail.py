#!/usr/bin/env python3
"""Probe an Encuentra24 detail page to discover available data fields."""

import httpx
import json
import re
import sys

URL = (
    "https://www.encuentra24.com/el-salvador-en/"
    "real-estate-for-sale-houses-homes/"
    "metapan-oportunidad-de-inversion-casa-para-alquiler-de-locales-y-para-habitar/31801322"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}


def main():
    print(f"Fetching: {URL[:80]}...")
    resp = httpx.get(URL, headers=HEADERS, follow_redirects=True, timeout=30)
    print(f"Status: {resp.status_code}  Length: {len(resp.text)}")
    html = resp.text

    if resp.status_code != 200:
        print("FAILED — may be blocked")
        # Save for inspection
        with open("_probe_response.html", "w", encoding="utf-8") as f:
            f.write(html)
        return

    # ── Pattern scan ──
    patterns = {
        "description": r"description|descripcion",
        "latitude": r'"latitude"|"lat"[:\s]|latLng|lat[:\s]*[-\d]',
        "longitude": r'"longitude"|"lng"|"lon"|lng[:\s]*[-\d]',
        "gallery/carousel": r"gallery|carousel|slider",
        "JSON-LD": r"application/ld\+json",
        "og:image": r"og:image",
        "lot/terreno": r"lot|terreno|lote",
        "date": r"datePublished|datePosted|createdAt|publishDate",
        "features/attrs": r"feature|attribute|amenity",
        "photos.encuentra24": r"photos\.encuentra24\.com",
    }
    print("\n── Pattern scan ──")
    for name, pat in patterns.items():
        matches = re.findall(pat, html, re.I)
        print(f"  {name:25s}: {len(matches)} matches")

    # ── JSON-LD ──
    print("\n── JSON-LD blocks ──")
    for m in re.finditer(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    ):
        try:
            d = json.loads(m.group(1))
            t = d.get("@type", "?")
            print(f"\n  @type: {t}")
            for k, v in d.items():
                print(f"    {k}: {str(v)[:100]}")
        except Exception as e:
            print(f"  JSON-LD parse error: {e}")

    # ── Images ──
    print("\n── Images (photos.encuentra24.com) ──")
    imgs = list(set(re.findall(r'(https://photos\.encuentra24\.com/[^"\'\\]+)', html)))
    print(f"  Found {len(imgs)} unique image URLs")
    for img in imgs[:5]:
        print(f"    {img[:100]}")

    # ── Description-like blocks ──
    print("\n── Description candidates ──")
    for sel_pat in [
        r'class="[^"]*description[^"]*"[^>]*>(.*?)</(?:div|p|section)',
        r'class="[^"]*detail-desc[^"]*"[^>]*>(.*?)</(?:div|p)',
        r'id="description"[^>]*>(.*?)</(?:div|p|section)',
    ]:
        for m in re.finditer(sel_pat, html, re.S | re.I):
            text = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
            if len(text) > 20:
                print(f"  [{sel_pat[:40]}]")
                print(f"    {text[:200]}")

    # ── Coordinates in any JS/data ──
    print("\n── Coordinate candidates ──")
    for m in re.finditer(
        r'"?(?:lat(?:itude)?)"?\s*[:=]\s*([-]?\d+\.\d{3,})', html
    ):
        print(f"  lat: {m.group(1)}")
    for m in re.finditer(
        r'"?(?:lng|lon(?:gitude)?)"?\s*[:=]\s*([-]?\d+\.\d{3,})', html
    ):
        print(f"  lng: {m.group(1)}")

    # ── Map/marker related JS ──
    print("\n── Map/marker patterns ──")
    map_patterns = re.findall(
        r"(?:google\.maps|L\.map|mapbox|leaflet|initMap|marker|LatLng)", html, re.I
    )
    print(f"  Found: {map_patterns[:10]}")

    # ── Save full HTML for manual inspection ──
    with open("_probe_detail.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  Full HTML saved to _probe_detail.html ({len(html):,} chars)")


if __name__ == "__main__":
    main()
