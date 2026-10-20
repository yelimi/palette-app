# Jenkins CI (백엔드 pytest 자동화) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `feature/phase1-backend` 브랜치에 push가 발생할 때마다, 기존 Docker Jenkins가 자동으로 백엔드 pytest 164개를 실행하도록 한다.

**Architecture:** 기존 `jenkins/jenkins:lts` 컨테이너를 재사용한다. 컨테이너에 Python3를 설치하고, 저장소 루트에 Jenkinsfile을 추가해 `backend/`에서 venv를 만들고 pytest를 돌린다. Jenkins Pipeline Job은 `feature/phase1-backend` 브랜치만 추적하도록 설정하고(Jenkins REST API로 생성), GitHub webhook → ngrok 터널로 push 신호를 전달한다. 테스트 DB 접속 주소는 환경변수로 override 가능하게 고쳐서, 컨테이너 안에서는 `host.docker.internal`로 호스트 PostgreSQL에 접근한다.

**Tech Stack:** Jenkins(Docker, 기존 컨테이너 `jenkins`), Python 3(컨테이너 내 신규 설치), pytest, ngrok, Jenkins REST API(Job 생성), GitHub webhook

**참고 설계 문서:** `docs/superpowers/specs/2026-10-10-jenkins-ci-design.md`

## Global Constraints

- 트리거 범위: `feature/phase1-backend` 브랜치로의 push만. 다른 브랜치 push는 빌드를 트리거하지 않음
- 로컬에서 환경변수 없이 `pytest tests/ -v` 실행 시 기존과 동일하게 동작해야 함 (conftest.py 변경이 기존 워크플로우를 깨면 안 됨)
- Jenkins 컨테이너 안의 Docker 소켓은 권한 거부 상태이므로 Docker-in-Docker 방식은 쓰지 않음 — 컨테이너에 Python을 직접 설치
- Jenkins 컨테이너 안에서 `host.docker.internal`로 호스트 PostgreSQL(`localhost:5432`, DB `palette_test`, 계정 `palette`/`palette123`)에 접근
- GitHub 저장소(`yelimi/palette-app`)는 public — 코드 체크아웃에 별도 인증 불필요
- Jenkins Job 생성은 UI 클릭이 아니라 Jenkins REST API(사용자 API 토큰 + Basic Auth)로 자동화
- ngrok은 이미 설치 및 authtoken 등록 완료된 상태

---

## 파일 구조

```
palette-app/
├── Jenkinsfile                      # 신규 — Jenkins가 읽는 파이프라인 정의
└── backend/
    └── tests/
        └── conftest.py              # 수정 — TEST_DB_URL을 환경변수로 override 가능하게
```

---

## Task 1: conftest.py — 테스트 DB 주소 환경변수화

**Files:**
- Modify: `backend/tests/conftest.py:8`

**Interfaces:**
- Produces: `TEST_DB_URL` — 환경변수 `TEST_DATABASE_URL`이 설정되어 있으면 그 값을, 없으면 기존 기본값(`postgresql://palette:palette123@localhost:5432/palette_test`)을 사용

- [ ] **Step 1: 현재 동작 확인 (베이스라인)**

```bash
cd /Users/jang-yelim/Desktop/palette-app/backend
source venv/bin/activate
pytest tests/ -v 2>&1 | tail -5
```

Expected: `164 passed`

- [ ] **Step 2: conftest.py 수정**

`backend/tests/conftest.py`의 1~8번째 줄을 아래로 교체:

```python
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://palette:palette123@localhost:5432/palette_test",
)
```

- [ ] **Step 3: 환경변수 없이 실행해 기존과 동일하게 동작하는지 확인**

```bash
cd /Users/jang-yelim/Desktop/palette-app/backend
source venv/bin/activate
unset TEST_DATABASE_URL
pytest tests/ -v 2>&1 | tail -5
```

Expected: `164 passed` (Step 1과 동일한 결과)

- [ ] **Step 4: 환경변수가 실제로 읽히는지 확인 (일부러 잘못된 주소로)**

```bash
cd /Users/jang-yelim/Desktop/palette-app/backend
source venv/bin/activate
TEST_DATABASE_URL="postgresql://palette:palette123@nonexistent-host:5432/palette_test" pytest tests/test_auth.py -v 2>&1 | tail -15
```

