import io
import pytest
from PIL import Image


def make_image_bytes(color=(200, 100, 50), size=(100, 100), fmt="JPEG"):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "name": "이미지테스트유저", "email": "imgtest@example.com", "password": "pass1234"
    })
    res = client.post("/auth/login", json={"email": "imgtest@example.com", "password": "pass1234"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_extract_requires_auth(client):
    data = make_image_bytes()
    response = client.post("/colors/extract", files={"file": ("test.jpg", data, "image/jpeg")})
    assert response.status_code == 403


def test_extract_jpeg_success(client, auth_headers):
    data = make_image_bytes(color=(200, 100, 50))
    response = client.post(
        "/colors/extract",
        files={"file": ("test.jpg", data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert "extracted_color" in body
    assert "recommendations" in body
    assert body["extracted_color"].startswith("#")
    assert len(body["recommendations"]) == 5


def test_extract_png_success(client, auth_headers):
    data = make_image_bytes(color=(50, 150, 200), fmt="PNG")
    response = client.post(
        "/colors/extract",
        files={"file": ("test.png", data, "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_extract_unsupported_format(client, auth_headers):
    response = client.post(
        "/colors/extract",
        files={"file": ("test.gif", b"GIF89a", "image/gif")},
        headers=auth_headers,
    )
    assert response.status_code == 415


def test_extract_file_missing(client, auth_headers):
    response = client.post("/colors/extract", headers=auth_headers)
    assert response.status_code == 422


def test_extract_size_exceeded(client, auth_headers):
    # 10MB 초과 데이터
    big_data = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/colors/extract",
        files={"file": ("big.jpg", big_data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 413


def test_extract_dark_image(client, auth_headers):
    # 매우 어두운 이미지 (검정에 가까운 색)
    data = make_image_bytes(color=(10, 10, 10))
    response = client.post(
        "/colors/extract",
        files={"file": ("dark.jpg", data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["extracted_color"].startswith("#")


def test_extract_bright_image(client, auth_headers):
    # 매우 밝은 이미지 (흰색에 가까운 색)
    data = make_image_bytes(color=(250, 250, 250))
    response = client.post(
        "/colors/extract",
        files={"file": ("bright.jpg", data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_extract_recommendation_count(client, auth_headers):
    data = make_image_bytes(color=(100, 150, 200))
    response = client.post(
        "/colors/extract",
        files={"file": ("test.jpg", data, "image/jpeg")},
        headers=auth_headers,
    )
    assert len(response.json()["recommendations"]) == 5


def test_extract_recommendation_fields(client, auth_headers):
    data = make_image_bytes(color=(100, 150, 200))
    response = client.post(
        "/colors/extract",
        files={"file": ("test.jpg", data, "image/jpeg")},
        headers=auth_headers,
    )
    rec = response.json()["recommendations"][0]
    assert "color_name" in rec
    assert "hex" in rec
    assert rec["hex"].startswith("#")


def test_extract_empty_file(client, auth_headers):
    response = client.post(
        "/colors/extract",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert "비어" in response.json()["detail"]


def test_extract_invalid_image_data(client, auth_headers):
    response = client.post(
        "/colors/extract",
        files={"file": ("fake.jpg", b"this is not a real image", "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert "유효하지 않은" in response.json()["detail"]


def test_extract_dimension_exceeded(client, auth_headers):
    # 압축은 잘 되지만(용량 작음) 해상도가 매우 큰 이미지 -> 디컴프레션 밤 방어 확인
    data = make_image_bytes(color=(100, 100, 100), size=(9000, 9000))
    response = client.post(
        "/colors/extract",
        files={"file": ("huge.jpg", data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert "해상도" in response.json()["detail"]


def test_extract_truncated_image(client, auth_headers):
    # 헤더는 정상이지만 데이터가 중간에 잘린 진짜 이미지 -> 500이 아니라 422여야 함
    full_data = make_image_bytes(color=(100, 150, 200), size=(200, 200))
    truncated_data = full_data[: len(full_data) // 2]
    response = client.post(
        "/colors/extract",
        files={"file": ("truncated.jpg", truncated_data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert "손상" in response.json()["detail"]
