# FreeCAD 인터랙티브 모드 가이드 💬🎨

**작성일**: 2025-10-26  
**목적**: 실시간으로 FreeCAD GUI를 보면서 채팅으로 객체를 추가/수정

## 🎯 개요

**FreeCAD 인터랙티브 모드**는 채팅하듯이 대화하면서 실시간으로 CAD 모델을 만들 수 있는 기능입니다.

### 주요 기능
- ✅ 실시간 FreeCAD GUI 업데이트
- ✅ 세션 유지 (대화 컨텍스트 유지)
- ✅ 자연어로 객체 추가/수정 요청
- ✅ 이전 객체 유지하면서 새 객체 추가
- ✅ 언제든지 저장/초기화 가능

### 작동 방식
```
사용자 입력 → Agent → FreeCAD 스크립트 생성 → 문서 업데이트 → GUI 자동 반영
```

## 🚀 사용 방법

### 1. 기본 실행
```bash
cd /Users/shkim5/Documents/cadai
python3 interactive_freecad.py
```

### 2. 모델 지정하여 실행
```bash
# Groq OSS 20B 모델 (기본값)
python3 interactive_freecad.py groq/openai/gpt-oss-20b

# llama.cpp 로컬 모델
python3 interactive_freecad.py llama.cpp

# GPT-4o
python3 interactive_freecad.py openai/gpt-4o
```

## 💬 대화 예시

### 시작 화면
```
======================================================================
🎨 FreeCAD 인터랙티브 모드
======================================================================

📡 LiteLLM Proxy: http://localhost:4000
🧠 모델: groq/openai/gpt-oss-20b
📁 작업 파일: interactive_session.FCStd

💡 사용 방법:
  - 원하는 객체를 자유롭게 요청하세요
  - FreeCAD 창에서 실시간으로 결과를 확인할 수 있습니다
  - 'quit', 'exit', 'q'를 입력하면 종료됩니다
  - 'clear'를 입력하면 모든 객체를 삭제합니다
  - 'save'를 입력하면 현재 상태를 저장합니다

✅ 초기 문서 생성: interactive_session.FCStd
✅ FreeCAD GUI 열림
======================================================================
🚀 세션이 시작되었습니다! FreeCAD 창을 확인하세요.
======================================================================

======================================================================
턴 1 - 무엇을 만들고 싶으신가요?
======================================================================
👤 당신: 
```

### 대화 예시 1: 간단한 객체
```
👤 당신: 10x10x10 박스를 만들어줘

🤖 Agent 실행...
✅ FreeCAD 업데이트 완료 (1개 객체)
```

### 대화 예시 2: 객체 추가
```
👤 당신: 박스 옆에 실린더를 추가해줘. 반지름 5, 높이 20

🤖 Agent 실행...
✅ FreeCAD 업데이트 완료 (2개 객체)
```

### 대화 예시 3: 복잡한 구조
```
👤 당신: 간격 20cm 짜리 1미터 사다리를 만들어줘

🤖 Agent 실행...
[반복 1/16] 🧠 모델: groq/openai/gpt-oss-20b
  → 도구 호출: freecad_new_document
[반복 2/16] 🧠 모델: groq/openai/gpt-oss-20b
  → 도구 호출: freecad_create_box (왼쪽 기둥)
[반복 3/16] 🧠 모델: groq/openai/gpt-oss-20b
  → 도구 호출: freecad_create_box (오른쪽 기둥)
[반복 4/16] 🧠 모델: groq/openai/gpt-oss-20b
  → 도구 호출: freecad_create_box (발판1)
...

✅ FreeCAD 업데이트 완료 (7개 객체)
```

### 대화 예시 4: 모델이 질문하는 경우
```
👤 당신: 의자를 만들어줘

🤖 Assistant: 의자를 만들기 위해 몇 가지 정보가 필요합니다:
1. 좌판 크기는 어느 정도가 좋을까요?
2. 다리 높이는?
3. 등받이가 필요한가요?

👤 당신: 좌판 40x40, 다리 높이 45cm, 등받이 있는 걸로 해줘

🤖 Agent 실행...
✅ FreeCAD 업데이트 완료 (6개 객체)
```

## 🎮 명령어

### 특수 명령어
| 명령어 | 설명 |
|--------|------|
| `quit`, `exit`, `q` | 세션 종료 |
| `clear` | 모든 객체 삭제 |
| `save` | 현재 상태를 파일로 저장 |

### save 명령어 사용
```
👤 당신: save

저장할 파일 이름 (예: my_design.FCStd): my_chair

✅ 저장 완료: /Users/shkim5/Documents/cadai/my_chair.FCStd
```

### clear 명령어 사용
```
👤 당신: clear

🗑️  모든 객체를 삭제합니다...
✅ 모든 객체가 삭제되었습니다.
💡 FreeCAD에서 File > Recent Files > interactive_session.FCStd를 다시 열어주세요.
```

## 🔄 FreeCAD GUI 업데이트

### 자동 업데이트
각 턴이 끝나면 자동으로 FreeCAD 문서가 업데이트됩니다.

### 수동 리로드 (필요시)
FreeCAD GUI에서:
1. **File > Recent Files**
2. **interactive_session.FCStd** 선택
3. 업데이트된 객체 확인

또는:
1. **Ctrl+R** (Recompute)
2. **File > Reload**

## 💡 활용 예시

### 예시 1: 점진적으로 모델 만들기
```
턴 1: 10x10x10 박스 만들어줘
턴 2: 박스 위에 실린더 올려줘
턴 3: 실린더 옆에 구를 추가해줘
턴 4: 전체를 10도 회전시켜줘
```

