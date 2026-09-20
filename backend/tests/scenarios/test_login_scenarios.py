import uuid

from .helpers import register, timed, unique_email


def _max_length_local_part(total_len=64):
    suffix = uuid.uuid4().hex[:12]
    return "a" * (total_len - len(suffix)) + suffix


def _login(client, email, password):
    return timed(client.post, "/auth/login", json={"email": email, "password": password})


def test_TC34_로그인_정상(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, email, "Test1234!")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_TC35_이메일_공백(client):
    response = _login(client, "", "Test1234!")
    assert response.status_code == 422


def test_TC36_패스워드_공백(client):
    response = _login(client, "honggildong1@gmail.com", "")
    assert response.status_code == 401


def test_TC37_전체_공백(client):
    response = _login(client, "", "")
    assert response.status_code == 422


def test_TC38_이메일_누락(client):
    response = timed(client.post, "/auth/login", json={"password": "Test1234!"})
    assert response.status_code == 422


def test_TC39_패스워드_누락(client):
    response = timed(client.post, "/auth/login", json={"email": "honggildong1@gmail.com"})
    assert response.status_code == 422


def test_TC40_전체_누락(client):
    response = timed(client.post, "/auth/login", json={})
    assert response.status_code == 422


def test_TC41_미가입_이메일(client):
    response = _login(client, "aabbc@test.com", "aabb1234@")
    assert response.status_code == 401


def test_TC42_잘못된_패스워드(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, email, "wrong1234!")
    assert response.status_code == 401


def test_TC43_이메일_골뱅이_누락(client):
    response = _login(client, "honggildong1gmail.com", "Test1234!")
    assert response.status_code == 422


def test_TC44_이메일_도메인_누락(client):
    response = _login(client, "honggildong1@", "Test1234!")
    assert response.status_code == 422


def test_TC45_패스워드_최대길이(client):
    email = unique_email()
    max_password = "A" + "a" * 252 + "1!"
    register(client, email=email, password=max_password)
    response = _login(client, email, max_password)
    assert response.status_code == 200


def test_TC46_패스워드_최대길이_초과(client):
    over_password = "A" + "a" * 253 + "1!"
    response = _login(client, unique_email(), over_password)
    assert response.status_code == 422


def test_TC47_이메일_최대길이(client):
    email = f"{_max_length_local_part(64)}@example.com"
    register(client, email=email, password="Test1234!")
    response = _login(client, email, "Test1234!")
    assert response.status_code == 200


def test_TC48_이메일_최대길이_초과(client):
    wrong_email = f"{_max_length_local_part(65)}@example.com"
    response = _login(client, wrong_email, "Test1234!")
    assert response.status_code == 422


def test_TC49_이메일_앞뒤_공백(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, f" {email} ", "Test1234!")
    assert response.status_code == 200


def test_TC50_이메일_중간_공백(client):
    local = uuid.uuid4().hex[:8]
    wrong_email = f"kim11 {local}@gmail.com"
    response = _login(client, wrong_email, "Test1234!")
    assert response.status_code == 422


def test_TC51_패스워드_앞뒤_공백(client):
    email = unique_email()
    register(client, email=email, password="kim123123@")
    response = _login(client, email, " kim123123@ ")
    assert response.status_code == 401


def test_TC52_패스워드_중간_공백(client):
    email = unique_email()
    register(client, email=email, password="kim123 123 @")
    response = _login(client, email, "kim123 123 @")
    assert response.status_code == 200


def test_TC53_이메일_대소문자_처리(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, email.upper(), "Test1234!")
    assert response.status_code == 200


def test_TC54_패스워드_대소문자_처리(client):
    email = unique_email()
    register(client, email=email, password="test1234!")
    response = _login(client, email, "TEST1234!")
    assert response.status_code == 401


def test_TC55_3회_이상_틀린_패스워드(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    for _ in range(3):
        _login(client, email, "wrong1234!")
    response = _login(client, email, "wrong1234!")
    assert response.status_code == 423
