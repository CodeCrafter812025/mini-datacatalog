import csv
import sqlite3

DB_FILE = "datacatalog.db"
SCHEMAS_FILE = "schemas.csv"
TABLES_FILE = "tables_name.csv"

def load_data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # ایجاد جدول‌ها در صورت نبودن
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS schemas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        schema_id INTEGER NOT NULL,
        FOREIGN KEY (schema_id) REFERENCES schemas(id)
    );
    CREATE TABLE IF NOT EXISTS etl_tables (
        etl_id INTEGER NOT NULL,
        table_id INTEGER NOT NULL,
        UNIQUE (etl_id, table_id)
    );
    """)
    # بارگذاری schemas
    with open(SCHEMAS_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            if name:
                cur.execute("INSERT OR IGNORE INTO schemas(name) VALUES (?)", (name,))
    # بارگذاری جداول و ارتباط با ETL
    with open(TABLES_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tbl_name = row["name"].strip()
            schema_name = row["schema_name"].strip()
            etl_name = row["etl_name"].strip()
            # یافتن schema_id
            cur.execute("SELECT id FROM schemas WHERE name=?", (schema_name,))
            res = cur.fetchone()
            if not res:
                continue
            schema_id = res[0]
            # درج جدول در جدول tables
            cur.execute("INSERT OR IGNORE INTO tables(name, schema_id) VALUES (?, ?)", (tbl_name, schema_id))
            cur.execute("SELECT id FROM tables WHERE name=? AND schema_id=?", (tbl_name, schema_id))
            table_id = cur.fetchone()[0]
            # یافتن etl_id
            cur.execute("SELECT id FROM etls WHERE name=?", (etl_name,))
            res = cur.fetchone()
            if not res:
                continue
            etl_id = res[0]
            # ارتباط در etl_tables
            cur.execute("INSERT OR IGNORE INTO etl_tables(etl_id, table_id) VALUES (?, ?)", (etl_id, table_id))
    conn.commit()
    conn.close()
    print("Schemas and tables loaded successfully.")

if __name__ == "__main__":
    load_data()
