# Agent Flow Architecture (Code-as-Intermediate)

LLM이 직접 XML을 쓰지 않고, OCXBuilder SDK를 호출하는 파이썬 코드를 생성·실행·검증하는 흐름입니다.

## 전체 흐름도

```mermaid
flowchart TD
    Start([사용자 입력]) --> Frontend[Frontend: ChatInterface]
    Frontend -->|POST /api/chat| Backend[FastAPI]

    Backend --> Pipeline[GenerativeDesignCoordinator]
    Pipeline --> CodeAgent[OCXCodeAgent<br/>\"Python only\" system prompt]
    CodeAgent --> Code[Python Builder Script]
    Code --> Executor[OcxCodeExecutor<br/>sandboxed exec]
    Executor --> XML[OCX XML]
    XML --> Sanity[XMLValidator<br/>auto self-check]
    Sanity -->|pass| FreeCAD[FreeCADService<br/>OCX -> STL/PNG]
    Sanity -->|fail & retry| CodeAgent

    FreeCAD --> Files[Save XML/STL/(PNG)]
    Files -->|enable_validation| VLM[VLMValidator<br/>GPT-4o vision]
    VLM --> Validation[검증 결과]

    Files --> Response
    Validation --> Response
    Response[API 응답<br/>xml_url/model_url/png_url<br/>builder_code/xml_validation/agent_trace] --> Frontend
    Frontend[Runs Panel<br/>OCX/XML/PNG + diff<br/>builder_code/agent_trace/xml_validation] --> End([결과 표시])
```

## 핵심 컴포넌트

- **GenerativeDesignCoordinator** (`src/agent/generative_design.py`): Instruction → 코드 생성 → 실행 → XML 검증 → 재시도 루프(기본 2회).
- **OCXCodeAgent** (`src/agent/ocx_code_agent.py`): OCXBuilder 전용 파이썬 코드만 생성하는 LLM 에이전트.
- **OcxCodeExecutor** (`src/agent/code_executor.py`): 안전한 빌트인만 허용한 샌드박스에서 코드 실행, `xml_output` 추출. 실행 시 repo root와 `src/`를 `sys.path`에 추가해 `import ocx_sdk`가 어떤 cwd에서도 동작.
- **XMLValidator** (`src/agent/xml_validator.py`): 파싱/구조 검증 후 실패 시 코드 생성 단계에 피드백 전달.
- **OCXBuilder SDK** (`src/ocx_sdk/builder.py`): `create_plate`, `create_stiffeners_on_plate`, `create_stiffener`, `add_opening`, `to_xml_string` 등 반복 계산을 캡슐화.
- **FreeCADService** (`backend/services/freecad_service.py`): OCX → STL/PNG 변환, 실패 시 debug_info 포함.
- **OCX Importer** (`src/freecad_tools/ocx_importer.py`): 패널을 면 → 솔리드로 압출, stiffener를 방향 맞춘 실린더로 생성, openings를 패널 솔리드에서 컷(가능할 때)하여 STL 시각화 품질 개선.
- **VLMValidator** (`src/agent/vlm_validator.py`): PNG가 있을 때 Vision 모델(gpt-4o 또는 llava)으로 요구사항 매칭 검사. 모델은 환경 변수 `VLM_VALIDATION_MODEL` 또는 API 요청의 `vlm_model`로 지정 가능.
- **Frontend Runs Panel** (`frontend/src/components/ChatInterface.jsx`): 각 run에 OCX/XML/PNG 링크 + diff + `builder_code`, `agent_trace`, `xml_validation`을 그대로 노출하여 디버깅 가시성 제공.

## 요청/응답 확장

- 요청: `POST /api/chat` (기존과 동일), `enable_validation` 활성 시 PNG+VLM 검증.
  - `model`: 코드 생성에 사용할 모델 (기본값: gpt-4o)
  - `vlm_model`: VLM 검증에 사용할 모델 (기본값: gpt-4o, 옵션: llava)
- 응답 필드 추가:
  - `builder_code`: LLM이 생성한 파이썬 코드
  - `xml_validation`: XMLValidator 결과
  - `agent_trace`: 코드 생성/실행/검증 시도 기록

## 환경 변수

```bash
LITELLM_BASE_URL=http://localhost:4000
LITELLM_API_KEY=sk-1234
OPENAI_API_KEY=your_openai_api_key

# 모델 선택 (선택사항)
CODE_GENERATION_MODEL=gpt-4o      # 코드 생성 모델
VLM_VALIDATION_MODEL=gpt-4o       # VLM 검증 모델 (gpt-4o 또는 llava)
```

자세한 모델 선택 전략은 [MODEL_SELECTION_STRATEGY.md](./MODEL_SELECTION_STRATEGY.md) 참고.

## 실패/재시도 정책

- 코드 실행 실패 → 예외 메시지를 LLM에 피드백 → 재생성.
- XML 구조 검증 실패 → 문제 리스트를 LLM에 전달 → 재생성.
- FreeCAD 미설치 시: STL/PNG 생성을 건너뛰고 XML만 반환(시뮬레이션 모드 안내).

## 로컬 디버그 & 참고 문서

- `debug_freecad.py`: 로컬에서 OCX XML을 임포트/렌더링해 FreeCAD 파이프를 점검하는 스크립트.
- `AGENT_FLOW_VERIFICATION.md`: 이전(직접 XML 생성) 흐름 검증 기록. 최신 Code-as-Intermediate 흐름에 맞춘 재검증 필요 시 갱신.
