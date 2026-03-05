-- ═══════════════════════════════════════════════════════
-- PupuserIA — Supabase Storage Bucket Setup
-- Run after 001_schema.sql
-- ═══════════════════════════════════════════════════════

-- Create a public storage bucket for property images
INSERT INTO storage.buckets (id, name, public)
VALUES ('property-images', 'property-images', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Allow public read access to property images
CREATE POLICY "Public image read" ON storage.objects
  FOR SELECT USING (bucket_id = 'property-images');

-- Only service role can upload/delete
CREATE POLICY "Service image write" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'property-images' AND auth.role() = 'service_role');

CREATE POLICY "Service image delete" ON storage.objects
  FOR DELETE USING (bucket_id = 'property-images' AND auth.role() = 'service_role');
