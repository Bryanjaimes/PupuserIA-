#!/usr/bin/env python3
"""
AI Enrichment Pipeline — PupuserIA
Runs listings through Gemini 1.5 Flash to generate:
  - impact_score (1-10)
  - is_single_story (boolean)
  - needs_remodel (boolean)
  - ideal_for (tags: retirees, families, airbnb, community_events, surfers, investors)
  - english_summary (1 paragraph)
  - family_friendly_score (1-10)
  - investment_potential (1-10)

Usage:
    export GOOGLE_API_KEY=your-key
    python enrich_ai.py [--limit 50] [--batch 10] [--model gemini-1.5-flash]

Reads:  data/scraper_output/all_listings_scored.json
Writes: data/scraper_output/all_listings_enriched.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ── Config ──────────────────────────────────────────

INPUT = Path("data/scraper_output/all_listings_scored.json")
OUTPUT = Path("data/scraper_output/all_listings_enriched.json")
CHECKPOINT = Path("data/scraper_output/_enrich_checkpoint.json")

ENRICHMENT_PROMPT = """You are a real estate analyst specializing in El Salvador properties. Analyze this listing and return ONLY a JSON object (no markdown, no explanation).

LISTING:
Title: {title}
Department: {department}, Municipality: {municipio}
Type: {property_type}
Price: ${price_usd}
Bedrooms: {bedrooms}, Bathrooms: {bathrooms}
Area: {area_m2} m², Lot: {lot_size_m2} m²
Description: {description}
Features: {features}

