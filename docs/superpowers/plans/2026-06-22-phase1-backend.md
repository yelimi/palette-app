# Palette Backend (Phase 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI + PostgreSQL REST API 서버 구축 — 인증(JWT), 상품 조회, 장바구니 CRUD 엔드포인트 제공

**Architecture:** FastAPI 라우터를 기능별(auth/products/cart)로 분리하고, SQLAlchemy ORM으로 PostgreSQL과 연결한다. JWT 토큰으로 인증하며, pytest + httpx로 각 엔드포인트를 TDD로 구현한다.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x, PostgreSQL 15, python-jose (JWT), passlib[bcrypt], pytest, httpx, Docker (PostgreSQL 실행용)

## Global Constraints

- Python 3.11 이상 사용
- 모든 엔드포인트는 JSON 응답
- /products, /cart 엔드포인트는 JWT Bearer 토큰 필수
- 비밀번호는 bcrypt 해시 저장 (평문 저장 금지)
- 색상 파라미터는 `#RRGGBB` 형식 (예: `#26354A`)
- 포트: 8000

---

## 파일 구조

```
palette-app/
└── backend/
    ├── main.py              # FastAPI 앱 생성, CORS, 라우터 등록
    ├── database.py          # SQLAlchemy 엔진, 세션, Base
    ├── models.py            # User, Product, Cart ORM 모델
    ├── schemas.py           # Pydantic 요청/응답 스키마
    ├── auth.py              # JWT 생성/검증, 비밀번호 해시
    ├── color_utils.py       # CIE76 색상 거리 계산
    ├── seed.py              # 샘플 상품 데이터 삽입
    ├── requirements.txt
    ├── routers/
    │   ├── __init__.py
    │   ├── auth.py          # POST /auth/register, POST /auth/login
    │   ├── products.py      # GET /products?color=
    │   └── cart.py          # GET/POST/DELETE /cart, /cart/{id}
    └── tests/
        ├── conftest.py      # pytest fixtures (테스트 DB, 클라이언트)
        ├── test_auth.py     # 회원가입/로그인 테스트
        ├── test_products.py # 상품 조회 테스트
        └── test_cart.py     # 장바구니 CRUD 테스트
```

---

## Task 1: 개발 환경 설정 + DB 연결

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/database.py`
- Create: `backend/main.py`

**Interfaces:**
- Produces: `get_db()` — FastAPI Depends로 사용하는 DB 세션 제너레이터

- [ ] **Step 1: PostgreSQL 실행 (Docker)**

```bash
docker run -d \
  --name palette-db \
  -p 5432:5432 \
  -e POSTGRES_DB=palette \
  -e POSTGRES_USER=palette \
  -e POSTGRES_PASSWORD=palette123 \
  postgres:15
```

확인:
```bash
docker ps | grep palette-db
```
Expected: `palette-db` 컨테이너가 `Up` 상태

- [ ] **Step 2: backend 디렉토리 생성 및 가상환경 설정**

```bash
mkdir -p /Users/jang-yelim/palette-app/backend/routers
mkdir -p /Users/jang-yelim/palette-app/backend/tests
cd /Users/jang-yelim/palette-app/backend
python3 -m venv venv
source venv/bin/activate
```

- [ ] **Step 3: requirements.txt 작성**

`backend/requirements.txt`:
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
pytest==8.3.3
httpx==0.27.2
pytest-asyncio==0.24.0
```

```bash
pip install -r requirements.txt
```

Expected: 패키지 설치 완료, 오류 없음

- [ ] **Step 4: database.py 작성**

`backend/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://palette:palette123@localhost:5432/palette"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: DB 연결 확인 테스트**

```bash
cd /Users/jang-yelim/palette-app/backend
source venv/bin/activate
python3 -c "from database import engine; conn = engine.connect(); print('DB 연결 성공'); conn.close()"
```

Expected: `DB 연결 성공`

- [ ] **Step 6: main.py 작성 (라우터 없이 기본 앱)**

`backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Palette API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 7: 서버 실행 확인**

