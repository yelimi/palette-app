from .helpers import assert_error_detail, login, register, timed, unique_email


def _token(client, email, password="Test1234!"):
    register(client, email=email, password=password)
    return login(client, email, password).json()["access_token"]


def test_TC56_정상_로그아웃(client):
    token = _token(client, unique_email())
    response = timed(client.post, "/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "message" in response.json()


def test_TC57_로그아웃_상태에서_로그아웃(client):
    token = _token(client, unique_email())
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/auth/logout", headers=headers)
    response = timed(client.post, "/auth/logout", headers=headers)
    assert response.status_code == 401
    assert_error_detail(response)


def test_TC58_토큰_없이_로그아웃(client):
    response = timed(client.post, "/auth/logout")
    assert response.status_code == 403
    assert_error_detail(response)


def test_TC59_유효하지_않은_토큰으로_로그아웃(client):
    response = timed(client.post, "/auth/logout", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
    assert_error_detail(response)
