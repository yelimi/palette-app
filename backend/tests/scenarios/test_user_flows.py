from pathlib import Path

from .helpers import unique_email

FIXTURES = Path(__file__).resolve().parents[3] / "postman" / "fixtures"


def _register(client, name, email, password):
    return client.post("/auth/register", json={"name": name, "email": email, "password": password})


def _login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_user_flow(client):
    """회원가입 -> 로그인 -> 사진 업로드 -> 색상 추천 -> 상품 구매"""
    email = unique_email()
    password = "Test1234!"

    register_res = _register(client, "홍이사", email, password)
    assert register_res.status_code == 201

    login_res = _login(client, email, password)
    assert login_res.status_code == 200
    login_body = login_res.json()
    assert "access_token" in login_body
    headers = {"Authorization": f"Bearer {login_body['access_token']}"}

    image_data = (FIXTURES / "ex_jpg.jpg").read_bytes()
    color_res = client.post(
        "/colors/extract",
        files={"file": ("ex_jpg.jpg", image_data, "image/jpeg")},
        headers=headers,
    )
    assert color_res.status_code == 200
    color_body = color_res.json()
    assert len(color_body["recommendations"]) == 5
    recommended_color = color_body["recommendations"][0]["hex"].replace("#", "")

    products_res = client.get(f"/products?color={recommended_color}&limit=5", headers=headers)
    assert products_res.status_code == 200
    products_body = products_res.json()
    assert len(products_body["items"]) > 0
    product_id = products_body["items"][0]["id"]

    add_cart_res = client.post("/cart", json={"product_id": product_id}, headers=headers)
    assert add_cart_res.status_code == 201
    add_cart_body = add_cart_res.json()
    assert add_cart_body["product_id"] == product_id
    cart_id = add_cart_body["id"]

    get_cart_res = client.get("/cart", headers=headers)
    assert get_cart_res.status_code == 200
    cart_product_ids = [item["product_id"] for item in get_cart_res.json()]
    assert product_id in cart_product_ids

    delete_cart_res = client.delete(f"/cart/{cart_id}", headers=headers)
    assert delete_cart_res.status_code == 204


def test_auth_change(client):
    """로그인 -> 비밀번호 변경 -> 재로그인"""
    email = unique_email()
    initial_password = "Test1234!"
    new_password = "newPass1234!"

    register_res = _register(client, "장이사", email, initial_password)
    assert register_res.status_code == 201

    first_login_res = _login(client, email, initial_password)
    assert first_login_res.status_code == 200
    first_login_body = first_login_res.json()
    assert "access_token" in first_login_body
    headers = {"Authorization": f"Bearer {first_login_body['access_token']}"}

    change_res = client.patch(
        "/auth/password",
        json={"current_password": initial_password, "new_password": new_password},
        headers=headers,
    )
    assert change_res.status_code == 200

    relogin_res = _login(client, email, new_password)
    assert relogin_res.status_code == 200
    assert "access_token" in relogin_res.json()


def test_account_lock_recovery(client):
    """3회 로그인 실패 후 계정 잠김 -> 비밀번호 재설정 -> 로그인"""
    email = unique_email()
    correct_password = "Test1234!"
    wrong_password = "wrong1234!"
    new_password = "recover1234!"

    register_res = _register(client, "홍길", email, correct_password)
    assert register_res.status_code == 201

    for _ in range(2):
        attempt_res = _login(client, email, wrong_password)
        assert attempt_res.status_code == 401

    # 3번째 실패에서 failed_attempts가 임계치(3)에 도달해 이 응답 자체가 423으로 잠김
    third_attempt_res = _login(client, email, wrong_password)
    assert third_attempt_res.status_code == 423

    reset_res = client.post(
        "/auth/password/reset",
        json={"email": email, "new_password": new_password},
    )
    assert reset_res.status_code == 200

    login_after_reset_res = _login(client, email, new_password)
    assert login_after_reset_res.status_code == 200
    assert "access_token" in login_after_reset_res.json()


def test_session_end_restart(client):
    """로그인 -> 로그아웃 -> 재로그인"""
    email = unique_email()
    password = "Test1234!"

    register_res = _register(client, "장이", email, password)
    assert register_res.status_code == 201

    first_login_res = _login(client, email, password)
    assert first_login_res.status_code == 200
    first_login_body = first_login_res.json()
    assert "access_token" in first_login_body
    headers = {"Authorization": f"Bearer {first_login_body['access_token']}"}

    logout_res = client.post("/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    products_res = client.get("/products", headers=headers)
    assert products_res.status_code == 401

    login_again_res = _login(client, email, password)
    assert login_again_res.status_code == 200
    assert "access_token" in login_again_res.json()


def test_cart_management(client):
    """로그인 -> 상품 저장 -> 장바구니 조회 -> 상품 삭제 -> 장바구니 조회"""
    email = unique_email()
    password = "Test1234!"

    register_res = _register(client, "장이수", email, password)
    assert register_res.status_code == 201

    login_res = _login(client, email, password)
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
