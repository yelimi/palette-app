import uuid

from .helpers import register, timed, unique_email


def _max_length_local_part(total_len=64):
    suffix = uuid.uuid4().hex[:12]
    return "a" * (total_len - len(suffix)) + suffix


def _login(client, email, password):
    return timed(client.post, "/auth/login", json={"email": email, "password": password})


def test_TC34_login_success(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, email, "Test1234!")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_TC35_email_blank(client):
    response = _login(client, "", "Test1234!")
    assert response.status_code == 422


def test_TC36_password_blank(client):
    response = _login(client, "honggildong1@gmail.com", "")
    assert response.status_code == 401


def test_TC37_all_fields_blank(client):
    response = _login(client, "", "")
    assert response.status_code == 422


def test_TC38_email_missing(client):
    response = timed(client.post, "/auth/login", json={"password": "Test1234!"})
    assert response.status_code == 422


def test_TC39_password_missing(client):
    response = timed(client.post, "/auth/login", json={"email": "honggildong1@gmail.com"})
    assert response.status_code == 422


def test_TC40_all_fields_missing(client):
    response = timed(client.post, "/auth/login", json={})
    assert response.status_code == 422


def test_TC41_email_not_registered(client):
    response = _login(client, "aabbc@test.com", "aabb1234@")
    assert response.status_code == 401


def test_TC42_password_incorrect(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, email, "wrong1234!")
    assert response.status_code == 401


def test_TC43_email_missing_at_symbol(client):
    response = _login(client, "honggildong1gmail.com", "Test1234!")
    assert response.status_code == 422


def test_TC44_email_missing_domain(client):
    response = _login(client, "honggildong1@", "Test1234!")
    assert response.status_code == 422


def test_TC45_password_max_length(client):
    email = unique_email()
    max_password = "A" + "a" * 252 + "1!"
    register(client, email=email, password=max_password)
    response = _login(client, email, max_password)
    assert response.status_code == 200


def test_TC46_password_exceeds_max_length(client):
    over_password = "A" + "a" * 253 + "1!"
    response = _login(client, unique_email(), over_password)
    assert response.status_code == 422


def test_TC47_email_max_length(client):
    email = f"{_max_length_local_part(64)}@example.com"
    register(client, email=email, password="Test1234!")
    response = _login(client, email, "Test1234!")
    assert response.status_code == 200


def test_TC48_email_exceeds_max_length(client):
    wrong_email = f"{_max_length_local_part(65)}@example.com"
    response = _login(client, wrong_email, "Test1234!")
    assert response.status_code == 422


def test_TC49_email_leading_trailing_whitespace(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, f" {email} ", "Test1234!")
    assert response.status_code == 200


def test_TC50_email_internal_whitespace(client):
    local = uuid.uuid4().hex[:8]
    wrong_email = f"kim11 {local}@gmail.com"
    response = _login(client, wrong_email, "Test1234!")
    assert response.status_code == 422


def test_TC51_password_leading_trailing_whitespace(client):
    email = unique_email()
    register(client, email=email, password="kim123123@")
    response = _login(client, email, " kim123123@ ")
    assert response.status_code == 401


def test_TC52_password_internal_whitespace(client):
    email = unique_email()
    register(client, email=email, password="kim123 123 @")
    response = _login(client, email, "kim123 123 @")
    assert response.status_code == 200


def test_TC53_email_uppercase(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    response = _login(client, email.upper(), "Test1234!")
    assert response.status_code == 200


def test_TC54_password_case_sensitivity(client):
    email = unique_email()
    register(client, email=email, password="test1234!")
    response = _login(client, email, "TEST1234!")
    assert response.status_code == 401


def test_TC55_account_locked_after_3_failures(client):
    email = unique_email()
    register(client, email=email, password="Test1234!")
    for _ in range(3):
        _login(client, email, "wrong1234!")
    response = _login(client, email, "wrong1234!")
    assert response.status_code == 423
