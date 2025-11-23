# 🧪 테스트 디렉토리

FreeCAD Tool-Calling Agent의 모든 테스트 파일입니다.

---

## 📂 디렉토리 구조

```
tests/
├── unit/               # 단위 테스트
│   ├── test_freecad_tools.py
│   └── test_mcp_server.py
│
├── integration/        # 통합 테스트
│   ├── test_agent.py
│   ├── test_agent_simple.py
│   ├── test_with_groq_oss.py
│   ├── test_finish_tool.py
│   ├── test_complex_objects.py
│   └── test_with_freecad_gui.py
│
├── gui/                # GUI 테스트
│   ├── test_interactive_gui.py
│   ├── test_gui_script.py
│   └── test_timeout_fix.py
│
└── results/            # 테스트 결과
    ├── 01_compatibility_check.txt
    ├── ...
    └── TEST_SUMMARY.md
```

---

## 🔬 단위 테스트 (unit/)

**개별 모듈의 기능 테스트**

### test_freecad_tools.py
FreeCAD primitives 및 document 관리 테스트

```bash
python tests/unit/test_freecad_tools.py
```

**테스트 항목**:
- Box, Cylinder, Sphere, Cone 생성
- Position 및 rotation 파라미터
- 문서 생성 및 저장
- 시뮬레이션 모드

### test_mcp_server.py
MCP 서버 기능 테스트

```bash
python tests/unit/test_mcp_server.py
```

**테스트 항목**:
- Tool 정의 및 스키마
- OpenAI function calling 형식
- Tool 실행

---

## 🔗 통합 테스트 (integration/)

**여러 모듈의 상호작용 테스트**

### test_agent.py
Agent 핵심 기능 테스트

```bash
python tests/integration/test_agent.py
```

**테스트 시나리오**:
- 단순 명령 처리
- 도구 호출 검증
- 결과 반환 확인

### test_agent_simple.py
Agent 간단한 시나리오 테스트

```bash
python tests/integration/test_agent_simple.py
```

### test_with_groq_oss.py
Groq OSS 모델 테스트

```bash
python tests/integration/test_with_groq_oss.py
```

**필수 설정**:
- Groq API 키 필요 (`.env`)
- `litellm_config.yaml`에 groq-oss 모델 설정

### test_finish_tool.py
finish 도구 기능 테스트

```bash
python tests/integration/test_finish_tool.py
```

**테스트 항목**:
- finish 도구 호출
- 명시적 작업 종료
- 결과 반환

### test_complex_objects.py
복잡한 객체 생성 테스트

```bash
python tests/integration/test_complex_objects.py
```

**테스트 객체**:
- 의자 (4개 다리 + 등받이 + 좌석)
- 사다리 (세로 막대 + 가로 발판)
- 테이블 (4개 다리 + 상판)

### test_with_freecad_gui.py
FreeCAD GUI 통합 테스트

```bash
python tests/integration/test_with_freecad_gui.py
```

**테스트 항목**:
- GUI 자동 열기
- 파일 저장 및 로드
- macOS 포그라운드 활성화

---

## 🖥️ GUI 테스트 (gui/)

**GUI 관련 기능 테스트**

### test_interactive_gui.py
인터랙티브 GUI 테스트

```bash
python tests/gui/test_interactive_gui.py
```

### test_gui_script.py
GUI 스크립트 실행 테스트

```bash
python tests/gui/test_gui_script.py
```

### test_timeout_fix.py
타임아웃 문제 해결 테스트

```bash
python tests/gui/test_timeout_fix.py
```

**검증 항목**:
- `sys.exit(0)` 추가 확인
- 2-4초 내 완료 확인
- 이모지 인코딩 확인

---

## 📊 테스트 결과 (results/)

모든 테스트 실행 결과가 저장됩니다.

**주요 파일**:
- `01_compatibility_check.txt` - 호환성 체크 결과
- `02_health_check.txt` - 서비스 상태 확인
- `03_model_compatibility.txt` - 모델 호환성
- `04_agent_test.txt` - Agent 테스트
- `05_groq_oss_test.txt` - Groq OSS 테스트
- `06_synthetic_data_validation.txt` - 합성 데이터 검증
- `07_position_parameters_success.md` - Position 파라미터 성공
- `08_model_display_and_16turns.md` - 모델 표시 및 16턴
- `09_interactive_gui_autoopen.md` - GUI 자동 열기
- `TEST_SUMMARY.md` - 전체 테스트 요약

---

## 🚀 빠른 시작

### 모든 테스트 실행
```bash
# 프로젝트 루트에서
cd /Users/shkim5/Documents/cadai

# 단위 테스트
python tests/unit/test_freecad_tools.py
python tests/unit/test_mcp_server.py

# 통합 테스트
python tests/integration/test_agent.py
python tests/integration/test_complex_objects.py

# GUI 테스트
python tests/gui/test_interactive_gui.py
```

### 특정 기능 테스트
```bash
# Agent 기본 기능
python tests/integration/test_agent_simple.py

# 복잡한 객체
python tests/integration/test_complex_objects.py

# Groq 모델
python tests/integration/test_with_groq_oss.py
```

---

## ⚙️ 테스트 설정

### 환경 변수
테스트 실행 전 `.env` 파일 설정:

```bash
LITELLM_BASE_URL=http://localhost:4000
LITELLM_API_KEY=sk-1234
OPENPIPE_API_KEY=your_key_here
GROQ_API_KEY=your_groq_key_here  # Groq 테스트용
```

### 서비스 시작
일부 테스트는 서비스가 필요합니다:

```bash
# Docker 서비스 시작
docker-compose up -d

# 또는 웹 서버
./start_server.sh
```

---

## 📝 테스트 작성 가이드

### 단위 테스트
```python
# tests/unit/test_new_feature.py
def test_new_function():
    result = new_function()
    assert result is not None
    assert result['success'] == True
```

### 통합 테스트
```python
# tests/integration/test_new_integration.py
from src.agent import ToolCallingAgent

def test_agent_with_new_tool():
    agent = ToolCallingAgent()
    result = agent.run("새 도구를 사용해줘")
    assert result['success'] == True
```

### GUI 테스트
```python
# tests/gui/test_new_gui_feature.py
import subprocess

def test_gui_feature():
    # GUI 기능 테스트
    process = subprocess.Popen([...])
    # 검증
    assert process.returncode == 0
```

---

## 📖 관련 문서

- **프로젝트 상태**: `../docs/PROJECT_STATUS.md`
- **문제 해결**: `../docs/TROUBLESHOOTING.md`
- **구현 요약**: `../docs/IMPLEMENTATION_SUMMARY.md`

---

## 💡 팁

### 테스트 빠르게 실행
```bash
# 시뮬레이션 모드 사용 (FreeCAD 없이)
FREECAD_SIMULATION=1 python tests/unit/test_freecad_tools.py
```

### 특정 테스트만 실행
```python
# pytest 사용 (설치 필요)
pytest tests/integration/test_agent.py::test_specific_function
```

### 로그 확인
```bash
# 상세 로그로 실행
python tests/integration/test_agent.py --verbose
```

---

**업데이트**: 2025-10-26


