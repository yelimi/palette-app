# Palette QA 프로젝트 설계 문서

날짜: 2026-06-22

## 1. 프로젝트 개요

색상 기반 옷 추천 앱을 QA 테스트 포트폴리오 목적으로 구축한다.
사진을 찍거나 이미지를 로드해 색상을 추출하고, 어울리는 색상을 우선순위화하여 추천한다.
추천 색상을 선택하면 해당 색상의 옷을 DB에서 조회해 보여주고, 장바구니에 담을 수 있다.

### 목표
- Postman + Newman으로 REST API 테스트
- Appium으로 iOS / Android 앱 E2E 테스트
- Selenium으로 웹 앱 E2E 테스트
- QA 이직 포트폴리오로 활용

---

## 2. 전체 아키텍처

```
┌─────────────────────────────────────────────┐
│              QA 테스트 도구                    │
│   Postman/Newman    Appium      Selenium     │
└──────┬──────────────────┬──────────┬─────────┘
       │                  │          │
       ▼                  ▼          ▼
┌─────────────┐   ┌──────────────┐ ┌──────────┐
│  FastAPI    │   │ React Native │ │  React   │
│  REST API   │◀──│ iOS/Android  │ │  웹 앱   │
│  JWT 인증   │◀──│     앱       │ │(브라우저)│
└──────┬──────┘   └──────────────┘ └────┬─────┘
       │                                │
       │◀───────────────────────────────┘
       ▼
┌─────────────┐
│ PostgreSQL  │
│ - users     │
│ - products  │
│ - cart      │
└─────────────┘
```

---

## 3. 기술 스택

| 구성 | 기술 | 이유 |
|------|------|------|
| 모바일 앱 | React Native (Expo) | iOS + Android 크로스플랫폼 |
| 웹 앱 | React | 브라우저 버전 |
| 백엔드 | FastAPI (Python) | REST API, Swagger 자동 생성, JWT 인증 |
| DB | PostgreSQL | 현업 표준, Oracle/Tibero와 SQL 문법 유사 |
| API 테스트 | Postman + Newman | 수동 → CLI 자동화 |
| 모바일 테스트 | Appium | iOS/Android 크로스플랫폼 자동화 |
| 웹 테스트 | Selenium | 브라우저 E2E 자동화 |

---

## 4. 화면 구성

### React Native 앱 (iOS + Android 동일)

```
로그인 화면
  ├── 이메일/비밀번호 입력
  └── 회원가입 화면으로 이동

회원가입 화면
  └── 이름/이메일/비밀번호 입력

홈 화면 (로그인 후)
  ├── 카메라 촬영
  ├── 사진 전체 선택
  └── 크롭 후 선택

색상 추출 결과 화면
  └── 추출된 색상 목록 (비율 표시)

색상 추천 화면
  └── 어울리는 색상 우선순위 목록

옷 추천 목록 화면
  ├── 색상 기반 옷 목록 (이름/카테고리/가격)
  └── 장바구니 담기 버튼

장바구니 화면
  ├── 담긴 옷 목록
  └── 삭제 기능
```

### React 웹 앱 (브라우저)

- 모바일과 동일한 플로우
- 카메라 대신 이미지 파일 업로드

---

## 5. API 엔드포인트 (Postman 테스트 대상)

### 인증
| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /auth/register | 회원가입 |
| POST | /auth/login | 로그인 → JWT 토큰 반환 |

### 상품
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /products?color={hex} | 색상으로 옷 목록 조회 |

### 장바구니
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /cart | 장바구니 조회 |
| POST | /cart | 장바구니 추가 |
| DELETE | /cart/{id} | 장바구니 항목 삭제 |

모든 /cart, /products 엔드포인트는 JWT 토큰 필요 (Authorization: Bearer {token})

---

## 6. DB 스키마 (PostgreSQL)

```sql
-- 사용자
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 상품
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    color_name VARCHAR(100) NOT NULL,
    hex VARCHAR(7) NOT NULL,
    price INTEGER NOT NULL
);

-- 장바구니
CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 7. QA 테스트 범위

### Postman (API 테스트)
- 회원가입 성공/실패 (중복 이메일, 필드 누락)
- 로그인 성공/실패 (잘못된 비밀번호, 없는 계정)
- JWT 토큰 만료/없는 경우 401 응답 검증
- 상품 조회 (색상 파라미터 있음/없음)
- 장바구니 CRUD (추가, 조회, 삭제)
- Newman으로 컬렉션 CLI 자동 실행

### Appium (모바일 E2E)
- iOS / Android 동일 시나리오
- 로그인 플로우
- 이미지 선택 → 색상 추출 → 추천 → 장바구니 담기 전체 플로우
- 장바구니 삭제

### Selenium (웹 E2E)
- 로그인/회원가입
- 이미지 업로드 → 색상 추출 → 추천
- 장바구니 담기/삭제

---

## 8. 구현 순서 (Phase)

| Phase | 내용 |
|-------|------|
| 1 | FastAPI + PostgreSQL 서버 구축 (인증, 상품, 장바구니 API) |
| 2 | React Native 앱 (로그인/회원가입/색상추천/장바구니 화면) |
| 3 | React 웹 앱 (동일 기능, 브라우저) |
| 4 | QA 테스트 작성 (Postman → Appium → Selenium 순) |
