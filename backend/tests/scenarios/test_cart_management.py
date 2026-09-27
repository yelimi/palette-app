from .helpers import login, register, unique_email


def test_cart_management(client):
    """로그인 -> 상품 저장 -> 장바구니 조회 -> 상품 삭제 -> 장바구니 조회"""
    email = unique_email()
    password = "Test1234!"

    register_res = register(client, name="장이수", email=email, password=password)
    assert register_res.status_code == 201

    login_res = login(client, email, password)
    assert login_res.status_code == 200
    login_body = login_res.json()
    assert "access_token" in login_body
    headers = {"Authorization": f"Bearer {login_body['access_token']}"}

    # 서로 다른 상품 2개 선택 (원본은 page=2/limit=20/items[9]를 썼지만,
    # 현재 테스트 DB 상품 수가 적어 동일한 의도를 살려 각각 1개씩 조회)
    product1_res = client.get("/products?page=1&limit=1", headers=headers)
    assert product1_res.status_code == 200
    assert len(product1_res.json()["items"]) > 0
    product_id1 = product1_res.json()["items"][0]["id"]

    product2_res = client.get("/products?page=2&limit=1", headers=headers)
    assert product2_res.status_code == 200
    assert len(product2_res.json()["items"]) > 0
    product_id2 = product2_res.json()["items"][0]["id"]

    save1_res = client.post("/cart", json={"product_id": product_id1}, headers=headers)
    assert save1_res.status_code == 201
    assert save1_res.json()["product_id"] == product_id1

    save2_res = client.post("/cart", json={"product_id": product_id2}, headers=headers)
    assert save2_res.status_code == 201
    assert save2_res.json()["product_id"] == product_id2
    cart_id2 = save2_res.json()["id"]

    cart_before_res = client.get("/cart", headers=headers)
    assert cart_before_res.status_code == 200
    ids_before = [item["product_id"] for item in cart_before_res.json()]
    assert product_id1 in ids_before
    assert product_id2 in ids_before

    delete_res = client.delete(f"/cart/{cart_id2}", headers=headers)
    assert delete_res.status_code == 204

    cart_after_res = client.get("/cart", headers=headers)
    assert cart_after_res.status_code == 200
    ids_after = [item["product_id"] for item in cart_after_res.json()]
    assert product_id1 in ids_after
    assert product_id2 not in ids_after
