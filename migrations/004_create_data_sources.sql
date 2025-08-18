-- 004_create_data_sources.sql
-- create data_sources in public schema for app models
CREATE TABLE IF NOT EXISTS public.data_sources (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT,
  connection_string TEXT,
  description TEXT,
  owner_id INTEGER REFERENCES public.users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- optional sample data
INSERT INTO public.data_sources (name, type, connection_string, description, owner_id)
VALUES ('sample-src-1', 'postgres', 'postgresql://example', 'sample datasource 1', 1)
ON CONFLICT DO NOTHING;
