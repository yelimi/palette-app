from .helpers import assert_error_detail, login, register, timed, unique_email

BASE_PASSWORD = "Test1234!"


def _headers(client, email=None, password=BASE_PASSWORD):
    email = email or unique_email()
    register(client, email=email, password=password)
    token = login(client, email, password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _change(client, headers, body, threshold_ms=500):
    return timed(client.patch, "/auth/password", json=body, headers=headers, threshold_ms=threshold_ms)


def test_TC60_잘못된_현재_패스워드(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": "wrongpassword123", "new_password": "newpassword123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC61_현재_패스워드_누락(client):
    headers = _headers(client)
    response = _change(client, headers, {"new_password": "newpassword123"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC62_새_패스워드_누락(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC63_현재_패스워드_공백(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": "", "new_password": "newpassword123"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC64_새_패스워드_공백(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": ""})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC65_새_패스워드_정상_입력(client):
    headers = _headers(client)
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": "kimkim33@"}, threshold_ms=1200
    )
    assert response.status_code == 200


def test_TC66_패스워드_동일_입력(client):
    headers = _headers(client)
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": BASE_PASSWORD}, threshold_ms=1000
    )
    assert response.status_code == 400
    assert_error_detail(response)


def test_TC67_8자리_미만의_새_패스워드(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": "kim33"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC68_최대_길이의_새_패스워드(client):
    headers = _headers(client)
    max_password = "A" + "a" * 252 + "1!"
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": max_password}, threshold_ms=1200
    )
    assert response.status_code == 200


def test_TC69_새_패스워드_최대_길이_초과(client):
    headers = _headers(client)
    over_password = "A" + "a" * 253 + "1!"
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": over_password})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC70_빈_문자열의_현재_패스워드(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": " ", "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC71_빈_문자열의_새_패스워드(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": " "})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC72_로그인_없이_변경_시도(client):
    response = timed(
        client.patch, "/auth/password",
        json={"current_password": BASE_PASSWORD, "new_password": "kimkim33@"},
    )
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC73_앞뒤_빈_문자열의_새_패스워드(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": " kimkim33@ "})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC74_중간_빈_문자열의_새_패스워드(client):
    headers = _headers(client)
    response = _change(
        client, headers, {"current_password": BASE_PASSWORD, "new_password": "kim kim33@"}, threshold_ms=1200
    )
    assert response.status_code == 200


def test_TC75_앞뒤_빈_문자열_현재_패스워드(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": f" {BASE_PASSWORD} ", "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC76_중간_빈_문자열의_현재_패스워드(client):
    headers = _headers(client)
    response = _change(client, headers, {"current_password": "Test 1234!", "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC77_유효하지_않은_토큰으로_변경_시도(client):
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = _change(client, headers, {"current_password": BASE_PASSWORD, "new_password": "kimkim33@"})
    assert response.status_code == 401
    assert_error_detail(response)
