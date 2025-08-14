-- ???????? ?????: ???? ????? ????

-- ???? schema ??? ???? ?????
CREATE SCHEMA IF NOT EXISTS catalog_test;

-- ???? schemas
CREATE TABLE IF NOT EXISTS catalog_test.schemas (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ???? tables_name
CREATE TABLE IF NOT EXISTS catalog_test.tables_name (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    etl_name TEXT,
    schema_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schema_id) REFERENCES catalog_test.schemas(id)
);

-- ???? etl_processes
CREATE TABLE IF NOT EXISTS catalog_test.etl_processes (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ???? etl_table_relations
CREATE TABLE IF NOT EXISTS catalog_test.etl_table_relations (
    id SERIAL PRIMARY KEY,
    etl_id INTEGER REFERENCES catalog_test.etl_processes(id),
    table_id INTEGER REFERENCES catalog_test.tables_name(id),
    usage_type TEXT DEFAULT 'both',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
