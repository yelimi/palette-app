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
