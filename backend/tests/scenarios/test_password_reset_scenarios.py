from .helpers import login, register, unique_email

BASE_PASSWORD = "Test1234!"
WRONG_PASSWORD = "Wrong1234!"


def _locked_email(client, fail_count=3):
    email = unique_email()
    register(client, email=email, password=BASE_PASSWORD)
    for _ in range(fail_count):
        login(client, email, WRONG_PASSWORD)
    return email


def _reset(client, body):
    return client.post("/auth/password/reset", json=body)


def test_TC78_새_패스워드_누락(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email})
    assert response.status_code == 422


def test_TC79_이메일_누락(client):
    _locked_email(client)
    response = _reset(client, {"new_password": "newpasswd12@"})
    assert response.status_code == 422


def test_TC80_새_패스워드_공백(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": ""})
    assert response.status_code == 422


def test_TC81_이메일_공백(client):
    _locked_email(client)
    response = _reset(client, {"email": "", "new_password": "newpasswd12@"})
    assert response.status_code == 422


def test_TC82_8자리_미만의_새_패스워드(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": "test12@"})
    assert response.status_code == 422


def test_TC83_최대_길이의_새_패스워드(client):
    email = _locked_email(client)
    max_password = "A" + "a" * 252 + "1!"
    response = _reset(client, {"email": email, "new_password": max_password})
    assert response.status_code == 200


def test_TC84_새_패스워드_최대_길이_초과(client):
    email = _locked_email(client)
    over_password = "A" + "a" * 253 + "1!"
    response = _reset(client, {"email": email, "new_password": over_password})
    assert response.status_code == 422


def test_TC85_빈_문자열의_새_패스워드(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": " "})
    assert response.status_code == 422


def test_TC86_앞뒤_빈_문자열의_새_패스워드(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": " newpasswd12@ "})
    assert response.status_code == 422


def test_TC87_중간_빈_문자열의_새_패스워드(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": "new passwd12@"})
    assert response.status_code == 200


def test_TC88_정상_패스워드_재설정(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email, "new_password": "passwd1@"})
    assert response.status_code == 200
    assert login(client, email, "passwd1@").status_code == 200


def test_TC89_3회_미만_실패_후_재설정_시도(client):
    email = _locked_email(client, fail_count=2)
    response = _reset(client, {"email": email, "new_password": "newpasswd12@"})
    assert response.status_code == 403


def test_TC90_대문자_이메일_입력(client):
    email = _locked_email(client)
    response = _reset(client, {"email": email.upper(), "new_password": "newpasswd12@"})
    assert response.status_code == 200


def test_TC91_존재하지_않는_이메일로_재설정_시도(client):
    response = _reset(client, {"email": unique_email(), "new_password": "newpasswd12@"})
    assert response.status_code == 404


def test_TC92_이메일_골뱅이_누락(client):
    email = _locked_email(client)
    wrong_email = email.replace("@", "")
    response = _reset(client, {"email": wrong_email, "new_password": "newpasswd12@"})
    assert response.status_code == 422


def test_TC93_이메일_도메인_누락(client):
    email = _locked_email(client)
    wrong_email = email.split("@")[0] + "@"
    response = _reset(client, {"email": wrong_email, "new_password": "newpasswd12@"})
    assert response.status_code == 422
