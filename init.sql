-- ایجاد کاربر admin
CREATE USER admin WITH PASSWORD 'admin123';
ALTER USER admin CREATEDB;
CREATE DATABASE catalogdb OWNER admin;
CREATE DATABASE gnaf OWNER admin;
GRANT ALL PRIVILEGES ON DATABASE catalogdb TO admin;
GRANT ALL PRIVILEGES ON DATABASE gnaf TO admin;

-- اتصال به دیتابیس catalogdb
\c catalogdb;

-- ایجاد جداول
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    etl_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS table_meta (
    id SERIAL PRIMARY KEY,
    schema_name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    description TEXT,
    source_id INTEGER REFERENCES data_sources(id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS database_connections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    connection_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- افزودن کاربر admin پیش‌فرض
INSERT INTO users (username, hashed_password) VALUES 
('admin', '')
ON CONFLICT (username) DO NOTHING;
