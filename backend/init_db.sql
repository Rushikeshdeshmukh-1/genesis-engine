-- Initialize database with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial schemas
CREATE SCHEMA IF NOT EXISTS idea_engine;

-- Set search path
SET search_path TO idea_engine, public;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA idea_engine TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA idea_engine TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA idea_engine TO postgres;