Expected: 연결 실패 에러(`could not translate host name "nonexistent-host"` 등) — 환경변수가 실제로 적용되고 있다는 증거. (Step 2의 코드가 없었다면 이 테스트는 여전히 `localhost`로 붙어서 통과했을 것임)

- [ ] **Step 5: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add backend/tests/conftest.py
git commit -m "feat: 테스트 DB 주소를 환경변수로 override 가능하게 변경

Jenkins 컨테이너 안에서는 localhost가 컨테이너 자신을 가리켜
호스트 PostgreSQL에 닿지 않으므로, TEST_DATABASE_URL 환경변수로
override 가능하게 한다. 환경변수 없으면 기존 기본값 그대로 사용."
```

---

## Task 2: Jenkinsfile 추가

**Files:**
- Create: `Jenkinsfile` (저장소 루트)

**Interfaces:**
- Consumes: Task 1의 `TEST_DATABASE_URL` 환경변수 지원
- Produces: Jenkins가 Pipeline Job에서 참조할 `Jenkinsfile` (Task 4에서 Job 생성 시 `scriptPath: Jenkinsfile`로 참조)

- [ ] **Step 1: Jenkinsfile 작성**

`/Users/jang-yelim/Desktop/palette-app/Jenkinsfile`:

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

- [ ] **Step 2: Groovy 문법 기본 검증 (중괄호 짝 확인)**

```bash
python3 -c "
content = open('/Users/jang-yelim/Desktop/palette-app/Jenkinsfile').read()
assert content.count('{') == content.count('}'), '중괄호 개수 불일치'
print('중괄호 짝 맞음:', content.count('{'), '쌍')
"
```

Expected: `중괄호 짝 맞음: 4 쌍`

(실제 Jenkins Pipeline DSL 문법 검증은 Task 5에서 실제 빌드를 돌려볼 때 이루어진다 — Jenkins 자체 crumb 인증이 필요한 `/pipeline-model-converter/validate` 엔드포인트는 이 태스크에서 쓰지 않는다.)

- [ ] **Step 3: Commit**

```bash
cd /Users/jang-yelim/Desktop/palette-app
git add Jenkinsfile
git commit -m "feat: Jenkins Pipeline용 Jenkinsfile 추가

backend/에서 venv 생성 후 pytest 실행. TEST_DATABASE_URL을
host.docker.internal로 지정해 Jenkins 컨테이너에서 호스트
PostgreSQL에 접근한다."
```

---

## Task 3: Jenkins 컨테이너에 Python3 설치

**Files:** 없음 (컨테이너 환경 변경만, 저장소 코드 변경 없음)

**Interfaces:**
- Produces: Jenkins 컨테이너 안에서 `python3`, `pip3`, `python3 -m venv` 사용 가능

- [ ] **Step 1: 설치 전 상태 확인**

```bash
docker exec jenkins which python3
```

Expected: (출력 없음, 종료 코드 1 — 아직 설치 안 됨)

- [ ] **Step 2: Python3 설치**

```bash
docker exec -u root jenkins apt-get update
docker exec -u root jenkins apt-get install -y python3 python3-pip python3-venv
```

Expected: `python3-venv` 포함 설치 완료 메시지, 에러 없음

- [ ] **Step 3: 설치 확인**

```bash
docker exec jenkins python3 --version
docker exec jenkins python3 -m venv --help
```

Expected: 둘 다 에러 없이 출력 (Python 버전 문자열, venv 사용법)

- [ ] **Step 4: 호스트 PostgreSQL에 실제로 연결 가능한지 확인 (TCP 레벨)**

```bash
docker exec jenkins python3 -c "
import socket
s = socket.create_connection(('host.docker.internal', 5432), timeout=5)
print('연결 성공')
s.close()
"
```

Expected: `연결 성공`

(이 Task는 코드 커밋이 없으므로 git commit 단계 없음 — 컨테이너 자체의 상태 변경)

---

## Task 4: Jenkins Pipeline Job 생성 (REST API)

**Files:** 없음 (Jenkins 서버 상태 변경만)

**Interfaces:**
- Consumes: 사용자의 Jenkins 로그인 ID + API 토큰 (대화 중 전달됨, 평문으로 파일에 기록하지 않음)
- Produces: Jenkins Job `palette-backend-ci` — `feature/phase1-backend` 브랜치 추적, GitHub push trigger 활성화

- [ ] **Step 1: 인증 확인**

```bash
curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/json
```

Expected: `200`

- [ ] **Step 2: CSRF crumb 발급**

```bash
CRUMB=$(curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
  "http://localhost:8080/crumbIssuer/api/json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['crumbRequestField']+':'+d['crumb'])")
