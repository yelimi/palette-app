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
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_products_have_required_fields(client, auth_headers):
    response = client.get("/products", headers=auth_headers)
    product = response.json()[0]
    for field in ["id", "name", "gender", "category", "subcategory", "color_name", "hex", "price"]:
        assert field in product


def test_products_sorted_by_color_distance(client, auth_headers):
    response = client.get("/products?color=%2326354A", headers=auth_headers)
    products = response.json()
    assert products[0]["hex"] == "#26354A"


def test_products_filter_by_gender(client, auth_headers):
    response = client.get("/products?gender=남성", headers=auth_headers)
    assert response.status_code == 200
    products = response.json()
    assert all(p["gender"] == "남성" for p in products)


def test_products_filter_by_category(client, auth_headers):
    response = client.get("/products?category=상의", headers=auth_headers)
    assert response.status_code == 200
    products = response.json()
    assert all(p["category"] == "상의" for p in products)


def test_products_filter_by_subcategory(client, auth_headers):
    response = client.get("/products?subcategory=카디건", headers=auth_headers)
    assert response.status_code == 200
    products = response.json()
    assert all(p["subcategory"] == "카디건" for p in products)


def test_products_combined_filter_gender_and_category(client, auth_headers):
    response = client.get("/products?gender=남성&category=바지", headers=auth_headers)
    assert response.status_code == 200
    products = response.json()
    assert all(p["gender"] == "남성" and p["category"] == "바지" for p in products)


def test_products_no_results_for_nonexistent_filter(client, auth_headers):
    response = client.get("/products?gender=어린이", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []
