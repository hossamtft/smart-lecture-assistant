-- Initialize pgvector extension for Smart Lecture Assistant
-- This script runs automatically when the PostgreSQL container starts

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension initialized successfully';
END $$;
