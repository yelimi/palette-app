import pytest


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "name": "상품테스트유저", "email": "prod@example.com", "password": "pass1234"
    })
    res = client.post("/auth/login", json={"email": "prod@example.com", "password": "pass1234"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_products_requires_auth(client):
    response = client.get("/products")
    assert response.status_code == 403


def test_products_returns_paginated_response(client, auth_headers):
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    for field in ["total", "page", "limit", "total_pages", "items"]:
        assert field in data
    assert isinstance(data["items"], list)


def test_products_default_page_size(client, auth_headers):
    response = client.get("/products", headers=auth_headers)
    data = response.json()
    assert len(data["items"]) <= 20


def test_products_custom_limit(client, auth_headers):
    response = client.get("/products?limit=5", headers=auth_headers)
    data = response.json()
    assert len(data["items"]) <= 5


def test_products_limit_max_100(client, auth_headers):
    response = client.get("/products?limit=200", headers=auth_headers)
    assert response.status_code == 422


def test_products_page_2(client, auth_headers):
    r1 = client.get("/products?page=1&limit=2", headers=auth_headers)
    r2 = client.get("/products?page=2&limit=2", headers=auth_headers)
    ids_p1 = [p["id"] for p in r1.json()["items"]]
    ids_p2 = [p["id"] for p in r2.json()["items"]]
    assert set(ids_p1).isdisjoint(set(ids_p2))


def test_products_items_have_required_fields(client, auth_headers):
    response = client.get("/products", headers=auth_headers)
    item = response.json()["items"][0]
    for field in ["id", "name", "gender", "category", "subcategory", "color_name", "hex", "price"]:
        assert field in item


def test_products_sorted_by_color_distance(client, auth_headers):
    response = client.get("/products?color=%2326354A&limit=1", headers=auth_headers)
    items = response.json()["items"]
    assert items[0]["hex"] == "#26354A"


def test_products_filter_by_gender(client, auth_headers):
    response = client.get("/products?gender=남성&limit=100", headers=auth_headers)
    data = response.json()
    assert all(p["gender"] == "남성" for p in data["items"])


def test_products_filter_by_category(client, auth_headers):
    response = client.get("/products?category=상의&limit=100", headers=auth_headers)
    data = response.json()
    assert all(p["category"] == "상의" for p in data["items"])


def test_products_filter_by_subcategory(client, auth_headers):
    response = client.get("/products?subcategory=카디건&limit=100", headers=auth_headers)
    data = response.json()
    assert all(p["subcategory"] == "카디건" for p in data["items"])


def test_products_combined_filter(client, auth_headers):
    response = client.get("/products?gender=남성&category=바지&limit=100", headers=auth_headers)
    data = response.json()
    assert all(p["gender"] == "남성" and p["category"] == "바지" for p in data["items"])


def test_products_no_results_for_nonexistent_filter(client, auth_headers):
    response = client.get("/products?gender=어린이", headers=auth_headers)
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_products_total_pages_calculation(client, auth_headers):
    response = client.get("/products?limit=2", headers=auth_headers)
    data = response.json()
    expected_pages = (data["total"] + 1) // 2
    assert data["total_pages"] == expected_pages


def test_get_product_by_id(client, auth_headers):
    first = client.get("/products", headers=auth_headers).json()["items"][0]
    response = client.get(f"/products/{first['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == first["id"]


def test_get_product_by_id_not_found(client, auth_headers):
    response = client.get("/products/999999", headers=auth_headers)
    assert response.status_code == 404


def test_get_product_by_id_requires_auth(client):
    response = client.get("/products/1")
    assert response.status_code == 403