echo "$CRUMB"
```

Expected: `Jenkins-Crumb:<긴 16진수 문자열>` 형태 출력

- [ ] **Step 3: Job config.xml 작성**

```bash
cat > /tmp/palette-backend-ci-config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>feature/phase1-backend push 시 pytest 자동 실행</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
      <triggers>
        <com.cloudbees.jenkins.GitHubPushTrigger>
          <spec></spec>
        </com.cloudbees.jenkins.GitHubPushTrigger>
      </triggers>
    </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/yelimi/palette-app.git</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/feature/phase1-backend</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF
```

Expected: 파일 생성됨, 특별한 출력 없음

- [ ] **Step 4: Job 생성 요청**

```bash
curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
  -H "$CRUMB" \
  -H "Content-Type: application/xml" \
  --data-binary @/tmp/palette-backend-ci-config.xml \
  -w "\nHTTP_STATUS:%{http_code}\n" \
  "http://localhost:8080/createItem?name=palette-backend-ci"
```

Expected: `HTTP_STATUS:200`

- [ ] **Step 5: Job 생성 확인**

```bash
curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
  "http://localhost:8080/job/palette-backend-ci/api/json" | python3 -m json.tool | head -20
```

Expected: Job 이름, `"buildable": true` 등이 포함된 JSON 출력 (404나 에러 없음)

- [ ] **Step 6: 수동으로 1회 빌드 트리거해서 파이프라인 자체가 동작하는지 확인**

```bash
curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
  -H "$CRUMB" \
  -X POST "http://localhost:8080/job/palette-backend-ci/build"

# venv 생성 + pip install + pytest(로컬 실측 105초)까지 포함되므로
# 고정 sleep 대신 완료될 때까지 폴링 (최대 5분)
for i in $(seq 1 30); do
  sleep 10
  RESULT=$(curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
    "http://localhost:8080/job/palette-backend-ci/lastBuild/api/json" | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('result') or 'RUNNING')")
  echo "폴링 $i: $RESULT"
  if [ "$RESULT" != "RUNNING" ]; then break; fi
done
echo "최종 결과: $RESULT"
```

Expected: `최종 결과: SUCCESS`

(이 Task는 저장소 코드 변경이 없으므로 git commit 없음)

---

## Task 5: ngrok 터널 + GitHub webhook 등록 + End-to-End 확인

**Files:** 없음

**Interfaces:**
- Consumes: Task 4에서 만든 Job `palette-backend-ci`
- Produces: `feature/phase1-backend`에 push할 때마다 자동 빌드되는 동작하는 전체 파이프라인

- [ ] **Step 1: ngrok 터널 백그라운드 실행**

```bash
nohup ngrok http 8080 --log=stdout > /tmp/ngrok.log 2>&1 &
sleep 5
cat /tmp/ngrok.log | grep -i "url="
```

Expected: `url=https://xxxx.ngrok-free.app` 형태의 로그 라인 (이 URL을 다음 단계에서 사용)

- [ ] **Step 2: 인터스티셜 경고 페이지 없이 바로 응답하는지 확인**

```bash
NGROK_URL="<Step 1에서 확인한 URL>"
curl -s -o /dev/null -w "%{http_code}\n" "$NGROK_URL"
```

Expected: `403` (Jenkins가 익명 접근을 거부하는 403 — ngrok 자체 경고 페이지가 아니라 Jenkins의 응답이라는 뜻. HTML 응답 본문에 ngrok 안내문구가 섞여있으면 인터스티셜이 끼어든 것이므로, 그 경우 `curl -s "$NGROK_URL"`로 본문을 직접 확인해서 "ngrok" 관련 문구가 있는지 판별)

- [ ] **Step 3: GitHub webhook 등록**

