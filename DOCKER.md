# Docker Deployment Guide

> [!NOTE]
> 현재 로컬 개발은 `start_dev.sh`를 사용합니다. Docker는 프로덕션 배포나 고사양 환경에서만 사용하세요.

## 시스템 요구사항

### 최소 사양 (Docker 사용 시)
- **CPU**: 4코어 이상
- **RAM**: 8GB 이상
- **디스크**: 10GB 여유 공간
- **Docker Desktop**: 최신 버전

### 권장 사양
- **CPU**: 8코어 이상
- **RAM**: 16GB 이상
- **디스크**: 20GB 이상

## Docker Compose 구성

### 포함된 서비스

```yaml
services:
  backend:       # FastAPI 백엔드 (포트 8000)
  frontend:      # React + Vite 프론트엔드 (포트 5173)
  postgres:      # PostgreSQL + pgvector (포트 5433)
  litellm-proxy: # LiteLLM API Gateway (포트 4000)
  # prometheus:  # 메트릭 모니터링 (선택사항, 비활성화됨)
```

### 네트워크
- 전용 네트워크: `litellm_network`
- 모든 서비스가 동일 네트워크에서 통신

## 사용 방법

### 1. 환경 변수 설정

```bash
cp env.template .env
# .env 파일을 편집하여 API 키 입력
```

필수 환경 변수:
- `OPENAI_API_KEY`: OpenAI API 키
- `LITELLM_MASTER_KEY`: LiteLLM 마스터 키 (임의 생성)
- `GROQ_API_KEY`: Groq API 키 (선택)

### 2. Docker Compose 실행

```bash
# 전체 스택 실행 (빌드 포함)
make up

# 또는 직접 실행
docker compose up --build

# 백그라운드 실행
docker compose up -d
```

### 3. 서비스 접속

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **LiteLLM Proxy**: http://localhost:4000
- **PostgreSQL**: localhost:5433

### 4. 종료

```bash
docker compose down

# 볼륨까지 삭제 (데이터베이스 초기화)
docker compose down -v
```

## FreeCAD Docker 통합 (선택사항)

### FreeCAD CLI 이미지

3D 모델 생성을 위해 FreeCAD를 Docker로 실행할 수 있습니다.

**이미지**: `ianussimoddocker/freecad`
- 크기: 약 2GB
- 플랫폼: linux/amd64
- 용도: Headless FreeCAD 스크립트 실행

### 사용 예시

```bash
# 이미지 다운로드
docker pull ianussimoddocker/freecad

# FreeCAD 버전 확인
docker run --rm ianussimoddocker/freecad freecadcmd --version

# Python 스크립트 실행
docker run --rm \
  -v $(pwd):/workspace \
  ianussimoddocker/freecad \
  freecadcmd /workspace/script.py
```

### Docker Compose에 FreeCAD 추가 (고급)

`docker-compose.yml`에 다음 서비스를 추가:

```yaml
  freecad:
    image: ianussimoddocker/freecad
    volumes:
      - ./backend/static:/workspace
      - ./src:/app/src
    command: tail -f /dev/null  # Keep container running
    restart: unless-stopped
```

Backend에서 호출:
```python
subprocess.run([
    "docker", "exec", "freecad-container",
    "freecadcmd", "/workspace/script.py"
])
```

## 트러블슈팅

### 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -ti:8000 -ti:5173 -ti:4000 -ti:5433

# 프로세스 종료
lsof -ti:포트번호 | xargs kill -9
```

### PostgreSQL 버전 충돌
기존 볼륨이 다른 버전일 경우:
```bash
docker compose down -v  # 볼륨 삭제
docker compose up       # 재시작
```

### 디스크 공간 부족
```bash
# 사용하지 않는 Docker 리소스 정리
docker system prune -a

# 볼륨까지 정리
docker system prune -a --volumes
```

### 빌드 속도 느림
```bash
# 빌드 없이 실행 (이미지가 있을 때)
docker compose up

# 특정 서비스만 재빌드
docker compose build backend
```

## 로컬 개발 (권장)

Docker가 무거운 경우 로컬 개발 환경 사용:

```bash
# 로컬 실행
./start_dev.sh

# 또는
make dev
```

**장점**:
- 빠른 시작 (Docker 오버헤드 없음)
- 적은 메모리 사용
- 파일 변경 즉시 반영

**단점**:
- LiteLLM Proxy 없음 (OpenAI 직접 연결)
- PostgreSQL 없음 (로깅/메트릭 수집 불가)

## 프로덕션 배포

### 권장 사항

1. **환경 변수 분리**: `.env.production` 파일 사용
2. **볼륨 백업**: PostgreSQL 데이터 정기 백업
3. **리버스 프록시**: Nginx/Caddy 추가
4. **모니터링**: Prometheus 활성화
5. **로그**: 중앙 집중식 로깅 설정

### Docker Compose 오버라이드

프로덕션 설정:
```bash
# docker-compose.prod.yml 생성
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 참고 문서

- [Docker Documentation](https://docs.docker.com/)
- [LiteLLM Proxy Docs](https://docs.litellm.ai/docs/proxy/deploy)
- [FreeCAD Python API](https://wiki.freecad.org/Power_users_hub)
