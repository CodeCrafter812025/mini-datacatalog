# tests/test_audit.py
def test_audit_recent(client, auth_headers):
    # فقط بررسی می‌کنیم endpoint کار می‌کند و لیست برمی‌گرداند
    r = client.get("/audit/recent?limit=5", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # اگر لاگین در همان تست‌ها انجام شده باشد، معمولاً حداقل یک رکورد login داریم
    # (تضمینی نمی‌گیریم که چه اکشنی باشد)