```bash
NGROK_URL="<Step 1에서 확인한 URL>"
gh api repos/yelimi/palette-app/hooks -X POST \
  -f name=web \
  -f "config[url]=${NGROK_URL}/github-webhook/" \
  -f "config[content_type]=json" \
  -f active=true \
  -f "events[]=push"
```

Expected: JSON 응답에 `"id"` 필드가 있는 webhook 객체 (생성 성공)

- [ ] **Step 4: End-to-End 확인 — feature/phase1-backend에 push하면 빌드되는지**

```bash
PREV_BUILD=$(curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
  "http://localhost:8080/job/palette-backend-ci/api/json" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['lastBuild']['number'])")
echo "이전 빌드 번호: $PREV_BUILD"

cd /Users/jang-yelim/Desktop/palette-app
git commit --allow-empty -m "test: Jenkins webhook 동작 확인용 빈 커밋"
git push origin feature/phase1-backend

# webhook 전달 + 빌드 시작까지 시간이 걸릴 수 있으므로 폴링 (최대 3분)
for i in $(seq 1 18); do
  sleep 10
  NEW_BUILD=$(curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
    "http://localhost:8080/job/palette-backend-ci/api/json" | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['lastBuild']['number'])")
  echo "폴링 $i: lastBuild=$NEW_BUILD"
  if [ "$NEW_BUILD" != "$PREV_BUILD" ]; then break; fi
done
echo "이전: $PREV_BUILD / 이후: $NEW_BUILD"
```

Expected: `이후` 번호가 `이전` 번호보다 1 증가 (webhook으로 새 빌드가 트리거됐다는 뜻)

- [ ] **Step 5: 음성 확인 — 다른 브랜치에 push해도 빌드 안 되는지**

```bash
PREV_BUILD=$(curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
  "http://localhost:8080/job/palette-backend-ci/api/json" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['lastBuild']['number'])")
echo "이전 빌드 번호(Step 4 종료 시점과 동일해야 함): $PREV_BUILD"

cd /Users/jang-yelim/Desktop/palette-app/.claude/worktrees/feature+phase2-mobile-app
git commit --allow-empty -m "test: 다른 브랜치 push가 Jenkins를 트리거하지 않는지 확인용"
git push origin feature/phase2-mobile-app

# webhook은 거의 즉시 도착하므로, 넉넉히 60초만 기다린 뒤
# (별도 폴링 불필요 — "증가하지 않았다"를 확인하는 것이므로 한 번만 체크)
sleep 60
NEW_BUILD=$(curl -s -u "<JENKINS_USER>:<JENKINS_API_TOKEN>" \
  "http://localhost:8080/job/palette-backend-ci/api/json" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['lastBuild']['number'])")
echo "이전: $PREV_BUILD / 60초 후: $NEW_BUILD"
```

Expected: `이전`과 `60초 후` 번호가 **동일**(증가하지 않음) — `feature/phase2-mobile-app` push는 이 Job을 트리거하지 않았다는 뜻

- [ ] **Step 6: 테스트용 빈 커밋 정리 (선택)**

Step 4/5에서 만든 `--allow-empty` 커밋은 기록용으로 남겨도 무방하다. 지우고 싶으면:

```bash
cd /Users/jang-yelim/Desktop/palette-app
git log --oneline -3
# 필요 시 git reset --hard로 직접 제거 여부는 사용자 판단
```

---

## 완료 기준

- [ ] `backend/tests/conftest.py` 변경 후에도 로컬 `pytest tests/ -v`가 환경변수 없이 164개 전부 통과
- [ ] Jenkins 컨테이너에 Python3 설치 완료, `host.docker.internal:5432` TCP 연결 확인
- [ ] Jenkins Job `palette-backend-ci`가 REST API로 생성되고 수동 빌드 시 `SUCCESS`
- [ ] ngrok 터널 + GitHub webhook 등록 완료
- [ ] `feature/phase1-backend`에 push → Jenkins 빌드 자동 트리거 확인 (lastBuild 번호 증가)
- [ ] `feature/phase2-mobile-app`에 push → Jenkins 빌드 트리거되지 않음 확인 (lastBuild 번호 불변)

---

## 다음 단계

- Phase 4 QA 자동화(Appium/Selenium) 작업 시 이 Jenkins 인프라를 재사용할 수 있음
