-- Create users table (compatible with app/models.py)
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  is_superuser BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- seed admin user (username: admin, password: admin123)
INSERT INTO users (username, email, hashed_password, is_active, is_superuser)
VALUES ('admin', 'admin@example.com', '$2b$12$.w.a3QrUpcYSlUvog25kmu2hc2xc975oCaR17SH7v0Enu6KoP.ehO', true, true)
ON CONFLICT (username) DO NOTHING;
