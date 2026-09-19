from pathlib import Path

from .helpers import login, register, unique_email

FIXTURES = Path(__file__).resolve().parents[3] / "postman" / "fixtures"


def _upload(client, headers, filename, content_type, override_content_type=None):
    data = (FIXTURES / filename).read_bytes()
    sent_type = override_content_type or content_type
    return client.post(
        "/colors/extract",
        files={"file": (filename, data, sent_type)},
        headers=headers,
    )


def _headers(client):
    email = unique_email()
    register(client, email=email)
    token = login(client, email, "Test1234!").json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_TC94_jpg_업로드(client):
    response = _upload(client, _headers(client), "ex_jpg.jpg", "image/jpeg")
    assert response.status_code == 200


def test_TC95_png_업로드(client):
    response = _upload(client, _headers(client), "ex_png.png", "image/png")
    assert response.status_code == 200


def test_TC96_webp_업로드(client):
    response = _upload(client, _headers(client), "ex_wepb.webp", "image/webp")
    assert response.status_code == 200


def test_TC97_heic_업로드(client):
    response = _upload(client, _headers(client), "ex_heic.heic", "image/heic")
    assert response.status_code == 415


def test_TC98_미지원_형식_업로드(client):
    response = _upload(client, _headers(client), "ex_gif.gif", "image/gif")
    assert response.status_code == 415


def test_TC99_이미지_누락(client):
    response = client.post("/colors/extract", headers=_headers(client))
    assert response.status_code == 422


def test_TC100_빈_파일_업로드(client):
    response = _upload(client, _headers(client), "empty.jpg", "image/jpeg")
    assert response.status_code == 422


def test_TC101_매우_작은_이미지_업로드(client):
    response = _upload(client, _headers(client), "tiny_1x1.jpg", "image/jpeg")
    assert response.status_code == 200


def test_TC102_크기_초과한_이미지_업로드(client):
    response = _upload(client, _headers(client), "oversized.jpg", "image/jpeg")
    assert response.status_code == 413


def test_TC103_손상된_이미지_업로드(client):
    response = _upload(client, _headers(client), "corrupted.jpg", "image/jpeg")
    assert response.status_code == 422


def test_TC104_이미지인_척하는_파일_업로드(client):
    response = _upload(client, _headers(client), "fake_image.jpg", "image/jpeg")
    assert response.status_code == 422


def test_TC105_해상도_초과_이미지_업로드(client):
    response = _upload(client, _headers(client), "huge_resolution.jpg", "image/jpeg")
    assert response.status_code == 422


def test_TC106_해상도_경계값_테스트(client):
    response = _upload(client, _headers(client), "boundary_8000.jpg", "image/jpeg")
    assert response.status_code == 200


def test_TC107_매우_어두운_이미지_업로드(client):
    response = _upload(client, _headers(client), "very_dark.jpg", "image/jpeg")
    assert response.status_code == 200


def test_TC108_매우_밝은_이미지_업로드(client):
    response = _upload(client, _headers(client), "very_bright.jpg", "image/jpeg")
    assert response.status_code == 200


def test_TC109_여러_색상_섞인_이미지_업로드(client):
    response = _upload(client, _headers(client), "multi_color.jpg", "image/jpeg")
    assert response.status_code == 200


def test_TC110_로그인_없이_업로드(client):
    data = (FIXTURES / "ex_jpg.jpg").read_bytes()
    response = client.post("/colors/extract", files={"file": ("ex_jpg.jpg", data, "image/jpeg")})
    assert response.status_code == 403


def test_TC111_유효하지_않은_토큰으로_업로드(client):
    data = (FIXTURES / "ex_png.png").read_bytes()
    response = client.post(
        "/colors/extract",
        files={"file": ("ex_png.png", data, "image/png")},
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert response.status_code == 401


def test_TC112_로그아웃된_토큰으로_업로드(client):
    headers = _headers(client)
    client.post("/auth/logout", headers=headers)
    response = _upload(client, headers, "ex_wepb.webp", "image/webp")
    assert response.status_code == 401


def test_TC113_Content_Type을_실제_파일과_다르게_설정(client):
    response = _upload(client, _headers(client), "ex_png.png", "image/png", override_content_type="image/jpeg")
    assert response.status_code == 200


def test_TC114_같은_이미지_반복_업로드(client):
    headers = _headers(client)
    first = _upload(client, headers, "ex_jpg.jpg", "image/jpeg")
    second = _upload(client, headers, "ex_jpg.jpg", "image/jpeg")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["extracted_color"] == second.json()["extracted_color"]
