# Architecture Overview

## 목적
- CADAI 에이전트가 LiteLLM Proxy를 통해 다양한 LLM 백엔드를 호출하고, FreeCADCmd로 CAD 도구를 실행해 결과를 수집한다.

## 시스템 개요
```
+-------------+     +----------------------+     +------------------+
|  CLI /     | --> | AgentRuntime (Python)| --> | LiteLLM Proxy    |
|  Typer App |     |  - llm.get_async_client|    |  (OpenAI API v1) |
+-------------+     |  - freecad.tools      |     +--+------+-------+
                    +-----------+----------+        |      |
                                |                   |      |
                                v                   v      v
                        +---------------+     +----------+ +----------------+
                        | FreeCAD Tools |     | OpenAI   | | Groq           |
                        | (freecad_box) |     | (remote) | | llama.cpp      |
                        +-------+-------+     +----------+ +----------------+
                                |
                                v
                        +---------------+
                        | FreeCADCmd    |
                        | FCStd / STL   |
                        +---------------+
```

## 주요 구성 요소
- `app/cli.py`: Typer 기반 진입점. 모델 선택, 데모 프롬프트, transcript 저장 옵션을 제공한다.
- `app/agent/runtime.py`: 단일 턴 루프 수행. LiteLLM Proxy(OpenAI SDK)를 호출하고 JSON 응답을 분석해 FreeCAD 툴을 실행한다.
- `app/llm.py`: `.env`에서 Proxy URL/Key를 읽어 `AsyncOpenAI` 클라이언트를 생성한다.
- `app/tools/freecad_box.py`: FreeCADCmd용 매크로 생성 및 실행. FCStd 파일과 stdout/stderr를 반환한다.
- `litellm_config.yaml`: Proxy 라우팅 테이블. `openai/gpt-4o-mini`, `groq/gpt-oss-20b`, `openai/llama.cpp` 모델을 등록한다.
- `docker-compose.yml`: LiteLLM Proxy(4000)와 llama.cpp 서버(8080)를 컨테이너로 제공한다.
- `freecad/`: Pixi 환경에서 빌드되는 FreeCAD 소스 트리. `FREECAD_CMD`가 여기서 생성된다.

## 데이터 흐름
1. 사용자가 `python3 -m app.cli ...`를 실행하면 Typer CLI가 AgentRuntime을 초기화한다.
2. AgentRuntime은 LiteLLM 설정을 읽어 모델을 선택하고, LiteLLM Proxy(`/v1/chat/completions`)에 요청한다.
3. Proxy는 등록된 백엔드(OpenAI, Groq, llama.cpp) 중 해당 모델로 트래픽을 라우팅한다.
4. LLM이 JSON으로 `freecad.create_box` 툴 호출을 지시하면, AgentRuntime이 FreeCAD 도구를 실행한다.
5. `freecad.create_box`는 FreeCADCmd를 호출해 매크로를 수행하고 결과(FCStd, stdout 등)를 반환한다.
6. 전체 메시지와 도구 결과는 transcript에 기록되어 재현 가능성을 보장한다.

## 의존성 및 환경
- Python 런타임: `.venv` 또는 `uv run`
- LiteLLM Proxy: Docker Compose 또는 `uv run litellm`
- FreeCAD 빌드: `pixi install`, `pixi run build-debug`
- 환경 변수: `FREECAD_CMD`, `OPENAI_API_KEY`, `GROQ_API_KEY`, `LITELLM_PROXY_URL`(선택)

## 테스트 흐름
- `pytest`는 CLI/Runtime/도구 단위 테스트를 실행한다.
- `pytest -m integration`은 `FREECAD_CMD`가 설정된 경우 FreeCADCmd를 실제로 호출해 통합 경로를 검증한다.
