import uuid

OMIT = object()


def unique_email(prefix="user"):
    return f"{prefix}{uuid.uuid4().hex[:12]}@example.com"


def build_payload(base, **overrides):
    data = dict(base)
    for key, value in overrides.items():
        if value is OMIT:
            data.pop(key, None)
        else:
            data[key] = value
    return data


def register(client, name="테스트유저", email=None, password="Test1234!"):
    email = email or unique_email()
    return client.post("/auth/register", json={
        "name": name, "email": email, "password": password,
    })


def login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth_header(client, email=None, password="Test1234!", name="테스트유저"):
    email = email or unique_email()
    register(client, name=name, email=email, password=password)
    token = login(client, email, password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
