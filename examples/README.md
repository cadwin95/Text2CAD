# 💡 예제 디렉토리

FreeCAD Tool-Calling Agent의 예제 파일 및 데모 스크립트입니다.

---

## 📦 FreeCAD 모델 파일

실행 가능한 FreeCAD 모델 예제:

- **simple_box.FCStd** - 기본 박스 예제
- **simple_chair.FCStd** - 의자 모델 (복잡한 객체)
- **positioned_objects.FCStd** - 위치가 지정된 여러 객체
- **interactive_session.FCStd** - 인터랙티브 세션 결과
- **test_gui_autoopen.FCStd** - GUI 자동 열기 테스트

### 사용 방법
```bash
# FreeCAD GUI로 열기
freecad simple_chair.FCStd

# 또는 macOS
/opt/homebrew/bin/freecad simple_chair.FCStd
```

---

## 🐍 Python 스크립트

### interactive_freecad.py
**인터랙티브 FreeCAD 세션**

채팅으로 FreeCAD를 제어하고 GUI에서 실시간 확인:

```bash
python examples/interactive_freecad.py
```

**기능**:
- 연속 채팅 세션
- FreeCAD GUI 자동 업데이트
- macOS 포그라운드 활성화
- 세션 파일 자동 저장

**사용 예**:
```
사용자: 박스 3개 만들어줘
Agent: 박스 3개를 생성했습니다.
[FreeCAD GUI 자동 업데이트]

사용자: 실린더도 추가해줘
Agent: 실린더를 추가했습니다.
[FreeCAD GUI 다시 업데이트]
```

---

### create_and_view_freecad.py
**FreeCAD 모델 생성 및 GUI 자동 열기**

다양한 예제 모델을 생성하고 GUI로 확인:

```bash
python examples/create_and_view_freecad.py
```

**생성되는 모델**:
1. 단순 박스
2. 위치가 지정된 여러 객체
3. 의자 (복잡한 조립 객체)

---

### setup_freecad_gui.py
**FreeCAD GUI 환경 설정**

FreeCAD 설치 경로를 찾고 Python 경로를 설정:

```bash
python examples/setup_freecad_gui.py
```

**기능**:
- FreeCAD 자동 검색 (macOS, Linux)
- sys.path 설정
- FreeCAD import 검증

---

## 🚀 빠른 시작

### 1. 기본 예제 보기
```bash
# 간단한 박스
freecad examples/simple_box.FCStd
```

### 2. 복잡한 객체 보기
```bash
# 의자 모델
freecad examples/simple_chair.FCStd
```

### 3. 인터랙티브 모드 실행
```bash
# 채팅으로 제어
python examples/interactive_freecad.py
```

### 4. 예제 생성 및 확인
```bash
# 새 예제 생성
python examples/create_and_view_freecad.py
```

---

## 📖 관련 문서

- **인터랙티브 모드**: `../docs/INTERACTIVE_MODE_GUIDE.md`
- **FreeCAD GUI**: `../docs/FREECAD_GUI_GUIDE.md`
- **FreeCAD 설치**: `../docs/FREECAD_SETUP.md`
- **복잡한 객체**: `../docs/COMPLEX_OBJECTS_PLAN.md`

---

## 💡 팁

### FreeCAD 경로 찾기
```bash
# macOS
which freecad
# 일반적으로: /opt/homebrew/bin/freecad

# Linux
which freecad
# 일반적으로: /usr/bin/freecad
```

### 예제 수정하기
모든 예제 파일은 수정 가능합니다. FreeCAD에서 열어서 편집하세요!

### 새 예제 만들기
```python
from src.freecad_tools import create_box, new_document, save_document

# 새 문서
new_document("MyExample")

# 객체 생성
create_box(10, 10, 10, name="MyBox")

# 저장
save_document("examples/my_example.FCStd")
```

---

**업데이트**: 2025-10-26

