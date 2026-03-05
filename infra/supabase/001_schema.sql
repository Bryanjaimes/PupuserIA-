-- ═══════════════════════════════════════════════════════
-- PupuserIA — Supabase Schema Migration
-- Run this in the Supabase SQL Editor after creating your project.
--
-- Features:
--   ✅ pgvector for semantic search (AI Matchmaker)
--   ✅ Full property schema with AI enrichment fields
--   ✅ Freshness tracking (is_active, last_checked_at)
--   ✅ Row Level Security (RLS) with public read access
--   ✅ Indexes for common filter queries
--   ✅ Storage bucket for property images
-- ═══════════════════════════════════════════════════════

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Properties table
CREATE TABLE IF NOT EXISTS properties (
  -- Identity
  id              TEXT PRIMARY KEY,  -- PIA-000001 format
  title           TEXT NOT NULL DEFAULT '',
  title_es        TEXT NOT NULL DEFAULT '',
  description     TEXT NOT NULL DEFAULT '',
  description_es  TEXT NOT NULL DEFAULT '',
  english_summary TEXT,  -- AI-generated

  -- Location
  department      TEXT NOT NULL DEFAULT '',
  municipio       TEXT NOT NULL DEFAULT '',
  address         TEXT DEFAULT '',
  latitude        DOUBLE PRECISION DEFAULT 0,
  longitude       DOUBLE PRECISION DEFAULT 0,

  -- Listing details
  price_usd           DOUBLE PRECISION,
  ai_valuation_usd    DOUBLE PRECISION,
  bedrooms            INTEGER,
  bathrooms           INTEGER,
  area_m2             DOUBLE PRECISION,
  lot_size_m2         DOUBLE PRECISION,
  property_type       TEXT DEFAULT 'unknown',

  -- Media
  thumbnail_url   TEXT,
  images          TEXT[] DEFAULT '{}',         -- Original CDN URLs
  images_storage  TEXT[] DEFAULT '{}',         -- Supabase Storage paths

  -- Quality & completeness
  is_featured         BOOLEAN DEFAULT FALSE,
  neighborhood_score  DOUBLE PRECISION DEFAULT 0,
  completeness_score  DOUBLE PRECISION DEFAULT 0,
  quality_tier        TEXT DEFAULT 'bronze',   -- gold, silver, bronze
  missing_fields      TEXT[] DEFAULT '{}',
  ad_ready            BOOLEAN DEFAULT FALSE,

  -- AI enrichment (from enrich_ai.py)
  impact_score            INTEGER,             -- 1-10
  is_single_story         BOOLEAN,
  needs_remodel           BOOLEAN,
  ideal_for               TEXT[] DEFAULT '{}', -- families, retirees, surfers, etc.
  family_friendly_score   INTEGER,             -- 1-10
  investment_potential     INTEGER,             -- 1-10
  surf_proximity          TEXT DEFAULT 'far',  -- near / far
  walkability_estimate    TEXT DEFAULT 'low',  -- high / medium / low

  -- Vector embedding for semantic search
  embedding       vector(768),   -- Compatible with Gemini text-embedding-004 (768d)
                                 -- Change to 1536 for OpenAI text-embedding-3-small

  -- Source tracking
  source          TEXT,          -- 'encuentra24', 'realtor', etc.
  source_url      TEXT,          -- Original listing URL
  seller          TEXT,

  -- Freshness
  is_active           BOOLEAN DEFAULT TRUE,
  listing_date        TIMESTAMPTZ,
  last_checked_at     TIMESTAMPTZ,
  freshness_status    TEXT DEFAULT 'unknown',  -- active, stale, error

  -- Timestamps
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_properties_department     ON properties (department);
CREATE INDEX IF NOT EXISTS idx_properties_municipio      ON properties (municipio);
CREATE INDEX IF NOT EXISTS idx_properties_price          ON properties (price_usd);
CREATE INDEX IF NOT EXISTS idx_properties_type           ON properties (property_type);
CREATE INDEX IF NOT EXISTS idx_properties_bedrooms       ON properties (bedrooms);
CREATE INDEX IF NOT EXISTS idx_properties_featured       ON properties (is_featured) WHERE is_featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_properties_active         ON properties (is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_properties_quality        ON properties (quality_tier);
CREATE INDEX IF NOT EXISTS idx_properties_ideal_for      ON properties USING GIN (ideal_for);

-- 4. Vector similarity search index (IVFFlat — faster for < 100k rows)
-- If you have > 100k rows, consider HNSW instead
CREATE INDEX IF NOT EXISTS idx_properties_embedding ON properties
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 50);

-- 5. Full-text search
ALTER TABLE properties ADD COLUMN IF NOT EXISTS fts tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || coalesce(english_summary, ''))
  ) STORED;
