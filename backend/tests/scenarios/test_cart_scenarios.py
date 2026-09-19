from .helpers import auth_header, login, register, unique_email


def _existing_product_id(client, headers):
    return client.get("/products?limit=1", headers=headers).json()["items"][0]["id"]


def test_TC139_상품_담기(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    response = client.post("/cart", json={"product_id": product_id}, headers=headers)
    assert response.status_code == 201


def test_TC140_존재하지_않는_product_id로_담기(client):
    headers = auth_header(client)
    response = client.post("/cart", json={"product_id": 99999999}, headers=headers)
    assert response.status_code == 404


def test_TC141_product_id_누락(client):
    headers = auth_header(client)
    response = client.post("/cart", json={}, headers=headers)
    assert response.status_code == 422


def test_TC142_product_id가_숫자가_아닌_경우(client):
    headers = auth_header(client)
    response = client.post("/cart", json={"product_id": "ABC"}, headers=headers)
    assert response.status_code == 422


def test_TC143_같은_상품_중복_담기(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    client.post("/cart", json={"product_id": product_id}, headers=headers)
    response = client.post("/cart", json={"product_id": product_id}, headers=headers)
    assert response.status_code == 201


def test_TC144_로그인_없이_담기(client):
    response = client.post("/cart", json={"product_id": 1})
    assert response.status_code == 403


def test_TC145_유효하지_않은_토큰으로_담기(client):
    response = client.post("/cart", json={"product_id": 1}, headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401


def test_TC146_로그아웃된_토큰으로_담기(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = client.post("/cart", json={"product_id": 1}, headers=headers)
    assert response.status_code == 401


def test_TC147_빈_장바구니_조회(client):
    headers = auth_header(client)
    response = client.get("/cart", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_TC148_장바구니에서_상품_조회(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    client.post("/cart", json={"product_id": product_id}, headers=headers)
    response = client.get("/cart", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_TC149_다른_유저_장바구니_안_보임(client):
    headers1 = auth_header(client)
    product_id = _existing_product_id(client, headers1)
    client.post("/cart", json={"product_id": product_id}, headers=headers1)

    headers2 = auth_header(client)
    response = client.get("/cart", headers=headers2)
    assert response.status_code == 200
    assert response.json() == []


def test_TC150_로그인_없이_조회(client):
    response = client.get("/cart")
    assert response.status_code == 403


def test_TC151_유효하지_않은_토큰으로_조회(client):
    response = client.get("/cart", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401


def test_TC152_로그아웃된_토큰으로_조회(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = client.get("/cart", headers=headers)
    assert response.status_code == 401


def test_TC153_장바구니에서_상품_삭제(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    cart_id = client.post("/cart", json={"product_id": product_id}, headers=headers).json()["id"]
    response = client.delete(f"/cart/{cart_id}", headers=headers)
    assert response.status_code == 204


def test_TC154_존재하지_않는_cart_id로_삭제(client):
    headers = auth_header(client)
    response = client.delete("/cart/9999999", headers=headers)
    assert response.status_code == 404


def test_TC155_cart_id가_숫자가_아닌_경우(client):
    headers = auth_header(client)
    response = client.delete("/cart/ABC", headers=headers)
    assert response.status_code == 422


def test_TC156_다른_유저의_장바구니_삭제_시도(client):
    headers1 = auth_header(client)
    product_id = _existing_product_id(client, headers1)
    cart_id = client.post("/cart", json={"product_id": product_id}, headers=headers1).json()["id"]

    headers2 = auth_header(client)
    response = client.delete(f"/cart/{cart_id}", headers=headers2)
    assert response.status_code == 404


def test_TC157_로그인_없이_삭제(client):
    response = client.delete("/cart/10")
    assert response.status_code == 403


def test_TC158_유효하지_않은_토큰으로_삭제(client):
    response = client.delete("/cart/10", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401


def test_TC159_로그아웃된_토큰으로_삭제(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = client.delete("/cart/10", headers=headers)
    assert response.status_code == 401
