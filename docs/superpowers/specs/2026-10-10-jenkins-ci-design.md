# Jenkins CI (백엔드 pytest 자동화) 설계 문서

날짜: 2026-10-10

## 1. 개요

`feature/phase1-backend` 브랜치에 push가 발생할 때마다, 기존에 로컬 Docker로 띄워둔 Jenkins가
자동으로 백엔드 pytest 테스트 스위트(53개)를 실행하도록 한다.

**범위:** 백엔드(`backend/`) pytest 실행만. 모바일 앱 빌드는 범위 밖.
**트리거 범위:** `feature/phase1-backend` 브랜치로의 push만. 다른 브랜치 push는 빌드를 트리거하지 않음.

## 2. 현재 인프라 (확인된 사실)

- Jenkins는 `jenkins/jenkins:lts` Docker 이미지로 이미 로컬에서 실행 중 (컨테이너명 `jenkins`,
  `localhost:8080`, 2주 이상 가동). 이 컨테이너를 그대로 재사용한다.
- 설치된 플러그인 중 `git`, `github`, `docker-workflow`, `pipeline-*` 계열 확인됨 — 추가 플러그인
  설치 불필요.
- 컨테이너 안에 **Python3가 없음** — pytest 실행을 위해 1회 설치 필요 (`apt-get install python3
  python3-pip python3-venv`, `docker exec -u root jenkins ...`로 수행).
- 컨테이너 안에서 `host.docker.internal`이 호스트(192.168.65.254 계열)로 정상 해석됨 — 호스트에서
  돌고 있는 PostgreSQL(`localhost:5432`, DB `palette_test`, 계정 `palette`/`palette123`)에 이
  호스트명으로 접근 가능.
- Docker 소켓은 jenkins 컨테이너 안에서 권한 거부(`permission denied`) — Docker-in-Docker 방식은
  쓰지 않고, 컨테이너에 Python을 직접 설치하는 방식을 택한다.
- GitHub 저장소(`yelimi/palette-app`)는 public — Jenkins의 코드 체크아웃에 별도 인증 불필요.
- ngrok 설치 및 authtoken 등록 완료 (Jenkins를 인터넷에서 webhook으로 호출 가능하게 하는 터널).

## 3. 아키텍처

```
GitHub (feature/phase1-backend에 push)
   │ webhook (POST, 저장소 전체에 걸림)
   ▼
ngrok 터널 (https://xxxx.ngrok-free.app → localhost:8080)
   │
   ▼
Jenkins (Docker 컨테이너, 기존 것 재사용)
   │ 단일 Pipeline Job — SCM을 feature/phase1-backend 브랜치로 고정
   │ "GitHub hook trigger for GITScm polling" → 이 브랜치에 실제 변경이
   │   있었는지 확인 후에만 빌드 시작 (다른 브랜치 push는 무시됨)
   ▼
pytest 53개 테스트 실행 (컨테이너에 Python3 설치됨)
   │
   ▼
host.docker.internal:5432 → 호스트 PostgreSQL (palette_test DB)
```

GitHub webhook 자체는 저장소 단위로만 걸리기 때문에 모든 브랜치의 push 이벤트가 Jenkins에 신호를
보내지만, Jenkins job에 설정된 "이 브랜치만 본다"는 설정 때문에 `feature/phase1-backend`가 아닌
push는 빌드로 이어지지 않는다.

## 4. Jenkins Job 구성

- **Job 종류:** 단일 **Pipeline** job (Multibranch 아님 — 단일 브랜치만 추적하므로 불필요한 복잡도)
- **Branch Specifier:** `*/feature/phase1-backend`
- **빌드 트리거:** "GitHub hook trigger for GITScm polling" 체크
- **Pipeline script:** 저장소 루트의 `Jenkinsfile` 사용 (Pipeline script from SCM)

## 5. 코드 변경 — `backend/tests/conftest.py`

현재 테스트 DB 주소가 하드코딩되어 있다 (`conftest.py:8`):
```python
TEST_DB_URL = "postgresql://palette:palette123@localhost:5432/palette_test"
```

Jenkins 컨테이너 안에서는 `localhost`가 컨테이너 자신을 가리켜 호스트의 DB에 닿지 않으므로,
환경변수로 override 가능하게 수정한다:

```python
import os

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://palette:palette123@localhost:5432/palette_test",
)
```

환경변수가 없으면 기존 기본값(`localhost`)을 그대로 쓰므로, 로컬에서 평소 `pytest` 실행하는
워크플로우는 전혀 바뀌지 않는다. Jenkinsfile에서만 `TEST_DATABASE_URL`을
`postgresql://palette:palette123@host.docker.internal:5432/palette_test`로 주입한다.

## 6. Jenkinsfile (저장소 루트에 신규 추가)

```groovy
pipeline {
    agent any
    environment {
        TEST_DATABASE_URL = 'postgresql://palette:palette123@host.docker.internal:5432/palette_test'
    }
    stages {
        stage('Setup') {
            steps {
                dir('backend') {
                    sh 'python3 -m venv venv'
                    sh './venv/bin/pip install -r requirements.txt'
                }
            }
        }
        stage('Test') {
            steps {
                dir('backend') {
                    sh './venv/bin/pytest tests/ -v'
                }
            }
        }
    }
}
```

## 7. 수동 설정 단계 (코드 변경 외에 사람이 직접 해야 하는 것)

1. `docker exec -u root jenkins apt-get update && apt-get install -y python3 python3-pip python3-venv`
2. Jenkins 웹 UI에서 위 4번 설정대로 Pipeline job 생성
3. `ngrok http 8080` 실행 → 발급된 URL 확인
4. GitHub 저장소 Settings → Webhooks에 `<ngrok-URL>/github-webhook/` 등록 (Content type: `application/json`, event: `push`)

## 8. 리스크 / 알아둘 점

- **ngrok 재시작 시 URL이 바뀜.** 터널 프로세스가 재시작되면(컴퓨터 재부팅, 수동 종료 등) 새
  URL이 발급되므로, 그때마다 GitHub webhook 주소를 갱신해야 한다. 터널을 계속 켜두면 문제 없음.
- **ngrok 무료 티어의 인터스티셜(경고 페이지) 가능성.** 과거 ngrok 무료 티어는 인증 없는 터널에
  경고 페이지를 끼워넣어 webhook 요청을 방해한 적이 있었는데, 이미 authtoken을 등록했으므로 이
  문제는 발생하지 않을 가능성이 높다 — 실제 webhook 테스트 시 확인 필요.
- **DB 연결은 설계상 가능함을 확인했으나(`host.docker.internal` 해석 성공), 실제 TCP 연결까지는
  아직 테스트하지 않았다** — 구현 단계에서 `pytest` 첫 실행 시 확인.
- 자동화 테스트 범위는 백엔드뿐이며, 모바일 앱 쪽 빌드/테스트는 포함하지 않는다 (Phase 4에서
  Appium 등으로 별도 다룰 예정).

## 9. 완료 기준

- [ ] `feature/phase1-backend`에 push하면 Jenkins가 1분 내로 빌드를 시작한다
- [ ] 다른 브랜치(예: `feature/phase2-mobile-app`)에 push해도 이 Jenkins job은 빌드되지 않는다
- [ ] pytest 53개 테스트가 Jenkins 빌드 안에서 전부 통과한다
- [ ] 로컬에서 `cd backend && pytest tests/ -v`를 환경변수 없이 실행해도 기존처럼 정상 동작한다
      (conftest.py 변경이 로컬 워크플로우를 깨지 않았는지 확인)
