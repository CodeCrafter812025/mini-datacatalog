import sqlite3
conn = sqlite3.connect('datacatalog.db')
cur = conn.cursor()
for col,defn in [('email','TEXT'),('full_name','TEXT'),('is_superuser','INTEGER DEFAULT 0')]:
    try:
        cur.execute(f"ALTER TABLE users ADD COLUMN {col} {defn}")
        print('added', col)
    except Exception as e:
        print('skip', col, e)
conn.commit(); conn.close()
