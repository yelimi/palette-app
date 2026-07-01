def test_register_success(client):
    response = client.post("/auth/register", json={
        "name": "테스트유저",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data


def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "name": "유저1", "email": "dup@example.com", "password": "pass123"
    })
    response = client.post("/auth/register", json={
        "name": "유저2", "email": "dup@example.com", "password": "pass456"
    })
    assert response.status_code == 409


def test_login_success(client):
    client.post("/auth/register", json={
        "name": "로그인유저", "email": "login@example.com", "password": "mypass123"
    })
    response = client.post("/auth/login", json={
        "email": "login@example.com", "password": "mypass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "name": "유저", "email": "wrongpw@example.com", "password": "correct"
    })
    response = client.post("/auth/login", json={
        "email": "wrongpw@example.com", "password": "wrong"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "email": "nobody@example.com", "password": "pass"
    })
    assert response.status_code == 401


def test_logout_success(client):
    client.post("/auth/register", json={
        "name": "로그아웃유저", "email": "logout@example.com", "password": "pass123"
    })
    token = client.post("/auth/login", json={
        "email": "logout@example.com", "password": "pass123"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200


def test_logout_requires_auth(client):
    response = client.post("/auth/logout")
    assert response.status_code == 403


def test_token_invalid_after_logout(client):
    client.post("/auth/register", json={
        "name": "만료유저", "email": "expired@example.com", "password": "pass123"
    })
    token = client.post("/auth/login", json={
        "email": "expired@example.com", "password": "pass123"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/auth/logout", headers=headers)

    # 로그아웃 후 같은 토큰으로 요청 → 401
    response = client.get("/products", headers=headers)
    assert response.status_code == 401


# ── 비밀번호 변경 ──────────────────────────────────────────

def test_change_password_success(client):
    client.post("/auth/register", json={
        "name": "변경유저", "email": "change@example.com", "password": "oldpass123"
    })
    token = client.post("/auth/login", json={
        "email": "change@example.com", "password": "oldpass123"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch("/auth/password", json={
        "current_password": "oldpass123", "new_password": "newpass123"
    }, headers=headers)
    assert response.status_code == 200


def test_change_password_wrong_current(client):
    client.post("/auth/register", json={
        "name": "변경유저2", "email": "change2@example.com", "password": "correct123"
    })
    token = client.post("/auth/login", json={
        "email": "change2@example.com", "password": "correct123"
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch("/auth/password", json={
        "current_password": "wrongpass", "new_password": "newpass123"
    }, headers=headers)
    assert response.status_code == 401


def test_change_password_requires_auth(client):
    response = client.patch("/auth/password", json={
        "current_password": "old", "new_password": "new"
    })
    assert response.status_code == 403


def test_login_with_new_password_after_change(client):
    client.post("/auth/register", json={
        "name": "변경확인유저", "email": "verify@example.com", "password": "oldpass123"
    })
    token = client.post("/auth/login", json={
        "email": "verify@example.com", "password": "oldpass123"
    }).json()["access_token"]
    client.patch("/auth/password", json={
        "current_password": "oldpass123", "new_password": "newpass123"
    }, headers={"Authorization": f"Bearer {token}"})

    response = client.post("/auth/login", json={
        "email": "verify@example.com", "password": "newpass123"
    })
    assert response.status_code == 200


# ── 비밀번호 재설정 (3회 잠금 후) ─────────────────────────

def test_account_locked_after_3_failures(client):
    client.post("/auth/register", json={
        "name": "잠금유저", "email": "lock@example.com", "password": "correct123"
    })
    for _ in range(3):
        client.post("/auth/login", json={
            "email": "lock@example.com", "password": "wrongpass"
        })
    response = client.post("/auth/login", json={
        "email": "lock@example.com", "password": "correct123"
    })
    assert response.status_code == 423


def test_reset_password_after_lockout(client):
    client.post("/auth/register", json={
        "name": "재설정유저", "email": "reset@example.com", "password": "correct123"
    })
    for _ in range(3):
        client.post("/auth/login", json={
            "email": "reset@example.com", "password": "wrongpass"
        })

    response = client.post("/auth/password/reset", json={
        "email": "reset@example.com", "new_password": "newpass123"
    })
    assert response.status_code == 200


def test_login_success_after_reset(client):
    client.post("/auth/register", json={
        "name": "재설정후로그인", "email": "resetlogin@example.com", "password": "correct123"
    })
    for _ in range(3):
        client.post("/auth/login", json={
            "email": "resetlogin@example.com", "password": "wrongpass"
        })
    client.post("/auth/password/reset", json={
        "email": "resetlogin@example.com", "new_password": "newpass123"
    })

    response = client.post("/auth/login", json={
        "email": "resetlogin@example.com", "password": "newpass123"
    })
    assert response.status_code == 200


def test_reset_password_without_lockout_fails(client):
    client.post("/auth/register", json={
        "name": "정상유저", "email": "normal@example.com", "password": "correct123"
    })
    response = client.post("/auth/password/reset", json={
        "email": "normal@example.com", "new_password": "newpass123"
    })
    assert response.status_code == 403


def test_reset_password_nonexistent_email(client):
    response = client.post("/auth/password/reset", json={
        "email": "ghost@example.com", "new_password": "newpass123"
    })
    assert response.status_code == 404
