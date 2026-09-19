from .helpers import auth_header, login, register, unique_email


def test_TC115_전체_필터_동작(client):
    response = client.get("/products", headers=auth_header(client))
    assert response.status_code == 200


def test_TC116_공용_필터_동작(client):
    response = client.get("/products?gender=공용", headers=auth_header(client))
    assert response.status_code == 200
    assert all(p["gender"] == "공용" for p in response.json()["items"])


def test_TC117_남성_필터_동작(client):
    response = client.get("/products?gender=남성&limit=100", headers=auth_header(client))
    assert response.status_code == 200
    assert all(p["gender"] == "남성" for p in response.json()["items"])


def test_TC118_여성_필터_동작(client):
    response = client.get("/products?gender=여성&limit=50", headers=auth_header(client))
    assert response.status_code == 200
    assert all(p["gender"] == "여성" for p in response.json()["items"])


def test_TC119_카테고리_필터_동작(client):
    response = client.get("/products?category=상의&limit=100", headers=auth_header(client))
    assert response.status_code == 200
    assert all(p["category"] == "상의" for p in response.json()["items"])


def test_TC120_서브_카테고리_필터_동작(client):
    response = client.get("/products?subcategory=셔츠/블라우스&limit=80", headers=auth_header(client))
    assert response.status_code == 200
    assert all(p["subcategory"] == "셔츠/블라우스" for p in response.json()["items"])


def test_TC121_컬러_필터_동작(client):
    response = client.get("/products?color=1B2B4B&limit=40", headers=auth_header(client))
    assert response.status_code == 200


def test_TC122_존재하지_않는_필터값(client):
    response = client.get("/products?gender=아동", headers=auth_header(client))
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_TC123_필터_조합_동작(client):
    headers = auth_header(client)
    response = client.get("/products?gender=여성&category=바지", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(p["gender"] == "여성" and p["category"] == "바지" for p in items)


def test_TC124_페이지네이션(client):
    headers = auth_header(client)
    page1 = client.get("/products?page=1&limit=20", headers=headers)
    page2 = client.get("/products?page=2&limit=20", headers=headers)
    assert page1.status_code == 200
    assert page2.status_code == 200
    ids1 = {p["id"] for p in page1.json()["items"]}
    ids2 = {p["id"] for p in page2.json()["items"]}
    assert ids1.isdisjoint(ids2)


def test_TC125_페이지네이션_경계값(client):
    response = client.get("/products?page=9999&limit=20", headers=auth_header(client))
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_TC126_페이지네이션_최솟값_미만(client):
    response = client.get("/products?page=0&limit=20", headers=auth_header(client))
    assert response.status_code == 422


def test_TC127_한_페이지_내_상품_조회(client):
    response = client.get("/products?limit=5", headers=auth_header(client))
    assert response.status_code == 200
    assert len(response.json()["items"]) <= 5


def test_TC128_한_페이지_내_상품_최댓값_초과(client):
    response = client.get("/products?limit=101", headers=auth_header(client))
    assert response.status_code == 422


def test_TC129_한_페이지_내_상품_최솟값_미만(client):
    response = client.get("/products?limit=0", headers=auth_header(client))
    assert response.status_code == 422


def test_TC130_로그인_없이_조회(client):
    response = client.get("/products")
    assert response.status_code == 403


def test_TC131_유효하지_않은_토큰으로_조회(client):
    response = client.get("/products", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401


def test_TC132_로그아웃된_토큰으로_조회(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = client.get("/products", headers=headers)
    assert response.status_code == 401


def test_TC133_존재하는_상품_조회(client):
    headers = auth_header(client)
    first = client.get("/products?limit=1", headers=headers).json()["items"][0]
    response = client.get(f"/products/{first['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == first["id"]


def test_TC134_존재하지_않는_상품_조회(client):
    response = client.get("/products/99999999", headers=auth_header(client))
    assert response.status_code == 404


def test_TC135_product_id가_숫자가_아닌_경우(client):
    response = client.get("/products/abc", headers=auth_header(client))
    assert response.status_code == 422


def test_TC136_로그인_없이_상품_id_조회(client):
    response = client.get("/products/1")
    assert response.status_code == 403


def test_TC137_유효하지_않은_토큰으로_상품_id_조회(client):
    response = client.get("/products/1", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401


def test_TC138_로그아웃된_토큰으로_상품_id_조회(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = client.get("/products/1", headers=headers)
    assert response.status_code == 401
