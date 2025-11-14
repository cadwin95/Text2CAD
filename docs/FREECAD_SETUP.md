# FreeCAD 설치 및 연동 가이드

## 1. FreeCAD 설치

### macOS
```bash
# Homebrew로 설치
brew install --cask freecad

# 또는 공식 사이트에서 다운로드
# https://www.freecad.org/downloads.php
```

설치 후 확인:
```bash
# FreeCAD 실행
open /Applications/FreeCAD.app

# Python 경로 확인
/Applications/FreeCAD.app/Contents/Resources/bin/python --version
```

## 2. Python 환경 설정

### 방법 A: FreeCAD의 Python 사용 (권장)

FreeCAD는 자체 Python 환경이 있습니다:

```bash
# FreeCAD Python 경로
FREECAD_PYTHON="/Applications/FreeCAD.app/Contents/Resources/bin/python"

# Agent 실행
$FREECAD_PYTHON test_with_freecad_gui.py
```

### 방법 B: 시스템 Python에서 FreeCAD 모듈 임포트

FreeCAD 모듈을 시스템 Python에서 사용:

```python
import sys
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD
import Part
```

## 3. GUI로 모델 보기

### 3.1 FreeCAD GUI 실행

```python
#!/usr/bin/env python3
"""
FreeCAD GUI에서 Agent로 생성한 모델 보기
"""

import sys
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')

import FreeCAD
import FreeCADGui
import Part

# 새 문서 생성
doc = FreeCAD.newDocument("AgentTest")

# Agent를 통해 객체 생성 (시뮬레이션 아님)
from src.freecad_tools import create_box, create_cylinder

# 박스 생성
result = create_box(10, 10, 10, "MyBox")
print(f"박스 생성: {result}")

# 실린더 생성
result = create_cylinder(5, 20, "MyCylinder")
print(f"실린더 생성: {result}")

# FreeCAD GUI 실행
FreeCADGui.showMainWindow()
FreeCADGui.exec_loop()
```

### 3.2 FreeCAD에서 직접 열기

Agent로 생성한 `.FCStd` 파일을 FreeCAD에서 열기:

```bash
# Agent로 모델 생성 및 저장
python3 create_and_save.py

# FreeCAD에서 열기
open -a FreeCAD output/model.FCStd
```

## 4. Headless 모드 (서버/CLI)

GUI 없이 명령줄에서만 사용:

```python
import sys
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')

import FreeCAD
import Part

# 새 문서 생성
doc = FreeCAD.newDocument("Headless")

# 박스 생성
box = doc.addObject("Part::Box", "Box")
box.Length = 10
box.Width = 10
box.Height = 10

# 문서 저장
doc.saveAs("output/headless_model.FCStd")

print("모델 저장 완료!")
```

## 5. 이미지 내보내기

### 5.1 GUI에서 스크린샷

```python
import FreeCADGui

# 활성 뷰 가져오기
view = FreeCADGui.activeDocument().activeView()

# 이미지 저장 (800x600, 흰 배경)
view.saveImage('output/model.png', 800, 600, 'White')
```

### 5.2 Agent의 export_image 도구 사용

```python
from src.agent import ToolCallingAgent

agent = ToolCallingAgent()
agent.run("10x10x10 박스를 만들고 model.png로 이미지를 저장해줘")
```

## 6. Agent와 실제 FreeCAD 통합

### 6.1 환경 변수 설정

```bash
# .env 파일에 추가
FREECAD_PATH=/Applications/FreeCAD.app/Contents/Resources
FREECAD_PYTHON=/Applications/FreeCAD.app/Contents/Resources/bin/python
```

### 6.2 Agent 실행

```python
from src.agent import ToolCallingAgent

# Agent 초기화
agent = ToolCallingAgent(verbose=True)

# 명령 실행 (이제 실제 FreeCAD로 작동)
result = agent.run("""
    10mm x 10mm x 10mm 박스를 만들고,
    반지름 5mm인 구를 추가한 다음,
    model.FCStd로 저장하고
    model.png로 이미지도 저장해줘
""")

print(result)
```

## 7. 시각화 예시

### 실제 생성되는 파일들:

```
output/
├── model.FCStd          # FreeCAD 문서 (더블클릭으로 열림)
├── model.png            # 3D 뷰 스크린샷
├── model.stl            # 3D 프린팅용 (추가 구현 필요)
└── model.step           # CAD 교환용 (추가 구현 필요)
```

### FreeCAD에서 보는 화면:

```
┌─────────────────────────────────────┐
│  FreeCAD - AgentTest                │
├─────────────────────────────────────┤
│  Tree View    │   3D View           │
│  ├─ Box       │   ╔═══╗             │
│  │  ├─ Length │   ║   ║             │
│  │  ├─ Width  │   ║   ║  ← 박스     │
│  │  └─ Height │   ╚═══╝             │
│  └─ Cylinder  │     ◯               │
│     ├─ Radius │    ║ ║  ← 실린더   │
│     └─ Height │    ║ ║              │
│               │    ╚═╝              │
└─────────────────────────────────────┘
```

## 8. 트러블슈팅

### 문제: "No module named 'FreeCAD'"

**해결책 1**: FreeCAD의 Python 사용
```bash
/Applications/FreeCAD.app/Contents/Resources/bin/python your_script.py
```

**해결책 2**: sys.path에 추가
```python
import sys
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD
```

### 문제: GUI가 실행되지 않음

**해결책**: Headless 모드 사용 또는 X11 설정
```bash
# macOS에서 XQuartz 필요할 수 있음
brew install --cask xquartz
```

### 문제: 권한 오류

**해결책**: FreeCAD 앱 권한 확인
```bash
chmod +x /Applications/FreeCAD.app/Contents/Resources/bin/python
```

## 9. 다음 단계

### 9.1 기본 모델링
- ✅ 박스, 실린더, 구, 원뿔 생성
- 🔲 Boolean 연산 (합집합, 차집합)
- 🔲 Fillet, Chamfer 적용

### 9.2 고급 기능
- 🔲 스케치 생성
- 🔲 Extrude, Revolve
- 🔲 어셈블리

### 9.3 내보내기 확장
- 🔲 STL 내보내기 (3D 프린팅)
- 🔲 STEP 내보내기 (CAD 교환)
- 🔲 PDF 도면 생성

## 10. 유용한 링크

- [FreeCAD 공식 사이트](https://www.freecad.org/)
- [FreeCAD Python API 문서](https://wiki.freecad.org/Python_scripting_tutorial)
- [FreeCAD Wiki](https://wiki.freecad.org/)
- [FreeCAD Forum](https://forum.freecad.org/)

---

**참고**: 현재 시뮬레이션 모드로도 Agent 개발/테스트/학습이 가능합니다. 
실제 FreeCAD 연동은 프로덕션 배포 시에만 필요합니다.

