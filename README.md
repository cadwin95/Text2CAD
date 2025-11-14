# FreeCAD Tool Calling Agent

FreeCAD를 제어할 수 있는 AI Agent입니다. LiteLLM proxy를 통해 Qwen3-4B 모델을 사용하고, OpenPipe로 데이터를 수집하며, Unsloth로 fine-tuning합니다.

## 주요 기능

- 🛠️ **FreeCAD Tool Calling**: 자연어로 CAD 모델 생성 (박스, 실린더, 구, 원뿔 등)
- 🔄 **MCP 서버**: FastMCP를 사용한 도구 서버 구현
- 📊 **데이터 수집**: OpenPipe를 통한 자동 로깅
- 🤖 **Fine-tuning**: Unsloth로 Qwen 모델 fine-tuning
- 👁️ **Vision 분석**: VL 모델(LLaVA)로 CAD 이미지 분석
- 🐳 **Docker 통합**: llama.cpp + LiteLLM proxy 완전 구성

## 📁 프로젝트 구조

```
cadai/
├── 📄 README.md, QUICKSTART.md, TODO.md, CHANGELOG.md
├── ⚙️ docker-compose.yml, pyproject.toml, litellm_config.yaml
├── 🚀 start_server.sh, stop_server.sh
│
├── 📚 docs/                # 모든 가이드 문서
│   ├── PROJECT_STATUS.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── TROUBLESHOOTING.md
│   ├── FREECAD_SETUP.md
│   └── ...
│
├── 💡 examples/            # 예제 및 데모
│   ├── simple_box.FCStd
│   ├── simple_chair.FCStd
│   ├── interactive_freecad.py
│   └── ...
│
├── 🧪 tests/               # 테스트
│   ├── unit/              # 단위 테스트
│   ├── integration/       # 통합 테스트
│   ├── gui/               # GUI 테스트
│   └── results/           # 테스트 결과
│
├── 🔧 scripts/             # 유틸리티 스크립트
│   ├── check_compatibility.py
│   ├── health_check.py
│   └── ...
│
├── 💻 src/                 # 소스 코드
│   ├── agent/             # Tool calling agent
│   ├── mcp_server/        # FastMCP 서버
│   ├── freecad_tools/     # FreeCAD API 래퍼
│   └── training/          # 학습 및 fine-tuning
│
├── 🌐 web_viewer/          # 웹 인터페이스
│   ├── app.py             # Flask 서버
│   ├── templates/         # HTML 템플릿
│   └── models/            # 생성된 모델
│
├── 📊 data/                # 데이터
│   ├── synthetic/         # 합성 데이터
│   └── logs/              # 로그
│
└── 🛠️ freecad/            # FreeCAD 소스 (서브모듈)
```

## 시작하기

### 1. 환경 설정

```bash
# Python 패키지 설치
uv sync

# 환경 변수 설정
cp env.template .env
# .env 파일을 편집하여 API 키 입력
```

### 2. 호환성 체크

```bash
# Python 및 패키지 버전 확인
python scripts/check_compatibility.py

# Docker 서비스 상태 확인
python scripts/health_check.py

# 모델 호환성 확인
python scripts/check_model_compatibility.py
```

### 3. Docker 서비스 시작

Docker Compose가 이미 실행 중이므로 서비스 상태만 확인하세요:

```bash
docker-compose ps
```

### 4. Agent 실행

```bash
# Tool calling agent 테스트
python -m src.agent.toolcalling

# MCP 서버 시작 (별도 터미널)
python -m src.mcp_server.server
```

## 사용 예시

### Agent로 FreeCAD 제어

```python
from src.agent import ToolCallingAgent

# Agent 초기화
agent = ToolCallingAgent(verbose=True)

# 명령 실행
result = agent.run("10mm x 10mm x 10mm 크기의 박스를 만들어줘")
print(result)
```

### Vision 분석

```python
from src.agent import VisionAnalyzer

# Vision 분석기 초기화
analyzer = VisionAnalyzer(verbose=True)

# 이미지 분석
result = analyzer.analyze_image("./data/captures/model.png")
print(result["analysis"])
```

## 학습 파이프라인

### 1. 합성 데이터 생성

```bash
# GPT-4로 FreeCAD 명령 생성
python -m src.training.synthetic_data
```

### 2. 데이터 수집

```bash
# OpenPipe로 실제 사용 데이터 수집
python -m src.training.data_collector
```

### 3. Fine-tuning

```bash
# Unsloth로 모델 학습
python -m src.training.finetune
```

### 4. Fine-tuned 모델 배포

학습된 GGUF 모델을 docker-compose.yml에서 설정:

```yaml
llama-server:
  command:
    - -m
    - /models/freecad-qwen-gguf/model.gguf  # Fine-tuned 모델 경로
```

## 환경 변수

`.env` 파일에 다음 변수를 설정하세요:

```bash
# API 키
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
OPENPIPE_API_KEY=your_openpipe_key

# LiteLLM 설정
LITELLM_BASE_URL=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MASTER_KEY=your_master_key
```

## FreeCAD 도구

현재 지원하는 도구:

- `freecad_create_box`: 박스 생성
- `freecad_create_cylinder`: 실린더 생성
- `freecad_create_sphere`: 구 생성
- `freecad_create_cone`: 원뿔 생성
- `freecad_new_document`: 새 문서 생성
- `freecad_save_document`: 문서 저장
- `freecad_get_document_info`: 문서 정보 조회
- `freecad_export_image`: 이미지 내보내기

## VL 모델 설정 (선택사항)

LLaVA를 사용한 이미지 분석을 원하면 docker-compose.yml에 추가:

```yaml
llava-server:
  image: ghcr.io/ggerganov/llama.cpp:server
  command:
    - -m
    - /models/llava-v1.6-vicuna-7b.Q4_K_M.gguf
    - --mmproj
    - /models/mmproj-model-f16.gguf
    - --port
    - "8081"
  ports:
    - "8081:8081"
  volumes:
    - ./models:/models
```

그리고 litellm_config.yaml에 추가:

```yaml
- model_name: llava
  litellm_params:
    model: openai/llava
    api_base: http://llava-server:8081/v1
    api_key: dummy-token
```

## OpenPipe 통합

LiteLLM Config에 OpenPipe 콜백 추가:

```yaml
litellm_settings:
  success_callback: ["openpipe"]
  openpipe_api_key: os.environ/OPENPIPE_API_KEY
```

이제 모든 API 호출이 자동으로 OpenPipe에 로깅됩니다.

## 트러블슈팅

### FreeCAD가 설치되지 않았다고 나올 때

FreeCAD Python API가 없어도 개발은 가능합니다. 시뮬레이션 모드로 작동합니다.

실제 FreeCAD와 연동하려면:
1. FreeCAD 설치: https://www.freecad.org/
2. FreeCAD Python 환경 확인

### Function calling이 작동하지 않을 때

Qwen3-4B가 function calling을 지원하지 않을 수 있습니다. 다음을 시도하세요:

1. OpenPipe로 데이터 수집
2. Unsloth로 fine-tuning
3. Fine-tuned 모델로 교체

또는 Hermes-3, Llama-3.1 등 function calling 지원 모델로 교체하세요.

### Docker 서비스가 실행되지 않을 때

```bash
# 서비스 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f llama-server
docker-compose logs -f litellm-proxy
```

## 라이선스

MIT License

## 기여

이슈와 PR을 환영합니다!

