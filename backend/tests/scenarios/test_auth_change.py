from .helpers import login, register, unique_email


def test_auth_change(client):
    """로그인 -> 비밀번호 변경 -> 재로그인"""
    email = unique_email()
    initial_password = "Test1234!"
    new_password = "newPass1234!"

    register_res = register(client, name="장이사", email=email, password=initial_password)
    assert register_res.status_code == 201

    first_login_res = login(client, email, initial_password)
    assert first_login_res.status_code == 200
    first_login_body = first_login_res.json()
    assert "access_token" in first_login_body
    headers = {"Authorization": f"Bearer {first_login_body['access_token']}"}

    change_res = client.patch(
        "/auth/password",
        json={"current_password": initial_password, "new_password": new_password},
        headers=headers,
    )
    assert change_res.status_code == 200

    relogin_res = login(client, email, new_password)
    assert relogin_res.status_code == 200
    assert "access_token" in relogin_res.json()
