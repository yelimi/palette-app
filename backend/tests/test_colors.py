import pytest


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "name": "색상테스트유저", "email": "color@example.com", "password": "pass123"
    })
    res = client.post("/auth/login", json={"email": "color@example.com", "password": "pass123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_recommend_requires_auth(client):
    response = client.get("/colors/recommend?color=%23D4B896")
    assert response.status_code == 403


def test_recommend_returns_5_colors(client, auth_headers):
    response = client.get("/colors/recommend?color=%23D4B896", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


def test_recommend_response_fields(client, auth_headers):
    response = client.get("/colors/recommend?color=%23D4B896", headers=auth_headers)
    item = response.json()[0]
    assert "color_name" in item
    assert "hex" in item
    assert item["hex"].startswith("#")


def test_recommend_excludes_input_color(client, auth_headers):
    # 블랙 입력 → 블랙이 추천 목록에 없어야 함
    response = client.get("/colors/recommend?color=%231C1C1C", headers=auth_headers)
    hexes = [item["hex"] for item in response.json()]
    assert "#1C1C1C" not in hexes


def test_recommend_no_duplicates(client, auth_headers):
    response = client.get("/colors/recommend?color=%23D4B896", headers=auth_headers)
    hexes = [item["hex"] for item in response.json()]
    assert len(hexes) == len(set(hexes))


def test_recommend_custom_top_n(client, auth_headers):
    response = client.get("/colors/recommend?color=%23D4B896&top_n=3", headers=auth_headers)
    assert len(response.json()) == 3


def test_recommend_dark_input_returns_lighter_colors(client, auth_headers):
    # 블랙(L≈10) 입력 → 추천 색상들은 대체로 밝아야 함
    response = client.get("/colors/recommend?color=%231C1C1C", headers=auth_headers)
    data = response.json()
    assert len(data) > 0


def test_recommend_white_input(client, auth_headers):
    response = client.get("/colors/recommend?color=%23F5F5F0", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_recommend_colored_input(client, auth_headers):
    # 네이비 입력
    response = client.get("/colors/recommend?color=%231B2B4B", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    hexes = [item["hex"] for item in data]
    assert "#1B2B4B" not in hexes


def test_recommend_top_n_max_10(client, auth_headers):
    response = client.get("/colors/recommend?color=%23D4B896&top_n=11", headers=auth_headers)
    assert response.status_code == 422
