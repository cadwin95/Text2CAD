# 개발 환경 가이드

## 로컬 개발 (권장)

현재 프로젝트는 **로컬 개발 환경**을 기본으로 합니다.

### 시작하기

```bash
# 1. 환경 변수 설정
cp env.template .env
# .env 파일 편집하여 OPENAI_API_KEY 입력

# 2. Python 패키지 설치
uv sync

# 3. Frontend 의존성 설치
cd frontend && npm install && cd ..

# 4. 개발 서버 시작
./start_dev.sh
```

### 서비스 접속

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 환경 변수

**필수**:
- `OPENAI_API_KEY`: OpenAI API 키 (GPT-4 사용)

**선택사항**:
- `GROQ_API_KEY`: Groq API 키
- `LITELLM_BASE_URL`: LiteLLM Proxy URL (로컬에서는 미사용)

### LiteLLM Fallback

로컬 개발 시 LiteLLM Proxy가 없어도 자동으로 **OpenAI API로 직접 연결**됩니다.

코드 위치: `src/agent/ocx_agent.py:76-89`

```python
# 자동 Fallback 로직
if not base_url or "localhost" in base_url:
    if os.getenv("OPENAI_API_KEY"):
        base_url = None  # OpenAI 직접 사용
```

### 장점

- ✅ 빠른 시작 (2-3초)
- ✅ 적은 메모리 사용 (~500MB)
- ✅ Hot-reload 지원
- ✅ FreeCAD 로컬 설치 시 3D 모델 생성 가능

### 단점

- ❌ LiteLLM Proxy 없음 (모델 통합 제한)
- ❌ PostgreSQL 없음 (로깅/메트릭 없음)
- ❌ Prometheus 없음 (모니터링 없음)

## Docker 개발 (고사양 환경)

고사양 PC나 프로덕션 환경에서는 Docker 사용 가능.

자세한 내용: [DOCKER.md](DOCKER.md)

### 요구사항

- CPU: 4코어 이상
- RAM: 8GB 이상
- 디스크: 10GB 여유

### 빠른 시작

```bash
# Docker로 실행
make up

# 또는
docker compose up --build
```

### 포함 서비스

- Backend (FastAPI)
- Frontend (Vite)
- PostgreSQL + pgvector
- LiteLLM Proxy
- (선택) Prometheus

## 개발 워크플로우

### 1. 코드 수정

```bash
# Backend 수정 시 자동 재시작 (uvicorn --reload)
# Frontend 수정 시 자동 반영 (Vite HMR)
```

### 2. 테스트

```bash
# Backend 테스트
cd backend && uv run pytest

# Frontend 린트
cd frontend && npm run lint
```

### 3. 코드 품질

```bash
# 린팅 & 타입 체크
make lint
```

## FreeCAD 설정

### macOS

```bash
# FreeCAD 설치 (Homebrew)
brew install --cask freecad

# 환경 변수 설정 (.env)
FREECAD_PATH=/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
```

### Docker (선택)

FreeCAD Docker 이미지 사용:
```bash
docker pull ianussimoddocker/freecad
```

자세한 설정: [DOCKER.md](DOCKER.md#freecad-docker-통합)

## Makefile 명령어

```bash
make install   # 의존성 설치
make dev       # 로컬 개발 서버 시작
make up        # Docker로 시작
make lint      # 코드 품질 검사
make test      # 테스트 실행
```

## 문제 해결

### 포트 충돌

```bash
# 포트 8000, 5173 사용 중인 프로세스 종료
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### OpenAI API 에러

`.env` 파일에 `OPENAI_API_KEY`가 제대로 설정되었는지 확인:
```bash
cat .env | grep OPENAI_API_KEY
```

### FreeCAD 없음

FreeCAD가 없어도 **OCX XML은 생성**됩니다. 3D 모델만 생성되지 않습니다.

시뮬레이션 모드로 작동하며 사용자에게 안내 메시지가 표시됩니다.

## 추가 문서

- [AGENT_FLOW.md](AGENT_FLOW.md): 에이전트 흐름도
- [DOCKER.md](DOCKER.md): Docker 배포 가이드
- [QUICKSTART.md](QUICKSTART.md): 빠른 시작 가이드
