from .helpers import assert_error_detail, auth_header, login, register, timed, unique_email

PRODUCT_FIELDS = ["id", "name", "gender", "category", "subcategory", "color_name", "hex", "price"]
LIST_FIELDS = ["total", "page", "limit", "total_pages", "items"]


def _get(client, url, headers):
    return timed(client.get, url, headers=headers)


def test_TC115_전체_필터_동작(client):
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


def test_TC116_공용_필터_동작(client):
    response = _get(client, "/products?gender=공용", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["gender"] == "공용" for p in body["items"])


def test_TC117_남성_필터_동작(client):
    response = _get(client, "/products?gender=남성&limit=100", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["gender"] == "남성" for p in body["items"])


def test_TC118_여성_필터_동작(client):
    response = _get(client, "/products?gender=여성&limit=50", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["gender"] == "여성" for p in body["items"])


def test_TC119_카테고리_필터_동작(client):
    response = _get(client, "/products?category=상의&limit=100", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["category"] == "상의" for p in body["items"])


def test_TC120_서브_카테고리_필터_동작(client):
    response = _get(client, "/products?subcategory=셔츠/블라우스&limit=80", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert all(p["subcategory"] == "셔츠/블라우스" for p in body["items"])


def test_TC121_컬러_필터_동작(client):
    response = _get(client, "/products?color=1B2B4B&limit=40", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert body["items"][0]["hex"].upper() == "#1B2B4B"


def test_TC122_존재하지_않는_필터값(client):
    response = _get(client, "/products?gender=아동", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_TC123_필터_조합_동작(client):
    headers = auth_header(client)
    response = _get(client, "/products?gender=여성&category=바지", headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    for p in body["items"]:
        assert p["gender"] == "여성"
        assert p["category"] == "바지"


def test_TC124_페이지네이션(client):
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


def test_TC125_페이지네이션_경계값(client):
    response = _get(client, "/products?page=9999&limit=20", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    assert body["page"] == 9999
    assert body["items"] == []


def test_TC126_페이지네이션_최솟값_미만(client):
    response = _get(client, "/products?page=0&limit=20", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC127_한_페이지_내_상품_조회(client):
    response = _get(client, "/products?limit=5", auth_header(client))
    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 5
    assert len(body["items"]) <= 5


def test_TC128_한_페이지_내_상품_최댓값_초과(client):
    response = _get(client, "/products?limit=101", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC129_한_페이지_내_상품_최솟값_미만(client):
    response = _get(client, "/products?limit=0", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC130_로그인_없이_조회(client):
    response = timed(client.get, "/products")
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC131_유효하지_않은_토큰으로_조회(client):
    response = _get(client, "/products", {"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC132_로그아웃된_토큰으로_조회(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = _get(client, "/products", headers)
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC133_존재하는_상품_조회(client):
    headers = auth_header(client)
    first = _get(client, "/products?limit=1", headers).json()["items"][0]
    response = _get(client, f"/products/{first['id']}", headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == first["id"]
    for field in PRODUCT_FIELDS:
        assert field in body


def test_TC134_존재하지_않는_상품_조회(client):
    response = _get(client, "/products/99999999", auth_header(client))
    assert response.status_code == 404
    assert_error_detail(response)


def test_TC135_product_id가_숫자가_아닌_경우(client):
    response = _get(client, "/products/abc", auth_header(client))
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC136_로그인_없이_상품_id_조회(client):
    response = timed(client.get, "/products/1")
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC137_유효하지_않은_토큰으로_상품_id_조회(client):
    response = _get(client, "/products/1", {"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC138_로그아웃된_토큰으로_상품_id_조회(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = _get(client, "/products/1", headers)
    assert response.status_code == 401
    assert_error_detail(response)
