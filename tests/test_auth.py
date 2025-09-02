def test_token_and_me(client, token):
    r = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    js = r.json()
    assert js.get("username") == "admin"
    assert js.get("is_active") is True
