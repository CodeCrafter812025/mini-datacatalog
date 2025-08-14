import sqlite3, pathlib
p = pathlib.Path("test.db")
if not p.exists():
    print("test.db not found")
else:
    conn = sqlite3.connect(str(p))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print("tables:", tables)
    for t in tables:
        try:
            cur.execute(f"SELECT count(*) FROM \"{t}\"")
            print(t, "count=", cur.fetchone()[0])
        except Exception as e:
            print("error counting", t, ":", e)
    conn.close()
