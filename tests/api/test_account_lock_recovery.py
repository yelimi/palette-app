from .helpers import login, register, unique_email


def test_account_lock_recovery(client):
    """3회 로그인 실패 후 계정 잠김 -> 비밀번호 재설정 -> 로그인"""
    email = unique_email()
    correct_password = "Test1234!"
    wrong_password = "wrong1234!"
    new_password = "recover1234!"

    register_res = register(client, name="홍길", email=email, password=correct_password)
    assert register_res.status_code == 201

    for _ in range(2):
        attempt_res = login(client, email, wrong_password)
        assert attempt_res.status_code == 401

    # 3번째 실패에서 failed_attempts가 임계치(3)에 도달해 이 응답 자체가 423으로 잠김
    third_attempt_res = login(client, email, wrong_password)
    assert third_attempt_res.status_code == 423

    reset_res = client.post(
        "/auth/password/reset",
        json={"email": email, "new_password": new_password},
    )
    assert reset_res.status_code == 200

    login_after_reset_res = login(client, email, new_password)
    assert login_after_reset_res.status_code == 200
    assert "access_token" in login_after_reset_res.json()
