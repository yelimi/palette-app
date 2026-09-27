from pathlib import Path

from .helpers import login, register, unique_email

FIXTURES = Path(__file__).resolve().parents[3] / "postman" / "fixtures"


def test_user_flow(client):
    """회원가입 -> 로그인 -> 사진 업로드 -> 색상 추천 -> 상품 구매"""
    email = unique_email()
    password = "Test1234!"

    register_res = register(client, name="홍이사", email=email, password=password)
    assert register_res.status_code == 201

    login_res = login(client, email, password)
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
