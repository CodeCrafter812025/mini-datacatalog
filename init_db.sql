-- ایجاد جداول مورد نیاز
CREATE TABLE IF NOT EXISTS etls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tables (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    etl_id INTEGER REFERENCES etls(id) ON DELETE CASCADE
);

-- ایجاد جدول کاربران (اگر وجود ندارد)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ایجاد کاربر admin
INSERT INTO users (username, hashed_password) VALUES
('admin', '\\\')
ON CONFLICT (username) DO NOTHING;
