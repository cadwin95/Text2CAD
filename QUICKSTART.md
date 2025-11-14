# FreeCAD Tool Calling Agent - 빠른 시작 가이드

## 5분 안에 시작하기

### 1단계: 환경 확인 (1분)

```bash
# Python 및 패키지 확인
python scripts/check_compatibility.py

# Docker 서비스 확인
python scripts/health_check.py

# 모델 호환성 확인
python scripts/check_model_compatibility.py
```

### 2단계: 패키지 설치 (2분)

```bash
# 기본 패키지 설치
uv sync

# MCP 서버용 패키지 (선택)
uv add fastmcp

# 학습용 패키지 (선택)
uv add unsloth torch transformers trl datasets
```

### 3단계: Agent 실행 (1분)

```python
# Python 인터프리터 실행
python

# Agent 테스트
from src.agent import ToolCallingAgent

agent = ToolCallingAgent(verbose=True)
result = agent.run("10mm x 10mm x 10mm 크기의 박스를 만들어줘")
print(result)
```

## 주요 사용 패턴

### 패턴 1: 간단한 명령 실행

```python
from src.agent import ToolCallingAgent

agent = ToolCallingAgent()

# 박스 생성
agent.run("10mm x 10mm x 10mm 박스를 만들어줘")

# 실린더 생성
agent.run("반지름 5mm, 높이 20mm인 실린더를 생성해")

# 구 생성
agent.run("반지름 7mm인 구를 만들어")
```

### 패턴 2: 이미지와 함께 사용

```python
from src.agent import ToolCallingAgent, VisionAnalyzer

# Vision 분석
analyzer = VisionAnalyzer()
vision_result = analyzer.analyze_image("./model.png")

# 분석 결과를 컨텍스트로 사용
agent = ToolCallingAgent()
agent.run(
    "이 이미지의 모델을 수정해줘",
    image_context=vision_result["analysis"]
)
```

### 패턴 3: 대화형 사용

```python
from src.agent import ToolCallingAgent

agent = ToolCallingAgent(verbose=True)

# 연속된 명령 (히스토리 유지)
agent.run("새 문서를 만들어줘")
agent.run("10x10x10 박스를 추가해")
agent.run("반지름 5mm인 구도 추가해")
agent.run("문서를 test.FCStd로 저장해줘")

# 히스토리 초기화
agent.reset()
```

## 학습 파이프라인 (10분)

### 1. 합성 데이터 생성 (3분)

```bash
python -m src.training.synthetic_data
```

생성된 데이터: `data/synthetic/synthetic_commands_*.json`

### 2. 실제 사용 데이터 수집 (5분)

```bash
python -m src.training.data_collector
```

여러 명령을 실행하면서 자동으로 OpenPipe에 로깅됩니다.

### 3. Fine-tuning (시간은 GPU에 따라 다름)

```bash
python -m src.training.finetune
```

학습된 모델: `models/finetuned/freecad-qwen-final/`

## 문제 해결

### Q: "openai 패키지가 설치되지 않았습니다"

```bash
uv add openai
```

### Q: "FreeCAD를 찾을 수 없습니다"

시뮬레이션 모드로 작동합니다. 실제 FreeCAD 없이도 개발 가능합니다.

### Q: "LiteLLM proxy에 연결할 수 없습니다"

```bash
# Docker 서비스 확인
docker-compose ps

# 서비스 재시작
docker-compose restart litellm-proxy
```

### Q: "Function calling이 작동하지 않습니다"

1. 모델이 function calling을 지원하는지 확인:
```bash
python scripts/check_model_compatibility.py
```

2. 지원하지 않으면 fine-tuning 필요:
```bash
python -m src.training.synthetic_data
python -m src.training.finetune
```

## 다음 단계

1. **도구 확장**: `src/freecad_tools/`에 새로운 FreeCAD 도구 추가
2. **MCP 서버**: `src/mcp_server/server.py`에 도구 등록
3. **학습 데이터**: 실제 사용하며 데이터 수집
4. **Fine-tuning**: 수집된 데이터로 모델 개선
5. **배포**: Fine-tuned 모델을 llama.cpp로 로드

자세한 내용은 [README.md](README.md)를 참조하세요.