Return this exact JSON structure:
{{
  "impact_score": <1-10, based on community value, open space, potential for social impact>,
  "is_single_story": <true/false, infer from description/type>,
  "needs_remodel": <true/false, infer from price vs area, description keywords>,
  "ideal_for": [<list of tags from: "families", "retirees", "surfers", "airbnb", "investors", "community_events", "digital_nomads", "students">],
  "english_summary": "<1 paragraph, max 100 words, compelling description in English>",
  "family_friendly_score": <1-10, consider bedrooms, garden, single-story, safe area>,
  "investment_potential": <1-10, consider price/m2, location, Airbnb viability, appreciation>,
  "surf_proximity": <"near" if La Libertad coast / El Tunco / Surf City area, else "far">,
  "walkability_estimate": <"high"/"medium"/"low" based on urban vs rural>
}}"""


# ── Gemini Client ────────────────────────────────────

class GeminiEnricher:
    """Google Gemini 1.5 Flash enrichment."""

    def __init__(self, model: str = "gemini-1.5-flash"):
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("❌ Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
            print("   Get a free key at: https://aistudio.google.com/app/apikey")
            sys.exit(1)

        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        try:
            import httpx
            self._client = httpx.Client(timeout=30)
            self._use_httpx = True
        except ImportError:
            import urllib.request
            self._use_httpx = False

        print(f"  Using model: {model}")
        print(f"  API key: {'✅' if self.api_key else '❌'} ({self.api_key[:8]}...)")

    def enrich(self, listing: dict) -> dict | None:
        """Send a listing to Gemini and parse the JSON response."""
        prompt = ENRICHMENT_PROMPT.format(
            title=listing.get("title", ""),
            department=listing.get("department", ""),
            municipio=listing.get("municipio", ""),
            property_type=listing.get("property_type", ""),
            price_usd=listing.get("price_usd") or "N/A",
            bedrooms=listing.get("bedrooms") or "N/A",
            bathrooms=listing.get("bathrooms") or "N/A",
            area_m2=listing.get("area_m2") or "N/A",
            lot_size_m2=listing.get("lot_size_m2") or "N/A",
            description=(listing.get("description") or "")[:500],
            features=", ".join((listing.get("features") or [])[:10]),
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "topP": 0.8,
                "maxOutputTokens": 500,
                "responseMimeType": "application/json",
            },
        }

        url = f"{self.base_url}?key={self.api_key}"

        try:
            if self._use_httpx:
                resp = self._client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
            else:
                import urllib.request
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())

            # Parse Gemini response
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            # Clean markdown fences if present
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()

            result = json.loads(text)
            return result

        except json.JSONDecodeError as e:
            return None
        except KeyError:
            return None
        except Exception as e:
            print(f"    ⚠ API error: {str(e)[:80]}")
            return None

    def close(self):
        if self._use_httpx and hasattr(self, "_client"):
            self._client.close()


# ── Fallback Rule-Based Enricher ─────────────────────

class RuleBasedEnricher:
    """Deterministic fallback when no API key is available."""

    SURF_MUNIS = {
        "la libertad", "tamanique", "chiltiupan", "el tunco",
        "surf city", "playa el tunco", "el zonte", "jiquilisco",
    }
    URBAN_DEPTS = {"san salvador", "santa tecla", "antiguo cuscatlan", "san miguel"}

    def enrich(self, listing: dict) -> dict:
        desc = (listing.get("description") or "").lower()
        dept = (listing.get("department") or "").lower()
        muni = (listing.get("municipio") or "").lower()
        ptype = (listing.get("property_type") or "").lower()
        beds = listing.get("bedrooms") or 0
        baths = listing.get("bathrooms") or 0
        area = listing.get("area_m2") or 0
        lot = listing.get("lot_size_m2") or 0
        price = listing.get("price_usd") or 0

        # Impact score
        impact = 5
        if lot > 500:
            impact += 2
        if any(w in desc for w in ["patio", "jardin", "garden", "open space", "terreno"]):
            impact += 1
        if beds >= 3:
            impact += 1
        impact = min(impact, 10)

        # Single story
        is_single = any(w in desc for w in [
            "una planta", "single story", "1 nivel", "un nivel",
            "one story", "planta baja",
        ]) or ptype == "land"

        # Needs remodel
        needs_remodel = any(w in desc for w in [
            "remodel", "remodelar", "fixer", "oportunidad",
            "reparar", "necesita arreglos", "to renovate",
        ])
        if price > 0 and area > 0 and (price / area) < 300:
            needs_remodel = True

        # Ideal for
        tags = []
        if beds >= 3 and baths >= 2:
            tags.append("families")
        if is_single and beds >= 2:
            tags.append("retirees")
        if muni in self.SURF_MUNIS or dept == "la libertad":
            tags.append("surfers")
        if beds >= 2 and any(w in desc for w in ["furnished", "amueblado", "view", "vista"]):
            tags.append("airbnb")
        if price > 0 and area > 0 and (price / area) < 800:
            tags.append("investors")
        if lot > 1000:
            tags.append("community_events")
        if not tags:
            tags.append("investors")

        # Family friendly
        family_score = 3
        if beds >= 3: family_score += 2
        if baths >= 2: family_score += 1
        if is_single: family_score += 1
        if any(w in desc for w in ["jardin", "garden", "patio", "safe", "seguro"]): family_score += 2
        family_score = min(family_score, 10)

        # Investment potential
        inv_score = 5
        if muni in self.SURF_MUNIS: inv_score += 2
        if dept in ("san salvador", "la libertad"): inv_score += 1
        if needs_remodel: inv_score += 1
        if price and price < 150000: inv_score += 1
        inv_score = min(inv_score, 10)

        # Surf proximity
        surf = "near" if (muni in self.SURF_MUNIS or dept == "la libertad") else "far"

        # Walkability
        walk = "high" if dept in self.URBAN_DEPTS else ("medium" if beds >= 2 else "low")

        title = listing.get("title") or ""
        summary = f"{ptype.title()} in {listing.get('municipio', '')}, {listing.get('department', '')}."
        if price:
            summary += f" Listed at ${price:,.0f}."
        if beds:
            summary += f" {beds} bed{'s' if beds > 1 else ''}"
        if baths:
            summary += f", {baths} bath{'s' if baths > 1 else ''}"
        if area:
            summary += f", {area:,.0f} m²"
        summary += "."

        return {
            "impact_score": impact,
            "is_single_story": is_single,
            "needs_remodel": needs_remodel,
            "ideal_for": tags,
            "english_summary": summary,
            "family_friendly_score": family_score,
            "investment_potential": inv_score,
            "surf_proximity": surf,
            "walkability_estimate": walk,
        }

    def close(self):
        pass


# ── Main ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Enrichment Pipeline")
    parser.add_argument("--limit", type=int, default=0, help="Process N listings (0=all)")
    parser.add_argument("--batch", type=int, default=10, help="Save checkpoint every N")
    parser.add_argument("--model", type=str, default="gemini-1.5-flash", help="Gemini model")
    parser.add_argument("--no-api", action="store_true", help="Use rule-based enrichment (no API key needed)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--rpm", type=int, default=15, help="Requests per minute (rate limit)")
    args = parser.parse_args()

    print("🧠 PupuserIA AI Enrichment Pipeline")
    print(f"   Input:  {INPUT}")
    print(f"   Output: {OUTPUT}")
    print()

    # Load listings
    with open(INPUT, "r", encoding="utf-8") as f:
        listings = json.load(f)
    if args.limit:
        listings = listings[:args.limit]
    print(f"  Loaded {len(listings)} listings")

    # Resume from checkpoint?
    enriched_map: dict[str, dict] = {}
    if args.resume and CHECKPOINT.exists():
        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        enriched_map = {r["id"]: r.get("ai_enrichment", {}) for r in checkpoint_data if r.get("ai_enrichment")}
        print(f"  Resuming: {len(enriched_map)} already enriched")

    # Choose enricher
    if args.no_api:
        enricher = RuleBasedEnricher()
        print("  Mode: Rule-based (no API)")
    else:
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if api_key:
            enricher = GeminiEnricher(model=args.model)
            print("  Mode: Gemini API")
        else:
            print("  ℹ No API key found — falling back to rule-based enrichment")
            print("    Set GOOGLE_API_KEY for AI-powered enrichment")
            enricher = RuleBasedEnricher()

    # Process
    delay = 60.0 / args.rpm if not isinstance(enricher, RuleBasedEnricher) else 0
    results = []
    success_count = 0
    fail_count = 0
    start = time.time()

    for i, listing in enumerate(listings):
        lid = listing.get("id", f"PIA-{i:06d}")

        # Skip if already enriched (resume mode)
        if lid in enriched_map:
            listing = listing.copy()
            listing["ai_enrichment"] = enriched_map[lid]
            results.append(listing)
            success_count += 1
            continue

        # Enrich
        enrichment = enricher.enrich(listing)
        listing = listing.copy()

        if enrichment:
            listing["ai_enrichment"] = enrichment
            success_count += 1
        else:
            # Fallback to rule-based
            fallback = RuleBasedEnricher()
            listing["ai_enrichment"] = fallback.enrich(listing)
            listing["ai_enrichment"]["_fallback"] = True
            fail_count += 1

        results.append(listing)

        # Progress
        if (i + 1) % args.batch == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"  [{i+1}/{len(listings)}] ✅ {success_count} ⚠ {fail_count} ({rate:.1f}/s)")

            # Save checkpoint
            with open(CHECKPOINT, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False)

        # Rate limit for API calls
        if delay > 0:
            time.sleep(delay)

    enricher.close()

    elapsed = time.time() - start
    print(f"\n✅ Enrichment complete in {elapsed:.1f}s")
    print(f"   Success: {success_count}")
    print(f"   Fallback: {fail_count}")

    # Save output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False)
    print(f"   Output: {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.1f} MB)")

    # Stats
    tags = {}
    for r in results:
        ai = r.get("ai_enrichment", {})
        for tag in ai.get("ideal_for", []):
            tags[tag] = tags.get(tag, 0) + 1

    print(f"\n   Tags distribution:")
    for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
        print(f"     {tag}: {count}")

    # Cleanup checkpoint
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()


if __name__ == "__main__":
    main()