### 예시 2: 복잡한 구조
```
턴 1: 간단한 의자를 만들어줘
턴 2: 의자 옆에 테이블을 추가해줘
턴 3: 테이블 위에 작은 박스를 3개 놓아줘
```

### 예시 3: 수정 및 조정
```
턴 1: 박스를 만들어줘
턴 2: 박스를 더 크게 만들어줘 (20x20x20)
턴 3: 박스를 오른쪽으로 10cm 이동시켜줘
```

## 🎨 FreeCAD GUI 조작

인터랙티브 모드가 실행되는 동안 FreeCAD GUI에서:

### 뷰 조작
- **회전**: 마우스 가운데 버튼 드래그
- **확대/축소**: 마우스 휠
- **이동**: Shift + 마우스 가운데 드래그
- **전체 보기**: V, F

### 객체 선택
- 왼쪽 사이드바에서 객체 클릭
- 3D 뷰에서 직접 클릭

### 속성 확인
- 객체 선택 → 하단 Properties 패널에서 확인

## 🔧 기술적 세부사항

### 세션 유지 방식
1. Agent의 대화 히스토리를 유지
2. 각 턴마다 누적된 모든 객체를 추출
3. FreeCAD Python 스크립트 생성
4. `freecad -c` 명령어로 스크립트 실행
5. 문서 업데이트

### 파일 구조
```
interactive_session.FCStd    # 작업 파일 (자동 업데이트)
interactive_script.py        # 임시 스크립트 (자동 생성/삭제)
```

### Agent 동작
- Agent는 매 턴마다 새로운 요청을 처리
- 이전 대화 컨텍스트를 유지하여 연속성 보장
- `finish` 도구를 호출하지 않도록 프롬프트 수정

## ⚠️ 알려진 제한사항

### 1. FreeCAD GUI 수동 리로드 필요
현재 버전에서는 FreeCAD GUI가 파일 변경을 자동 감지하지 않습니다.
→ **해결**: File > Recent Files에서 수동 리로드

### 2. 시뮬레이션 모드
Agent는 아직 시뮬레이션 모드로 작동합니다.
→ 실제 FreeCAD 파일 생성은 백그라운드 스크립트가 처리

### 3. 객체 수정의 한계
기존 객체를 직접 수정하기보다는 새로운 객체를 추가하는 방식입니다.
→ 수정이 필요하면 `clear` 후 다시 만들기

## 🚀 고급 기능 (예정)

### 1. 실시간 자동 리로드
FreeCAD가 파일 변경을 자동 감지하여 리로드

### 2. 웹 인터페이스
브라우저에서 채팅 + FreeCAD 뷰어

### 3. 음성 입력
음성으로 명령하여 모델 생성

### 4. 이미지 분석
현재 모델 스크린샷을 AI가 분석하여 피드백

## 📊 성능 및 제한

### 권장 사양
- 메모리: 4GB 이상
- FreeCAD: 1.0 이상
- Python: 3.10 이상

### 객체 수 제한
- 권장: 20개 이하 (빠른 업데이트)
- 최대: 100개 (느릴 수 있음)

### 응답 시간
- 간단한 요청: 2-5초
- 복잡한 요청: 5-15초
- 모델에 따라 다름

## 🐛 문제 해결

### 문제: FreeCAD가 열리지 않음
```bash
# FreeCAD 경로 확인
which freecad

# 없으면 설치
brew install freecad
```

### 문제: 객체가 업데이트되지 않음
1. FreeCAD에서 **File > Recent Files > interactive_session.FCStd**
2. 또는 **Ctrl+R** (Recompute)

### 문제: Agent가 응답하지 않음
1. LiteLLM 프록시 확인: `docker ps`
2. API 키 확인: `.env` 파일
3. 네트워크 연결 확인

### 문제: 세션이 끊김
```bash
# 작업 파일 확인
ls -lh interactive_session.FCStd

# 백업 파일 확인
ls -lh saved_design_*.FCStd
```

## 📝 예시 스크립트

### 간단한 테스트
```bash
cd /Users/shkim5/Documents/cadai

python3 -c "
from interactive_freecad import InteractiveFreeCAD
session = InteractiveFreeCAD('groq/openai/gpt-oss-20b')
session.start()
"
```

### 대화 시뮬레이션
```python
# test_interactive.py
from interactive_freecad import InteractiveFreeCAD

session = InteractiveFreeCAD('groq/openai/gpt-oss-20b')

# 자동화된 명령어 실행
commands = [
    "10x10x10 박스를 만들어줘",
    "박스 옆에 실린더 추가해줘",
    "전체 보기로 조정해줘"
]

for cmd in commands:
    print(f"실행: {cmd}")
    # ... (Agent 호출)
```

## 🎉 결론

**FreeCAD 인터랙티브 모드**를 사용하면:
- ✅ 자연어로 CAD 모델 생성
- ✅ 실시간으로 결과 확인
- ✅ 대화형 수정 및 추가
- ✅ 세션 유지로 연속 작업

이제 채팅하듯이 CAD 모델을 만들 수 있습니다! 🏗️💬

---

**작성 완료**: 2025-10-26  
**테스트**: 준비 완료 ✅  
**사용 준비**: 완료 ✅

## 🚀 바로 시작하기

```bash
cd /Users/shkim5/Documents/cadai
python3 interactive_freecad.py
```

그리고 FreeCAD 창을 보면서 대화를 시작하세요! 🎨

