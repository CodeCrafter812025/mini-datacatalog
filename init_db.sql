CREATE TABLE IF NOT EXISTS etls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tables (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    etl_id INTEGER REFERENCES etls(id) ON DELETE CASCADE
);

-- ایجاد کاربر admin
INSERT INTO users (username, hashed_password) VALUES
('admin', '\\\')
ON CONFLICT (username) DO NOTHING;
