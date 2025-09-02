-- مایگریشن اولیه: ساخت جداول اصلی

-- ساخت schema اگر وجود ندارد
CREATE SCHEMA IF NOT EXISTS catalog_test;

-- جدول schemas
CREATE TABLE IF NOT EXISTS catalog_test.schemas (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول tables_name
CREATE TABLE IF NOT EXISTS catalog_test.tables_name (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    etl_name TEXT,
    schema_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schema_id) REFERENCES catalog_test.schemas(id)
);

-- جدول etl_processes
CREATE TABLE IF NOT EXISTS catalog_test.etl_processes (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول etl_table_relations
CREATE TABLE IF NOT EXISTS catalog_test.etl_table_relations (
    id SERIAL PRIMARY KEY,
    etl_id INTEGER REFERENCES catalog_test.etl_processes(id),
    table_id INTEGER REFERENCES catalog_test.tables_name(id),
    usage_type TEXT DEFAULT 'both',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
