#!/usr/bin/env python3
"""
PupuserIA — Embedding + Supabase Ingestion Pipeline

Generates vector embeddings for listings and pushes everything to Supabase.

Usage:
    # Step 1: Generate embeddings (saves locally)
    export GOOGLE_API_KEY=your-key
    python embed_and_ingest.py --embed-only [--limit 50]

    # Step 2: Push to Supabase
    export SUPABASE_URL=https://xxx.supabase.co
    export SUPABASE_SERVICE_KEY=eyJ...
    python embed_and_ingest.py --push-only

    # Both at once
    python embed_and_ingest.py

Reads:  data/scraper_output/all_listings_enriched.json  (or all_listings_scored.json)
Writes: data/scraper_output/all_listings_embedded.json
Pushes: → Supabase `properties` table
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

INPUT_ENRICHED = Path("data/scraper_output/all_listings_enriched.json")
INPUT_SCORED = Path("data/scraper_output/all_listings_scored.json")
OUTPUT = Path("data/scraper_output/all_listings_embedded.json")
CHECKPOINT = Path("data/scraper_output/_embed_checkpoint.json")

BATCH_SIZE = 20  # Gemini embedding API supports batches


# ── Embedding providers ──────────────────────────────

class GeminiEmbedder:
    """Google Gemini text-embedding-004 (768 dimensions)."""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("❌ Set GOOGLE_API_KEY for embeddings")
            sys.exit(1)

        self.model = "text-embedding-004"
        self.dim = 768
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent"
        self.batch_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:batchEmbedContents"

        try:
            import httpx
            self._client = httpx.Client(timeout=30)
        except ImportError:
            print("❌ pip install httpx")
            sys.exit(1)

        print(f"  Embedder: Gemini {self.model} ({self.dim}d)")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts. Returns list of vectors."""
        payload = {
            "requests": [
                {
                    "model": f"models/{self.model}",
                    "content": {"parts": [{"text": t[:2000]}]},  # Truncate
                    "taskType": "RETRIEVAL_DOCUMENT",
                }
                for t in texts
            ]
        }

        resp = self._client.post(
            f"{self.batch_url}?key={self.api_key}",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        return [e["values"] for e in data["embeddings"]]

    def close(self):
        self._client.close()


class OpenAIEmbedder:
    """OpenAI text-embedding-3-small (1536 dimensions)."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ Set OPENAI_API_KEY for embeddings")
            sys.exit(1)

        self.model = "text-embedding-3-small"
        self.dim = 1536

        try:
            import httpx
            self._client = httpx.Client(timeout=30)
        except ImportError:
            print("❌ pip install httpx")
            sys.exit(1)

        print(f"  Embedder: OpenAI {self.model} ({self.dim}d)")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": [t[:8000] for t in texts]},
        )
        resp.raise_for_status()
        data = resp.json()
        return [d["embedding"] for d in data["data"]]

    def close(self):
        self._client.close()


# ── Text preparation ─────────────────────────────────

def prepare_text(listing: dict) -> str:
    """Build a rich text for embedding from listing fields."""
    parts = []

    # Title
    title = listing.get("title") or ""
    if title:
        parts.append(title)

    # Location
    dept = listing.get("department", "")
    muni = listing.get("municipio", "")
    if dept or muni:
        parts.append(f"Location: {muni}, {dept}, El Salvador")

    # Type + specs
    ptype = listing.get("property_type", "")
    specs = []
    if ptype:
        specs.append(ptype)
    beds = listing.get("bedrooms")
    if beds:
        specs.append(f"{beds} bedrooms")
    baths = listing.get("bathrooms")
    if baths:
        specs.append(f"{baths} bathrooms")
    area = listing.get("area_m2")
    if area:
        specs.append(f"{area} m²")
    price = listing.get("price_usd")
    if price:
        specs.append(f"${price:,.0f}")
    if specs:
        parts.append(", ".join(specs))

    # Description
    desc = listing.get("description") or ""
    if desc:
        parts.append(desc[:500])

    # AI enrichment
    ai = listing.get("ai_enrichment", {})
    summary = ai.get("english_summary") or ""
    if summary:
        parts.append(summary)
    tags = ai.get("ideal_for", [])
    if tags:
        parts.append(f"Ideal for: {', '.join(tags)}")

    # Features
    features = listing.get("features", [])
    if features:
        parts.append(f"Features: {', '.join(features[:10])}")

    return ". ".join(parts)


# ── Supabase push ────────────────────────────────────

def push_to_supabase(listings: list[dict]):
    """Push listings to Supabase properties table."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ Set SUPABASE_URL and SUPABASE_SERVICE_KEY")
        sys.exit(1)

    try:
        import httpx
    except ImportError:
        print("❌ pip install httpx")
        sys.exit(1)

    client = httpx.Client(
        base_url=f"{url}/rest/v1",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        timeout=30,
    )

    print(f"  Pushing {len(listings)} listings to Supabase...")

    batch_size = 100
    pushed = 0
    errors = 0

    for i in range(0, len(listings), batch_size):
        batch = listings[i : i + batch_size]
        rows = []

        for r in batch:
            ai = r.get("ai_enrichment", {})
            row = {
                "id": r.get("id"),
                "title": r.get("title", ""),
                "title_es": r.get("title_es", ""),
                "description": r.get("description", ""),
                "description_es": r.get("description_es", ""),
                "english_summary": ai.get("english_summary"),
                "department": r.get("department", ""),
                "municipio": r.get("municipio", ""),
                "address": r.get("address", ""),
                "latitude": r.get("latitude", 0),
                "longitude": r.get("longitude", 0),
                "price_usd": r.get("price_usd"),
                "ai_valuation_usd": r.get("ai_valuation_usd"),
                "bedrooms": r.get("bedrooms"),
                "bathrooms": r.get("bathrooms"),
                "area_m2": r.get("area_m2"),
                "lot_size_m2": r.get("lot_size_m2"),
                "property_type": r.get("property_type", "unknown"),
                "thumbnail_url": r.get("thumbnail_url"),
                "images": r.get("images", []),
                "images_storage": r.get("images_storage", []),
                "is_featured": r.get("is_featured", False),
                "neighborhood_score": r.get("neighborhood_score", 0),
                "completeness_score": r.get("completeness_score", 0),
                "quality_tier": r.get("quality_tier", "bronze"),
                "missing_fields": r.get("missing_fields", []),
                "ad_ready": r.get("ad_ready", False),
                "impact_score": ai.get("impact_score"),
                "is_single_story": ai.get("is_single_story"),
                "needs_remodel": ai.get("needs_remodel"),
                "ideal_for": ai.get("ideal_for", []),
                "family_friendly_score": ai.get("family_friendly_score"),
                "investment_potential": ai.get("investment_potential"),
                "surf_proximity": ai.get("surf_proximity", "far"),
                "walkability_estimate": ai.get("walkability_estimate", "low"),
                "source": r.get("source"),
                "source_url": r.get("source_url"),
                "seller": r.get("seller"),
                "listing_date": r.get("listing_date"),
                "is_active": r.get("is_active", True),
            }

            # Add embedding if present
            emb = r.get("embedding")
            if emb:
                row["embedding"] = emb

            rows.append(row)

        try:
            resp = client.post("/properties", json=rows)
            if resp.status_code in (200, 201):
                pushed += len(rows)
            else:
                print(f"    ⚠ Batch {i//batch_size}: {resp.status_code} - {resp.text[:200]}")
                errors += len(rows)
        except Exception as e:
            print(f"    ❌ Batch {i//batch_size}: {e}")
            errors += len(rows)

        if (i // batch_size + 1) % 5 == 0:
            print(f"    [{pushed + errors}/{len(listings)}] pushed: {pushed}, errors: {errors}")

    client.close()
    print(f"  ✅ Pushed {pushed}, errors: {errors}")


# ── Main ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Embed + Ingest to Supabase")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--embed-only", action="store_true")
    parser.add_argument("--push-only", action="store_true")
    parser.add_argument("--provider", choices=["gemini", "openai"], default="gemini")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--rpm", type=int, default=60, help="Requests per minute")
    args = parser.parse_args()

    print("🧠 PupuserIA Embedding + Ingestion Pipeline")
    print()

    # Choose input (prefer enriched, fall back to scored)
    input_path = INPUT_ENRICHED if INPUT_ENRICHED.exists() else INPUT_SCORED
    print(f"  Input: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        listings = json.load(f)
    if args.limit:
        listings = listings[:args.limit]
    print(f"  Loaded {len(listings)} listings")

    # ── Embed ──
    if not args.push_only:
        # Resume from checkpoint?
        embedded_map: dict[str, list[float]] = {}
        if args.resume and CHECKPOINT.exists():
            with open(CHECKPOINT, "r", encoding="utf-8") as f:
                cp = json.load(f)
            embedded_map = {r["id"]: r["embedding"] for r in cp if r.get("embedding")}
            print(f"  Resuming: {len(embedded_map)} already embedded")

        # Initialize embedder
        if args.provider == "gemini":
            embedder = GeminiEmbedder()
        else:
            embedder = OpenAIEmbedder()

        delay = 60.0 / args.rpm
        success = 0
        start = time.time()

        # Process in batches
        for i in range(0, len(listings), BATCH_SIZE):
            batch = listings[i : i + BATCH_SIZE]

            # Skip already embedded
            to_embed = []
            to_embed_idx = []
            for j, listing in enumerate(batch):
                lid = listing.get("id", "")
                if lid in embedded_map:
                    listing["embedding"] = embedded_map[lid]
                    success += 1
                else:
                    to_embed.append(prepare_text(listing))
                    to_embed_idx.append(j)

            if to_embed:
                try:
                    vectors = embedder.embed_batch(to_embed)
                    for j, vec in zip(to_embed_idx, vectors):
                        batch[j]["embedding"] = vec
                        success += 1
                except Exception as e:
                    print(f"  ⚠ Batch {i//BATCH_SIZE}: {e}")

                time.sleep(delay)

            if (i // BATCH_SIZE + 1) % 10 == 0:
                elapsed = time.time() - start
                rate = success / elapsed if elapsed > 0 else 0
                print(f"  [{i + len(batch)}/{len(listings)}] {success} embedded ({rate:.0f}/s)")

                # Checkpoint
                with open(CHECKPOINT, "w", encoding="utf-8") as f:
                    json.dump(listings[:i + len(batch)], f, ensure_ascii=False)

        embedder.close()
        elapsed = time.time() - start

        with_emb = sum(1 for r in listings if r.get("embedding"))
        print(f"\n  ✅ Embeddings done in {elapsed:.1f}s")
        print(f"     {with_emb}/{len(listings)} listings have embeddings")

        # Save
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(listings, f, ensure_ascii=False)
        print(f"     Output: {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.1f} MB)")

    # ── Push to Supabase ──
    if not args.embed_only:
        if args.push_only and OUTPUT.exists():
            with open(OUTPUT, "r", encoding="utf-8") as f:
                listings = json.load(f)
            if args.limit:
                listings = listings[:args.limit]

        supabase_url = os.environ.get("SUPABASE_URL")
        if supabase_url:
            push_to_supabase(listings)
        else:
            print("\n  ℹ SUPABASE_URL not set — skipping push")
            print("    Set SUPABASE_URL and SUPABASE_SERVICE_KEY to push to Supabase")

    # Cleanup
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
