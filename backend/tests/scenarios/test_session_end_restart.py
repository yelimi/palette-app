from .helpers import login, register, unique_email


def test_session_end_restart(client):
    """로그인 -> 로그아웃 -> 재로그인"""
    email = unique_email()
    password = "Test1234!"

    register_res = register(client, name="장이", email=email, password=password)
    assert register_res.status_code == 201

    first_login_res = login(client, email, password)
    assert first_login_res.status_code == 200
    first_login_body = first_login_res.json()
    assert "access_token" in first_login_body
    headers = {"Authorization": f"Bearer {first_login_body['access_token']}"}

    logout_res = client.post("/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    products_res = client.get("/products", headers=headers)
    assert products_res.status_code == 401

    login_again_res = login(client, email, password)
    assert login_again_res.status_code == 200
    assert "access_token" in login_again_res.json()
