# Phase 2: 모바일 앱 (React Native) 설계 문서

날짜: 2026-08-09

## 1. 개요

Phase 1에서 완성된 FastAPI 백엔드(인증, 상품 조회, 장바구니, 색상 추출/추천 API)를 사용하는
React Native(Expo) 클라이언트 앱을 구현한다. 현재 `App.js`는 `create-expo-app` 기본
보일러플레이트 상태이며, Phase 2에서 실제 화면과 API 연동을 처음 구현한다.

**범위:** 로그인/회원가입, 홈(이미지 업로드 → 색상 추천 → 상품 그리드), 상품 상세,
장바구니. 전체 상품을 훑어보는 별도 목록/필터 화면(`GET /products` 페이징·필터)은
Phase 2 범위에서 제외한다 (색상 추천 흐름에서만 상품에 접근).

**참고 문서:** `docs/superpowers/plans/2026-06-22-phase1-backend.md`,
`docs/superpowers/specs/2026-06-22-palette-qa-design.md`

---

## 2. 기술 스택 & 아키텍처

| 구성 | 선택 | 비고 |
|---|---|---|
| 네비게이션 | Expo Router (`app/` 디렉토리, 파일 기반) | Expo 56 신규 프로젝트 공식 기본값 |
| 인증 상태 관리 | React Context (`AuthContext`) | 이 규모에 Redux 등은 과함 (YAGNI) |
| 토큰 저장 | `expo-secure-store` | 앱 재실행해도 로그인 유지 (자동로그인) |
| API 통신 | fetch 기반 얇은 래퍼 (`api.ts`) | baseURL, Authorization 헤더 자동 첨부, 401 공통 처리 |
| 이미지 소스 | `expo-camera`(촬영) + `expo-image-picker`(갤러리) | 이미 설치되어 있음, 사용자가 버튼으로 선택 |

**신규 설치 패키지 (SDK 56과 버전 정합성 확인됨):**
- `expo-router@56.2.17`
- `expo-secure-store`
- `expo-constants@~56.0.22`, `expo-linking@~56.0.16`
- `react-native-screens@^4.26.0`, `react-native-safe-area-context@>=5.4.0`
- `react-native-gesture-handler`, `react-native-reanimated` (Expo Router 필수 peer)

> 최신 major(57.x)가 아닌, 현재 프로젝트의 Expo SDK 56.0.12와 짝을 이루는
> 56.x 라인을 사용한다. npm 레지스트리 확인 결과 `expo-router@56.2.17`은
> 2026-07-29에 릴리스되어 SDK 57 출시 이후에도 계속 유지보수되고 있음.

---

## 3. 화면/라우트 구조

```
app/
├── _layout.tsx              # 루트 레이아웃: AuthProvider + 인증 상태에 따라 (auth)/(tabs) 리다이렉트
├── (auth)/
│   ├── _layout.tsx           # 비로그인 스택
│   ├── login.tsx
│   └── register.tsx
└── (tabs)/
    ├── _layout.tsx           # 로그인 상태 bottom tabs (홈 / 장바구니)
    ├── index.tsx              # 홈: 이미지 업로드(카메라/갤러리) → 색상추천 → 상품 그리드
    ├── product/[id].tsx       # 상품 상세
    └── cart.tsx                # 장바구니 (목록 + 삭제, 로그아웃 버튼 위치)
```

- 앱 최초 실행 시 `expo-secure-store`에서 토큰 확인 → 있으면 `(tabs)`로, 없으면
  `(auth)/login`으로 리다이렉트
- 로그아웃 버튼은 장바구니 화면 헤더에 배치 → 토큰 삭제 후 `(auth)/login`으로 이동

---

## 4. 데이터 흐름

| 화면 | API 호출 | 비고 |
|---|---|---|
| 로그인 | `POST /auth/login` | 성공 시 토큰 secure-store 저장 → `(tabs)`로 이동 |
| 회원가입 | `POST /auth/register` → 성공 시 `/auth/login` 자동 호출 | 가입 직후 바로 로그인 처리 |
| 홈(색상추천) | 이미지 선택 → `POST /colors/extract` (multipart) | 응답 `recommendations`(색상 5개) 각각에 대해 `GET /products?color=` 호출해 상품 그리드 구성 |
| 상품상세 | `GET /products/{id}` | 장바구니 담기 버튼 → `POST /cart` |
| 장바구니 | `GET /cart` (탭 진입 시) | 삭제는 `DELETE /cart/{id}`, 성공 시 로컬 상태에서 즉시 제거 |

---

## 5. 에러 처리

백엔드 상태코드를 화면 공통 규칙으로 매핑한다:

- **401** (토큰 만료/무효): 전역 fetch 래퍼에서 감지 → 토큰 삭제 후 로그인 화면으로 강제 이동
  (개별 화면에서 따로 처리하지 않음)
- **423** (계정 잠금, 로그인 3회 실패): 로그인 화면에 "비밀번호를 재설정해주세요" 안내 +
  비밀번호 재설정 화면 링크
- **409** (이메일 중복): 회원가입 화면 인라인 에러
- **422** (유효성 검증 실패 — 이름/비밀번호/이미지 등): 서버 `detail` 메시지를 그대로 인라인 표시
- **413 / 415** (이미지 크기초과 / 형식오류): 홈 화면에서 업로드 직후 알럿
- 네트워크 오류(오프라인 등): 공통 알럿 "네트워크 연결을 확인해주세요"

---

## 6. 테스트 범위

Phase 4(QA)에서 Appium/Selenium E2E를 별도로 다루므로, Phase 2에서는:
- 화면별 수동 확인만 진행 (완료 기준에 체크리스트로 명시)
- RN 쪽 자동화 테스트(Jest 등)는 이 phase에서 신규로 구축하지 않음

---

## 7. 완료 기준

- [ ] 로그인 → 홈 탭 진입, 회원가입 → 자동 로그인 → 홈 탭 진입
- [ ] 홈에서 카메라 촬영 / 갤러리 선택 둘 다로 이미지 업로드 → 추천 색상 5개 + 각 색상별 상품 그리드 표시
- [ ] 상품 탭 → 상세 화면 → 장바구니 담기 → 장바구니 탭에서 확인
- [ ] 장바구니 항목 삭제 정상 동작
- [ ] 로그아웃 → 로그인 화면 이동, 앱 재실행 시 로그인 유지(자동로그인) 확인
- [ ] 401/423/409/422/413/415/네트워크 오류 각각 의도한 대로 표시되는지 수동 확인

---

## 8. 다음 단계

- **Phase 3:** 웹 앱 (React)
- **Phase 4:** QA 자동화 테스트 (Postman/Newman, Appium, Selenium)
