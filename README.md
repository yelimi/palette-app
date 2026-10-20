# 🎨 Palette App QA

---

## 테스트 현황

| 테스트 | 도구 | 대상 | 케이스 | 상태 | 위치 |
|--------|------|------|-------:|------|------|
| API 테스트 | Postman, Newman, pytest | FastAPI REST API | 164 | ✅ 완료 | [`tests/postman/`](tests/postman/), [`tests/api/`](tests/api/) |
| 모바일 E2E 테스트 | Appium | React Native 앱 (iOS / Android) | - | 🚧 진행 중 | - |
| 웹 E2E 테스트 | Selenium | 웹 앱 | - | 📋 예정 | - |
| CI 자동화 | Jenkins (Docker) | 위 테스트 자동 실행 | - | 🚧 진행 중 | [`Jenkinsfile`](Jenkinsfile) |

---

## 테스트 대상 앱

사진을 올리면 대표 색상을 뽑아 내고, 그 색과 어울리는 색상의 옷을 추천해 주는 앱입니다.

<!-- TODO: 앱 스크린샷을 docs/images/ 에 넣고 아래 주석을 풀어 주세요. -->
<!--
<p>
  <img src="docs/images/login.png" width="200" />
  <img src="docs/images/home.png" width="200" />
  <img src="docs/images/products.png" width="200" />
  <img src="docs/images/cart.png" width="200" />
</p>
-->

| 기능 | 설명 |
|------|------|
| 회원 인증 | 회원가입, 로그인(JWT), 로그아웃, 비밀번호 변경. 로그인 3회 실패 시 계정 잠금 |
| 색상 추출 / 추천 | 이미지를 올리면 대표 색상을 추출하고, 어울리는 색 5개를 추천 |
| 상품 조회 | 성별/카테고리 필터, 색상 기준 정렬, 페이징 |
| 장바구니 | 상품 담기, 조회, 삭제 |

### 앱 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | Python, FastAPI, SQLAlchemy |
| DB | PostgreSQL |
| Mobile | React Native (Expo) |

---

## 테스트 전략과 범위

API를 먼저 테스트해서 백엔드 동작을 검증하고, 그 위에서 화면 단위 E2E 테스트로 넓혀 가는 순서로 진행합니다.

| 단계 | 테스트 | 목적 |
|------|--------|------|
| 1 | API 테스트 | 입력값 검증, 인증, 권한, 에러 처리가 API 수준에서 맞는지 확인 |
| 2 | 모바일 / 웹 E2E 테스트 | 실제 사용자 화면에서 기능이 끝까지 동작하는지 확인 |
| 3 | CI 자동화 | 코드가 바뀔 때마다 위 테스트를 자동으로 실행 |

### 테스트 범위

| 포함 | 제외 |
|------|------|
| 기능 테스트 (정상, 예외, 경계값) | 성능, 부하 테스트 |
| 인증 / 권한 (토큰 상태, 다른 사용자 데이터 접근) | 보안 침투 테스트 |
| 입력값 검증 (필수값, 형식, 길이, 공백) | 색상 추천 결과가 "예쁜지" 같은 주관적 품질 |
| 파일 업로드 (포맷, 용량, 해상도, 손상된 파일) | UI 디자인, 시각적 비교 |
| 여러 기능을 이어서 쓰는 사용자 플로우 | |

---

## 테스트 도구와 환경

| 구분 | 내용 |
|------|------|
| API 테스트 | Postman (설계, 수동 실행), Newman (CLI 실행), pytest 8.3 (자동화) |
| 모바일 E2E | Appium |
| 웹 E2E | Selenium |
| CI | Jenkins (Docker 컨테이너) |
| 테스트 DB | PostgreSQL 테스트 전용 DB (`palette_test`), mock 없이 실제 DB 사용 |
| 테스트 서버 | 로컬 FastAPI 서버 (`http://127.0.0.1:8000`) |
| OS | macOS |

---

## 테스트 진행 과정

모든 테스트를 같은 흐름으로 진행합니다.

```
요구사항 분석 → 테스트 케이스 설계 → 수동 실행 → 자동화 → CI 연결
```

| 단계 | API 테스트에서 한 일 |
|------|----------------------|
| 요구사항 분석 | API별 입력값, 응답, 에러 규칙 정리 |
| 테스트 케이스 설계 | 정상, 예외, 경계값, 인증 상태 기준으로 케이스 작성 |
| 수동 실행 | Postman으로 요청을 보내고 응답 검증 스크립트 작성 |
| 자동화 | Newman으로 CLI 실행, 이후 pytest 코드로 전환 |
| CI 연결 | Jenkins에서 pytest 자동 실행 (진행 중) |

---

## 테스트 구조

```
            [ Appium ]          [ Selenium ]
                │                    │
                ▼                    ▼
         [ 모바일 앱 ]          [ 웹 앱 ]
                │                    │
                └─────────┬──────────┘
                          ▼
              [ FastAPI (JWT 인증) ] ◀── [ Postman / Newman / pytest ]
                          │
                          ▼
                   [ PostgreSQL ]

        Jenkins: 위 테스트를 GitHub push 때마다 자동 실행
```

---

## 향후 계획

- [x] API 테스트 (Postman, Newman, pytest)
- [ ] 모바일 E2E 테스트 (Appium, iOS / Android)
- [ ] 웹 E2E 테스트 (Selenium)
- [ ] Jenkins CI 연결 (GitHub push 시 테스트 자동 실행)

---

## 디렉토리 구조

```
palette-app/
├── backend/            # 테스트 대상: FastAPI 서버
├── mobile/             # 테스트 대상: Expo 모바일 앱
├── tests/
│   ├── api/            # pytest API 테스트
│   └── postman/        # Postman 컬렉션, 환경 파일, 업로드 테스트용 이미지
├── docs/               # 설계(specs), 구현 계획(plans) 문서
├── pytest.ini          # pytest 설정 (루트에서 실행)
└── Jenkinsfile         # CI 파이프라인
```
