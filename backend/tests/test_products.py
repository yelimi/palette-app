import pytest


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "name": "상품테스트유저", "email": "prod@example.com", "password": "pass123"
    })
    res = client.post("/auth/login", json={"email": "prod@example.com", "password": "pass123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_products_requires_auth(client):
    response = client.get("/products?color=%2326354A")
    assert response.status_code == 403


def test_products_returns_list(client, auth_headers):
    response = client.get("/products?color=%2326354A", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_products_sorted_by_color_distance(client, auth_headers):
    response = client.get("/products?color=%2326354A", headers=auth_headers)
    products = response.json()
    assert products[0]["hex"] == "#26354A"


def test_products_no_color_param_returns_all(client, auth_headers):
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