CREATE INDEX IF NOT EXISTS idx_properties_fts ON properties USING GIN (fts);

-- 6. Updated_at trigger
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS properties_updated_at ON properties;
CREATE TRIGGER properties_updated_at
  BEFORE UPDATE ON properties
  FOR EACH ROW
  EXECUTE FUNCTION update_modified_column();

-- 7. Row Level Security
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

-- Public read access (no auth needed to browse properties)
CREATE POLICY "Public read" ON properties
  FOR SELECT USING (TRUE);

-- Only service role can insert/update/delete
CREATE POLICY "Service write" ON properties
  FOR ALL USING (auth.role() = 'service_role');

-- 8. Semantic search function (called from your API)
CREATE OR REPLACE FUNCTION match_properties(
  query_embedding vector(768),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 10,
  filter_department TEXT DEFAULT NULL,
  filter_max_price DOUBLE PRECISION DEFAULT NULL,
  filter_bedrooms INT DEFAULT NULL
)
RETURNS TABLE (
  id TEXT,
  title TEXT,
  department TEXT,
  municipio TEXT,
  price_usd DOUBLE PRECISION,
  bedrooms INTEGER,
  bathrooms INTEGER,
  area_m2 DOUBLE PRECISION,
  thumbnail_url TEXT,
  english_summary TEXT,
  ideal_for TEXT[],
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.id,
    p.title,
    p.department,
    p.municipio,
    p.price_usd,
    p.bedrooms,
    p.bathrooms,
    p.area_m2,
    p.thumbnail_url,
    p.english_summary,
    p.ideal_for,
    1 - (p.embedding <=> query_embedding) AS similarity
  FROM properties p
  WHERE
    p.is_active = TRUE
    AND p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
    AND (filter_department IS NULL OR p.department = filter_department)
    AND (filter_max_price IS NULL OR p.price_usd <= filter_max_price)
    AND (filter_bedrooms IS NULL OR p.bedrooms >= filter_bedrooms)
  ORDER BY p.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- 9. Stats view (for dashboard)
CREATE OR REPLACE VIEW property_stats AS
SELECT
  COUNT(*) AS total_listings,
  COUNT(*) FILTER (WHERE is_active) AS active_listings,
  COUNT(*) FILTER (WHERE is_featured) AS featured_listings,
  COUNT(*) FILTER (WHERE quality_tier = 'gold') AS gold_tier,
  COUNT(*) FILTER (WHERE quality_tier = 'silver') AS silver_tier,
  COUNT(*) FILTER (WHERE quality_tier = 'bronze') AS bronze_tier,
  ROUND(AVG(price_usd)::numeric, 0) AS avg_price,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_usd)::numeric, 0) AS median_price,
  COUNT(DISTINCT department) AS departments,
  COUNT(DISTINCT municipio) AS municipalities,
  COUNT(*) FILTER (WHERE embedding IS NOT NULL) AS with_embeddings,
  COUNT(*) FILTER (WHERE english_summary IS NOT NULL) AS with_ai_summary
FROM properties;

-- 10. Department stats view
CREATE OR REPLACE VIEW department_stats AS
SELECT
  department,
  COUNT(*) AS listing_count,
  COUNT(*) FILTER (WHERE is_active) AS active_count,
  ROUND(AVG(price_usd)::numeric, 0) AS avg_price,
  ROUND(AVG(completeness_score)::numeric, 1) AS avg_completeness,
  array_agg(DISTINCT property_type) AS property_types
FROM properties
WHERE department != ''
GROUP BY department
ORDER BY listing_count DESC;
