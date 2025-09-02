import io

def test_preview_ok(client, auth_headers, sample_csv_bytes):
    files = {"file": ("test.csv", sample_csv_bytes, "text/csv")}
    r = client.post("/csv/preview?max_rows=5", headers=auth_headers, files=files)
    assert r.status_code == 200, r.text
    js = r.json()
    assert "columns" in js and "rows" in js

def test_load_replace_then_append(client, auth_headers):
    # برای هر بار ارسال، BytesIO جدید بساز که stream مصرف‌شده نباشد
    def make_csv():
        return io.BytesIO(b"name,schema,etl\ncsv_from_test,public,etl1\n")

    # بار اول: replace
    files1 = {"file": ("test.csv", make_csv(), "text/csv")}
    data = {"conn_id": "1", "schema": "sales", "table_name": "csv_import", "if_exists": "replace"}
    r1 = client.post("/csv/load", headers=auth_headers, files=files1, data=data)
    assert r1.status_code == 200, r1.text
    assert r1.json().get("ok") is True

    # بار دوم: append
    files2 = {"file": ("test.csv", make_csv(), "text/csv")}
    data["if_exists"] = "append"
    r2 = client.post("/csv/load", headers=auth_headers, files=files2, data=data)
    assert r2.status_code == 200, r2.text
    assert r2.json().get("ok") is True
