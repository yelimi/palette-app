from .helpers import assert_error_detail, login, register, timed, unique_email

BASE_PASSWORD = "Test1234!"


def _headers(client, email=None, password=BASE_PASSWORD):
    email = email or unique_email()
    register(client, email=email, password=password)
    token = login(client, email, password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _change(client, headers, body, threshold_ms=500):
    return timed(client.patch, "/auth/password", json=body, headers=headers, threshold_ms=threshold_ms)


def test_TC60_current_password_incorrect(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": "wrongpassword123", "new_password": "newpassword123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC61_current_password_missing(client):
    headers = _headers(client)
    response = _change(client, headers, {"new_password": "newpassword123"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC62_new_password_missing(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC63_current_password_blank(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": "", "new_password": "newpassword123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC64_new_password_blank(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": ""})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC65_password_change_success(client):
    headers = _headers(client)
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": "kimkim33@"}, threshold_ms=1200
    )
    assert response.status_code == 200


def test_TC66_new_password_same_as_current(client):
    headers = _headers(client)
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": BASE_PASSWORD}, threshold_ms=1000
    )
    assert response.status_code == 400
    assert_error_detail(response)


def test_TC67_new_password_under_min_length(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": "kim33"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC68_new_password_max_length(client):
    headers = _headers(client)
    max_password = "A" + "a" * 252 + "1!"
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": max_password}, threshold_ms=1200
    )
    assert response.status_code == 200


def test_TC69_new_password_exceeds_max_length(client):
    headers = _headers(client)
    over_password = "A" + "a" * 253 + "1!"
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": over_password})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC70_current_password_empty_string(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": " ", "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC71_new_password_empty_string(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": " "})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC72_password_change_without_login(client):
    response = timed(
        client.patch, "/auth/password",
        json={"current_password": BASE_PASSWORD, "new_password": "kimkim33@"},
    )
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC73_new_password_leading_trailing_whitespace(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": " kimkim33@ "})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC74_new_password_internal_whitespace(client):
    headers = _headers(client)
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": "kim kim33@"}, threshold_ms=1200
    )
    assert response.status_code == 200


def test_TC75_current_password_leading_trailing_whitespace(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": f" {BASE_PASSWORD} ", "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC76_current_password_internal_whitespace(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": "Test 1234!", "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC77_password_change_invalid_token(client):
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)
