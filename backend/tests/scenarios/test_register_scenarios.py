import uuid

from .helpers import OMIT, assert_error_detail, build_payload, timed, unique_email

BASE_PAYLOAD = {"name": "홍길동", "email": None, "password": "Test1234!"}


def _payload(**overrides):
    base = dict(BASE_PAYLOAD)
    base["email"] = unique_email()
    return build_payload(base, **overrides)


def _max_length_local_part(total_len=64):
    suffix = uuid.uuid4().hex[:12]
    return "a" * (total_len - len(suffix)) + suffix


def _assert_success(response):
    assert response.status_code == 201


def _assert_error(response, status):
    assert response.status_code == status
    assert_error_detail(response)


def test_TC1_register_success(client):
    payload = _payload()
    response = timed(client.post, "/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    for field in ("id", "name", "email"):
        assert field in body
    assert "password" not in body
    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]


def test_TC2_name_missing(client):
    response = timed(client.post, "/auth/register", json=_payload(name=OMIT))
    _assert_error(response, 422)


def test_TC3_email_missing(client):
    response = timed(client.post, "/auth/register", json=_payload(email=OMIT))
    _assert_error(response, 422)


def test_TC4_password_missing(client):
    response = timed(client.post, "/auth/register", json=_payload(password=OMIT))
    _assert_error(response, 422)


def test_TC5_all_fields_missing(client):
    response = timed(client.post, "/auth/register", json=_payload(name=OMIT, email=OMIT, password=OMIT))
    _assert_error(response, 422)


def test_TC6_name_blank(client):
    response = timed(client.post, "/auth/register", json=_payload(name=""))
    _assert_error(response, 422)


def test_TC7_email_blank(client):
    response = timed(client.post, "/auth/register", json=_payload(email=""))
    _assert_error(response, 422)


def test_TC8_password_blank(client):
    response = timed(client.post, "/auth/register", json=_payload(password=""))
    _assert_error(response, 422)


def test_TC9_all_fields_blank(client):
    response = timed(client.post, "/auth/register", json=_payload(name="", email="", password=""))
    _assert_error(response, 422)


def test_TC10_name_special_characters(client):
    response = timed(client.post, "/auth/register", json=_payload(name="홍길_동"))
    _assert_error(response, 422)


def test_TC11_email_missing_at_symbol(client):
    email = f"{unique_email().split('@')[0]}gmail.com"
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_error(response, 422)


def test_TC12_email_missing_domain(client):
    email = f"{unique_email().split('@')[0]}@"
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_error(response, 422)


def test_TC13_email_korean(client):
    email = f"길동{unique_email()}"
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_error(response, 422)


def test_TC14_email_valid_special_characters(client):
    email = f"yo_ung{unique_email()}"
    response = timed(
        client.post, "/auth/register",
        json=_payload(name="김영수", email=email, password="youngsu123@"),
    )
    _assert_success(response)


def test_TC15_email_invalid_special_characters(client):
    email = f"abc:{unique_email().split('@')[0]}@@gmail.com"
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_error(response, 422)


def test_TC16_email_duplicate(client):
    email = unique_email()
    first = timed(client.post, "/auth/register", json=_payload(email=email))
    assert first.status_code == 201

    second = timed(client.post, "/auth/register", json=_payload(email=email, name="다른유저"))
    _assert_error(second, 409)


def test_TC17_password_under_min_length(client):
    response = timed(client.post, "/auth/register", json=_payload(password="hong!"))
    _assert_error(response, 422)


def test_TC18_name_max_length(client):
    response = timed(client.post, "/auth/register", json=_payload(name="가" * 100))
    _assert_success(response)


def test_TC19_name_exceeds_max_length(client):
    response = timed(client.post, "/auth/register", json=_payload(name="가" * 101))
    _assert_error(response, 422)


def test_TC20_password_max_length(client):
    response = timed(client.post, "/auth/register", json=_payload(password="A" + "a" * 252 + "1!"))
    _assert_success(response)


def test_TC21_password_exceeds_max_length(client):
    response = timed(client.post, "/auth/register", json=_payload(password="A" + "a" * 253 + "1!"))
    _assert_error(response, 422)


def test_TC22_email_max_length(client):
    email = f"{_max_length_local_part(64)}@example.com"
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_success(response)


def test_TC23_email_exceeds_max_length(client):
    email = "a" * 65 + "@example.com"
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_error(response, 422)


def test_TC24_name_duplicate(client):
    first = timed(client.post, "/auth/register", json=_payload(name="홍동아"))
    assert first.status_code == 201

    second = timed(client.post, "/auth/register", json=_payload(name="홍동아"))
    assert second.status_code == 201


def test_TC25_name_leading_trailing_whitespace(client):
    response = timed(client.post, "/auth/register", json=_payload(name=" 김상철 "))
    _assert_success(response)


def test_TC26_name_internal_whitespace(client):
    response = timed(client.post, "/auth/register", json=_payload(name="이수 지"))
    _assert_success(response)


def test_TC27_email_leading_trailing_whitespace(client):
    email = f" {unique_email()} "
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_success(response)


def test_TC28_email_internal_whitespace(client):
    email = f"kim11 {unique_email()}"
    response = timed(client.post, "/auth/register", json=_payload(email=email))
    _assert_error(response, 422)


def test_TC29_password_leading_trailing_whitespace(client):
    response = timed(client.post, "/auth/register", json=_payload(password=" kim123123@ "))
    _assert_error(response, 422)


def test_TC30_password_internal_whitespace(client):
    response = timed(client.post, "/auth/register", json=_payload(password="kim123 123 @"))
    _assert_success(response)


def test_TC31_email_case_insensitive(client):
    email = unique_email()
    first = timed(client.post, "/auth/register", json=_payload(email=email))
    assert first.status_code == 201

    second = timed(client.post, "/auth/register", json=_payload(email=email.upper(), name="다른유저"))
    _assert_error(second, 409)


def test_TC32_name_numeric(client):
    response = timed(client.post, "/auth/register", json=_payload(name="홍1동"))
    _assert_error(response, 422)


def test_TC33_name_latin(client):
    response = timed(client.post, "/auth/register", json=_payload(name="janggildong"))
    _assert_success(response)