```bash
cd /Users/jang-yelim/palette-app/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

브라우저 또는 curl로 확인:
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

Swagger UI 확인: http://localhost:8000/docs

- [ ] **Step 8: routers/__init__.py 생성**

```bash
touch /Users/jang-yelim/palette-app/backend/routers/__init__.py
```

- [ ] **Step 9: Commit**

```bash
cd /Users/jang-yelim/palette-app
git add backend/
git commit -m "feat: backend 초기 설정 - FastAPI + PostgreSQL 연결"
```

---

## Task 2: DB 모델 + 스키마 + 시드 데이터

**Files:**
- Create: `backend/models.py`
- Create: `backend/schemas.py`
- Create: `backend/seed.py`

**Interfaces:**
- Produces:
  - `User` — id, name, email, password_hash, created_at
  - `Product` — id, name, category, color_name, hex, price
  - `Cart` — id, user_id, product_id, created_at
  - `UserCreate(name, email, password)` — 회원가입 요청 스키마
  - `UserResponse(id, name, email)` — 회원가입 응답 스키마
  - `LoginRequest(email, password)` — 로그인 요청 스키마
  - `TokenResponse(access_token, token_type)` — JWT 응답 스키마
  - `ProductResponse(id, name, category, color_name, hex, price)` — 상품 응답 스키마
  - `CartItemCreate(product_id)` — 장바구니 추가 요청 스키마
  - `CartItemResponse(id, product_id, product)` — 장바구니 응답 스키마

- [ ] **Step 1: models.py 작성**

`backend/models.py`:
```python
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cart_items: Mapped[list["Cart"]] = relationship("Cart", back_populates="user")

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    color_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hex: Mapped[str] = mapped_column(String(7), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    cart_items: Mapped[list["Cart"]] = relationship("Cart", back_populates="product")

class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
```

- [ ] **Step 2: schemas.py 작성**

`backend/schemas.py`:
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    color_name: str
    hex: str
    price: int
    model_config = {"from_attributes": True}

class CartItemCreate(BaseModel):
    product_id: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product: ProductResponse
    model_config = {"from_attributes": True}
```

- [ ] **Step 3: 테이블 생성 확인**

```bash
cd /Users/jang-yelim/palette-app/backend
source venv/bin/activate
python3 -c "
from database import engine, Base
import models
Base.metadata.create_all(bind=engine)
print('테이블 생성 완료')
"
```

Expected: `테이블 생성 완료`

- [ ] **Step 4: seed.py 작성**

`backend/seed.py`:
```python
from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

PRODUCTS = [
    {"name": "네이비 코튼 셔츠", "category": "상의", "color_name": "네이비", "hex": "#26354A", "price": 49000},
    {"name": "크림 니트 카디건", "category": "아우터", "color_name": "크림", "hex": "#EEE5D3", "price": 69000},
    {"name": "세이지 와이드 팬츠", "category": "하의", "color_name": "세이지", "hex": "#9BAA91", "price": 59000},
    {"name": "버건디 미디 원피스", "category": "원피스", "color_name": "버건디", "hex": "#7B2D3B", "price": 89000},
    {"name": "라이트 블루 블라우스", "category": "상의", "color_name": "라이트 블루", "hex": "#AFCBE3", "price": 52000},
    {"name": "차콜 슬랙스", "category": "하의", "color_name": "차콜", "hex": "#44474D", "price": 64000},
    {"name": "더스티 핑크 셔츠", "category": "상의", "color_name": "더스티 핑크", "hex": "#D6A7AD", "price": 48000},
    {"name": "머스타드 스웨터", "category": "상의", "color_name": "머스타드", "hex": "#C69B2B", "price": 57000},
    {"name": "올리브 트렌치코트", "category": "아우터", "color_name": "올리브", "hex": "#6B7645", "price": 129000},
    {"name": "화이트 린넨 셔츠", "category": "상의", "color_name": "화이트", "hex": "#F5F5F0", "price": 45000},
    {"name": "블랙 스키니진", "category": "하의", "color_name": "블랙", "hex": "#1C1C1C", "price": 79000},
    {"name": "코랄 니트 탑", "category": "상의", "color_name": "코랄", "hex": "#E07060", "price": 42000},
]

def seed():
    db = SessionLocal()
    if db.query(models.Product).count() > 0:
        print("이미 시드 데이터가 있습니다.")
        db.close()
        return
    for p in PRODUCTS:
        db.add(models.Product(**p))
    db.commit()
    db.close()
    print(f"{len(PRODUCTS)}개 상품 데이터 삽입 완료")

if __name__ == "__main__":
    seed()
```

- [ ] **Step 5: 시드 데이터 삽입**

```bash
cd /Users/jang-yelim/palette-app/backend
source venv/bin/activate
python3 seed.py
```

Expected: `12개 상품 데이터 삽입 완료`

- [ ] **Step 6: Commit**

```bash
cd /Users/jang-yelim/palette-app
git add backend/
git commit -m "feat: DB 모델, 스키마, 시드 데이터 추가"
```

---

## Task 3: 인증 유틸리티 + /auth 엔드포인트

**Files:**
- Create: `backend/auth.py`
- Create: `backend/routers/auth.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Modify: `backend/main.py`

**Interfaces:**
- Consumes: `User`, `UserCreate`, `UserResponse`, `LoginRequest`, `TokenResponse`
- Produces:
  - `hash_password(password: str) -> str`
  - `verify_password(plain: str, hashed: str) -> bool`
  - `create_access_token(data: dict) -> str`
  - `get_current_user(token: str, db: Session) -> User`

- [ ] **Step 1: 테스트 작성 (failing)**

`backend/tests/conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

TEST_DB_URL = "postgresql://palette:palette123@localhost:5432/palette_test"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(test_engine):
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def client(test_engine):
    Session = sessionmaker(bind=test_engine)
    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.rollback()
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

테스트 DB 생성:
```bash
docker exec -it palette-db psql -U palette -c "CREATE DATABASE palette_test;"
```

`backend/tests/test_auth.py`:
```python
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
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
cd /Users/jang-yelim/palette-app/backend
source venv/bin/activate
pytest tests/test_auth.py -v
```

Expected: FAILED (라우터 없으므로 404)

- [ ] **Step 3: auth.py 유틸리티 작성**

`backend/auth.py`:
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import models

SECRET_KEY = "palette-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰")
    user = db.get(models.User, int(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없음")
    return user
```

- [ ] **Step 4: routers/auth.py 작성**

`backend/routers/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth as auth_utils

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(body: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
    user = models.User(
        name=body.name,
        email=body.email,
        password_hash=auth_utils.hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not auth_utils.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    token = auth_utils.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
```

- [ ] **Step 5: main.py에 라우터 등록**

`backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth

app = FastAPI(title="Palette API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: 테스트 실행 (통과 확인)**

```bash
pytest tests/test_auth.py -v
```

Expected:
```
PASSED test_register_success
PASSED test_register_duplicate_email
PASSED test_login_success
PASSED test_login_wrong_password
PASSED test_login_nonexistent_user
```

- [ ] **Step 7: Commit**

```bash
cd /Users/jang-yelim/palette-app
git add backend/
git commit -m "feat: 인증 엔드포인트 구현 (회원가입/로그인/JWT)"
```

---

## Task 4: 색상 유틸리티 + /products 엔드포인트

**Files:**
- Create: `backend/color_utils.py`
- Create: `backend/routers/products.py`
- Create: `backend/tests/test_products.py`
- Modify: `backend/main.py`

**Interfaces:**
- Consumes: `Product`, `ProductResponse`, `get_current_user`
- Produces:
  - `color_distance(hex1: str, hex2: str) -> float` — CIE76 색상 거리
  - `GET /products?color=#RRGGBB` — 색상 거리 순 정렬된 상품 목록 반환

- [ ] **Step 1: 테스트 작성 (failing)**

`backend/tests/test_products.py`:
```python
import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "name": "상품테스트유저", "email": "prod@example.com", "password": "pass123"
    })
    res = client.post("/auth/login", json={"email": "prod@example.com", "password": "pass123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_products_requires_auth(client):
    response = client.get("/products?color=%2326354A")
    assert response.status_code == 403

def test_products_returns_list(client, auth_headers):
    response = client.get("/products?color=%2326354A", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_products_sorted_by_color_distance(client, auth_headers):
    response = client.get("/products?color=%2326354A", headers=auth_headers)
    products = response.json()
    assert products[0]["hex"] == "#26354A"

def test_products_no_color_param_returns_all(client, auth_headers):
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_products.py -v
```

Expected: FAILED (라우터 없으므로 404)

- [ ] **Step 3: color_utils.py 작성**

`backend/color_utils.py`:
```python
import math

def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def _rgb_to_lab(r: float, g: float, b: float) -> tuple[float, float, float]:
    def linear(v):
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92
    r, g, b = linear(r), linear(g), linear(b)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722)
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    def f(v):
        return v ** (1/3) if v > 0.008856 else 7.787 * v + 16/116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)

def color_distance(hex1: str, hex2: str) -> float:
    try:
        lab1 = _rgb_to_lab(*_hex_to_rgb(hex1))
        lab2 = _rgb_to_lab(*_hex_to_rgb(hex2))
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))
    except Exception:
        return float("inf")
```

- [ ] **Step 4: routers/products.py 작성**

`backend/routers/products.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from color_utils import color_distance
import models, schemas

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=list[schemas.ProductResponse])
def get_products(
    color: str = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    products = db.query(models.Product).all()
    if color:
        products = sorted(products, key=lambda p: color_distance(color, p.hex))
    return products
```

- [ ] **Step 5: main.py에 라우터 등록**

`backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, products

app = FastAPI(title="Palette API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: 테스트 DB에 시드 데이터 삽입**

```bash
cd /Users/jang-yelim/palette-app/backend
source venv/bin/activate
python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://palette:palette123@localhost:5432/palette_test'
" 
```

conftest.py의 test_engine fixture가 테이블을 생성하지만 시드 데이터는 없으므로 conftest.py에 추가:

`backend/tests/conftest.py` 끝에 추가:
```python
@pytest.fixture(scope="session", autouse=True)
def seed_products(test_engine):
    from sqlalchemy.orm import sessionmaker
    import models
    Session = sessionmaker(bind=test_engine)
    db = Session()
    if db.query(models.Product).count() == 0:
        products = [
            models.Product(name="네이비 코튼 셔츠", category="상의", color_name="네이비", hex="#26354A", price=49000),
            models.Product(name="크림 니트 카디건", category="아우터", color_name="크림", hex="#EEE5D3", price=69000),
            models.Product(name="차콜 슬랙스", category="하의", color_name="차콜", hex="#44474D", price=64000),
        ]
        db.add_all(products)
        db.commit()
    db.close()
```

- [ ] **Step 7: 테스트 실행 (통과 확인)**

```bash
pytest tests/test_products.py -v
```

Expected:
```
PASSED test_products_requires_auth
PASSED test_products_returns_list
PASSED test_products_sorted_by_color_distance
PASSED test_products_no_color_param_returns_all
```

- [ ] **Step 8: Commit**

```bash
cd /Users/jang-yelim/palette-app
git add backend/
git commit -m "feat: 상품 조회 엔드포인트 구현 (색상 거리 정렬)"
```

---

## Task 5: /cart 엔드포인트

**Files:**
- Create: `backend/routers/cart.py`
- Create: `backend/tests/test_cart.py`
- Modify: `backend/main.py`

**Interfaces:**
- Consumes: `Cart`, `CartItemCreate`, `CartItemResponse`, `get_current_user`
- Produces:
  - `GET /cart` — 현재 사용자 장바구니 목록
  - `POST /cart` — 장바구니 추가 (body: `{product_id}`)
  - `DELETE /cart/{id}` — 장바구니 항목 삭제

- [ ] **Step 1: 테스트 작성 (failing)**

`backend/tests/test_cart.py`:
```python
import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "name": "장바구니유저", "email": "cart@example.com", "password": "pass123"
    })
    res = client.post("/auth/login", json={"email": "cart@example.com", "password": "pass123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_cart_requires_auth(client):
    assert client.get("/cart").status_code == 403

def test_cart_initially_empty(client, auth_headers):
    response = client.get("/cart", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_add_to_cart(client, auth_headers):
    response = client.post("/cart", json={"product_id": 1}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == 1
    assert "product" in data

def test_cart_shows_added_item(client, auth_headers):
    client.post("/cart", json={"product_id": 1}, headers=auth_headers)
    response = client.get("/cart", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    assert items[0]["product_id"] == 1

def test_delete_cart_item(client, auth_headers):
    add_res = client.post("/cart", json={"product_id": 1}, headers=auth_headers)
    cart_id = add_res.json()["id"]
    del_res = client.delete(f"/cart/{cart_id}", headers=auth_headers)
    assert del_res.status_code == 204

def test_delete_other_users_cart_returns_404(client):
    client.post("/auth/register", json={"name": "유저A", "email": "a@ex.com", "password": "pass"})
    client.post("/auth/register", json={"name": "유저B", "email": "b@ex.com", "password": "pass"})
    token_a = client.post("/auth/login", json={"email": "a@ex.com", "password": "pass"}).json()["access_token"]
    token_b = client.post("/auth/login", json={"email": "b@ex.com", "password": "pass"}).json()["access_token"]
    add_res = client.post("/cart", json={"product_id": 1}, headers={"Authorization": f"Bearer {token_a}"})
    cart_id = add_res.json()["id"]
    del_res = client.delete(f"/cart/{cart_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_res.status_code == 404
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_cart.py -v
```

Expected: FAILED (라우터 없음)

- [ ] **Step 3: routers/cart.py 작성**

`backend/routers/cart.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("", response_model=list[schemas.CartItemResponse])
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Cart).filter(models.Cart.user_id == current_user.id).all()

@router.post("", response_model=schemas.CartItemResponse, status_code=201)
def add_to_cart(
    body: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = db.get(models.Product, body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    item = models.Cart(user_id=current_user.id, product_id=body.product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{cart_id}", status_code=204)
def delete_cart_item(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.query(models.Cart).filter(
        models.Cart.id == cart_id,
        models.Cart.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")
    db.delete(item)
    db.commit()
```

- [ ] **Step 4: main.py에 라우터 등록**

`backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, products, cart

app = FastAPI(title="Palette API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: 전체 테스트 실행 (통과 확인)**

```bash
cd /Users/jang-yelim/palette-app/backend
source venv/bin/activate
pytest tests/ -v
```

Expected: 전체 테스트 PASSED

- [ ] **Step 6: 서버 실행 후 Swagger UI 확인**

```bash
uvicorn main:app --reload --port 8000
```

브라우저에서 http://localhost:8000/docs 열어 확인:
- `/auth/register`, `/auth/login` 엔드포인트 존재
- `/products`, `/cart` 엔드포인트 존재 (Authorize 버튼으로 JWT 입력 가능)

- [ ] **Step 7: Commit**

```bash
cd /Users/jang-yelim/palette-app
git add backend/
git commit -m "feat: 장바구니 CRUD 엔드포인트 구현"
```

---

## 완료 기준 (Phase 1)

- [ ] `pytest tests/ -v` 전체 통과
- [ ] `uvicorn main:app` 실행 후 http://localhost:8000/docs 에서 모든 엔드포인트 확인 가능
- [ ] Postman으로 수동 확인:
  - POST /auth/register → 201
  - POST /auth/login → 200 + JWT 토큰
  - GET /products?color=%2326354A (Bearer 토큰) → 200 + 정렬된 목록
  - POST /cart (Bearer 토큰) → 201
  - GET /cart (Bearer 토큰) → 200 + 목록
  - DELETE /cart/{id} (Bearer 토큰) → 204

---

## 다음 단계

- **Phase 2:** `2026-06-22-phase2-mobile-app.md` — React Native 앱 (로그인/장바구니/색상추천 화면)
- **Phase 3:** `2026-06-22-phase3-web-app.md` — React 웹 앱
- **Phase 4:** `2026-06-22-phase4-qa-tests.md` — Postman 컬렉션, Appium, Selenium 테스트
