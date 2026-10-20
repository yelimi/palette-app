from .helpers import assert_error_detail, login, register, timed, unique_email

BASE_PASSWORD = "Test1234!"
WRONG_PASSWORD = "Wrong1234!"


def _locked_email(client, fail_count=3):
    email = unique_email()
    register(client, email=email, password=BASE_PASSWORD)
    for _ in range(fail_count):
        login(client, email, WRONG_PASSWORD)
    return email


def _reset(client, body):
    return timed(client.post, "/auth/password/reset", json=body)


def test_TC78_new_password_missing(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC79_email_missing(client):
    _locked_email(client)
    response = _reset(client, {"new_password": "newpasswd12@"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC80_new_password_blank(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": ""})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC81_email_blank(client):
    _locked_email(client)
    response = _reset(client, {"email": "", "new_password": "newpasswd12@"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC82_new_password_under_min_length(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": "test12@"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC83_new_password_max_length(client):
    email = _locked_email(client)
    max_password = "A" + "a" * 252 + "1!"
    response = _reset(client, {"email": email, "new_password": max_password})
    assert response.status_code == 200


def test_TC84_new_password_exceeds_max_length(client):
    email = _locked_email(client)
    over_password = "A" + "a" * 253 + "1!"
    response = _reset(client, {"email": email, "new_password": over_password})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC85_new_password_empty_string(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": " "})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC86_new_password_leading_trailing_whitespace(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": " newpasswd12@ "})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC87_new_password_internal_whitespace(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": "new passwd12@"})
    assert response.status_code == 200


def test_TC88_password_reset_success(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": "passwd1@"})
    assert response.status_code == 200
    assert login(client, email, "passwd1@").status_code == 200


def test_TC89_password_reset_before_lockout(client):
    email = _locked_email(client, fail_count=2)
    response = _reset(client, {"email": email, "new_password": "newpasswd12@"})
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC90_email_uppercase(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email.upper(), "new_password": "newpasswd12@"})
    assert response.status_code == 200


def test_TC91_email_not_registered(client):
    response = _reset(client, {"email": unique_email(), "new_password": "newpasswd12@"})
    assert response.status_code == 404
    assert_error_detail(response)


def test_TC92_email_missing_at_symbol(client):
    email = _locked_email(client)
    wrong_email = email.replace("@", "")
    response = _reset(client, {"email": wrong_email, "new_password": "newpasswd12@"})
    assert response.status_code == 422
    assert_error_detail(response)


def test_TC93_email_missing_domain(client):
    email = _locked_email(client)
    wrong_email = email.split("@")[0] + "@"
    response = _reset(client, {"email": wrong_email, "new_password": "newpasswd12@"})
    assert response.status_code == 422
    assert_error_detail(response)
