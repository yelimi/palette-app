import pytest


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "name": "장바구니유저", "email": "cart@example.com", "password": "pass1234"
    })
    res = client.post("/auth/login", json={"email": "cart@example.com", "password": "pass1234"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_cart_requires_auth(client):
    assert client.get("/cart").status_code == 403


def test_cart_initially_empty(client, auth_headers):
    response = client.get("/cart", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_add_to_cart(client, auth_headers):
    response = client.post("/cart", json={"product_id": 1}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == 1
    assert "product" in data


def test_cart_shows_added_item(client, auth_headers):
    client.post("/cart", json={"product_id": 1}, headers=auth_headers)
    response = client.get("/cart", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    assert items[0]["product_id"] == 1


def test_delete_cart_item(client, auth_headers):
    add_res = client.post("/cart", json={"product_id": 1}, headers=auth_headers)
    cart_id = add_res.json()["id"]
    del_res = client.delete(f"/cart/{cart_id}", headers=auth_headers)
    assert del_res.status_code == 204


def test_delete_other_users_cart_returns_404(client):
    client.post("/auth/register", json={"name": "유저A", "email": "a@ex.com", "password": "pass1234"})
    client.post("/auth/register", json={"name": "유저B", "email": "b@ex.com", "password": "pass1234"})
    token_a = client.post("/auth/login", json={"email": "a@ex.com", "password": "pass1234"}).json()["access_token"]
    token_b = client.post("/auth/login", json={"email": "b@ex.com", "password": "pass1234"}).json()["access_token"]
    add_res = client.post("/cart", json={"product_id": 1}, headers={"Authorization": f"Bearer {token_a}"})
    cart_id = add_res.json()["id"]
    del_res = client.delete(f"/cart/{cart_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_res.status_code == 404
