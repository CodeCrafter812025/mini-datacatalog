#!/bin/bash
# ایجاد کاربر admin
psql -U postgres -c "CREATE USER admin WITH PASSWORD 'admin123';"
psql -U postgres -c "ALTER USER admin CREATEDB;"
psql -U postgres -c "CREATE DATABASE catalogdb OWNER admin;"
psql -U postgres -c "CREATE DATABASE gnaf OWNER admin;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE catalogdb TO admin;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE gnaf TO admin;"
