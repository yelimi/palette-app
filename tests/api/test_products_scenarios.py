from .helpers import assert_error_detail, auth_header, login, register, timed, unique_email

PRODUCT_FIELDS = ["id", "name", "gender", "category", "subcategory", "color_name", "hex", "price"]
LIST_FIELDS = ["total", "page", "limit", "total_pages", "items"]


def _get(client, url, headers):
    return timed(client.get, url, headers=headers)


def test_TC115_no_filter(client):
    headers = auth_header(client)
    response = _get(client, "/products", headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert body["limit"] == 20
    assert len(body["items"]) <= 20
    for field in LIST_FIELDS:
        assert field in body
    for item in body["items"]:
        for field in PRODUCT_FIELDS:
            assert field in item


def test_TC116_filter_gender_unisex(client):
    response = _get(client, "/products?gender=공용", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["gender"] == "공용" for p in body["items"])


def test_TC117_filter_gender_male(client):
    response = _get(client, "/products?gender=남성&limit=100", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["gender"] == "남성" for p in body["items"])


def test_TC118_filter_gender_female(client):
    response = _get(client, "/products?gender=여성&limit=50", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["gender"] == "여성" for p in body["items"])


def test_TC119_filter_category(client):
    response = _get(client, "/products?category=상의&limit=100", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["category"] == "상의" for p in body["items"])


def test_TC120_filter_subcategory(client):
    response = _get(client, "/products?subcategory=셔츠/블라우스&limit=80", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["subcategory"] == "셔츠/블라우스" for p in body["items"])


def test_TC121_sort_by_color(client):
    response = _get(client, "/products?color=1B2B4B&limit=40", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert body["items"][0]["hex"].upper() == "#1B2B4B"


def test_TC122_filter_nonexistent_value(client):
    response = _get(client, "/products?gender=아동", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_TC123_filter_combined_gender_category(client):
    headers = auth_header(client)
    response = _get(client, "/products?gender=여성&category=바지", headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    for p in body["items"]:
        assert p["gender"] == "여성"
        assert p["category"] == "바지"


def test_TC124_pagination(client):
    headers = auth_header(client)
    page1 = _get(client, "/products?page=1&limit=20", headers)
    page2 = _get(client, "/products?page=2&limit=20", headers)
    assert page1.status_code == 200
    assert page2.status_code == 200
    body1, body2 = page1.json(), page2.json()
    assert body2["total"] > 0
    assert body2["page"] == 2
    assert len(body2["items"]) <= 20
    ids1 = {p["id"] for p in body1["items"]}
    ids2 = {p["id"] for p in body2["items"]}
    assert ids1.isdisjoint(ids2)


def test_TC125_pagination_out_of_range(client):
    response = _get(client, "/products?page=9999&limit=20", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert body["page"] == 9999
    assert body["items"] == []


def test_TC126_pagination_page_below_min(client):
    response = _get(client, "/products?page=0&limit=20", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC127_pagination_custom_limit(client):
    response = _get(client, "/products?limit=5", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 5
    assert len(body["items"]) <= 5


def test_TC128_pagination_limit_exceeds_max(client):
    response = _get(client, "/products?limit=101", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC129_pagination_limit_below_min(client):
    response = _get(client, "/products?limit=0", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC130_list_without_login(client):
    response = timed(client.get, "/products")
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC131_list_invalid_token(client):
    response = _get(client, "/products", {"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC132_list_logged_out_token(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = _get(client, "/products", headers)
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC133_get_product_success(client):
    headers = auth_header(client)
    first = _get(client, "/products?limit=1", headers).json()["items"][0]
    response = _get(client, f"/products/{first['id']}", headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == first["id"]
    for field in PRODUCT_FIELDS:
        assert field in body


def test_TC134_get_product_not_found(client):
    response = _get(client, "/products/99999999", auth_header(client))
    assert response.status_code == 404
    assert_error_detail(response)


def test_TC135_product_id_non_numeric(client):
    response = _get(client, "/products/abc", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC136_get_product_without_login(client):
    response = timed(client.get, "/products/1")
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC137_get_product_invalid_token(client):
    response = _get(client, "/products/1", {"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC138_get_product_logged_out_token(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = _get(client, "/products/1", headers)
    assert response.status_code == 401
    assert_error_detail(response)
