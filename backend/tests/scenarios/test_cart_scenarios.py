from .helpers import assert_error_detail, auth_header, login, register, timed, unique_email


def _existing_product_id(client, headers):
    return client.get("/products?limit=1", headers=headers).json()["items"][0]["id"]


def _post(client, url, headers, json=None):
    return timed(client.post, url, json=json, headers=headers)


def _get(client, url, headers):
    return timed(client.get, url, headers=headers)


def _delete(client, url, headers):
    return timed(client.delete, url, headers=headers)


def test_TC139_상품_담기(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    response = _post(client, "/cart", headers, json={"product_id": product_id})
    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] == product_id
    assert "id" in body
    assert "product" in body
    assert body["product"]["id"] == product_id


def test_TC140_존재하지_않는_product_id로_담기(client):
    headers = auth_header(client)
    response = _post(client, "/cart", headers, json={"product_id": 99999999})
    assert response.status_code == 404
    assert_error_detail(response)


def test_TC141_product_id_누락(client):
    headers = auth_header(client)
    response = _post(client, "/cart", headers, json={})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC142_product_id가_숫자가_아닌_경우(client):
    headers = auth_header(client)
    response = _post(client, "/cart", headers, json={"product_id": "ABC"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC143_같은_상품_중복_담기(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    _post(client, "/cart", headers, json={"product_id": product_id})
    response = _post(client, "/cart", headers, json={"product_id": product_id})
    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] == product_id
    assert "id" in body
    assert "product" in body
    assert body["product"]["id"] == product_id


def test_TC144_로그인_없이_담기(client):
    response = timed(client.post, "/cart", json={"product_id": 1})
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC145_유효하지_않은_토큰으로_담기(client):
    response = _post(client, "/cart", {"Authorization": "Bearer invalidtoken123"}, json={"product_id": 1})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC146_로그아웃된_토큰으로_담기(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = _post(client, "/cart", headers, json={"product_id": 1})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC147_빈_장바구니_조회(client):
    headers = auth_header(client)
    response = _get(client, "/cart", headers)
    assert response.status_code == 200
    assert response.json() == []


def test_TC148_장바구니에서_상품_조회(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    _post(client, "/cart", headers, json={"product_id": product_id})
    response = _get(client, "/cart", headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    assert product_id in [item["product_id"] for item in body]
    for item in body:
        assert "id" in item
        assert "product_id" in item
        assert "product" in item


def test_TC149_다른_유저_장바구니_안_보임(client):
    headers1 = auth_header(client)
    product_id = _existing_product_id(client, headers1)
    _post(client, "/cart", headers1, json={"product_id": product_id})

    headers2 = auth_header(client)
    response = _get(client, "/cart", headers2)
    assert response.status_code == 200
    body = response.json()
    assert body == []
    assert product_id not in [item["product_id"] for item in body]


def test_TC150_로그인_없이_조회(client):
    response = timed(client.get, "/cart")
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC151_유효하지_않은_토큰으로_조회(client):
    response = _get(client, "/cart", {"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC152_로그아웃된_토큰으로_조회(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = _get(client, "/cart", headers)
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC153_장바구니에서_상품_삭제(client):
    headers = auth_header(client)
    product_id = _existing_product_id(client, headers)
    cart_id = _post(client, "/cart", headers, json={"product_id": product_id}).json()["id"]
    response = _delete(client, f"/cart/{cart_id}", headers)
    assert response.status_code == 204
    assert response.text == ""


def test_TC154_존재하지_않는_cart_id로_삭제(client):
    headers = auth_header(client)
    response = _delete(client, "/cart/9999999", headers)
    assert response.status_code == 404
    assert_error_detail(response)


def test_TC155_cart_id가_숫자가_아닌_경우(client):
    headers = auth_header(client)
    response = _delete(client, "/cart/ABC", headers)
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC156_다른_유저의_장바구니_삭제_시도(client):
    headers1 = auth_header(client)
    product_id = _existing_product_id(client, headers1)
    cart_id = _post(client, "/cart", headers1, json={"product_id": product_id}).json()["id"]

    headers2 = auth_header(client)
    response = _delete(client, f"/cart/{cart_id}", headers2)
    assert response.status_code == 404
    assert_error_detail(response)


def test_TC157_로그인_없이_삭제(client):
    response = timed(client.delete, "/cart/10")
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC158_유효하지_않은_토큰으로_삭제(client):
    response = _delete(client, "/cart/10", {"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC159_로그아웃된_토큰으로_삭제(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = _delete(client, "/cart/10", headers)
    assert response.status_code == 401
    assert_error_detail(response)
