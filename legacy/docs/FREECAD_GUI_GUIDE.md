# FreeCAD GUI 사용 가이드 🎨

**작성일**: 2025-10-26  
**목적**: Agent로 생성한 CAD 모델을 FreeCAD GUI로 시각적으로 확인

## ✅ 설정 완료!

FreeCAD가 이미 설치되어 있으며, 테스트 파일들이 성공적으로 생성되었습니다!

### 설치 정보
- **FreeCAD 경로**: `/opt/homebrew/bin/freecad`
- **설치 방법**: Homebrew
- **버전**: FreeCAD 1.0.2

### 생성된 테스트 파일들
```
-rw-r--r--  simple_box.FCStd           (2.4 KB) - 간단한 박스
-rw-r--r--  positioned_objects.FCStd   (3.7 KB) - 실린더, 구, 박스
-rw-r--r--  simple_chair.FCStd         (6.8 KB) - 의자 (6 부품)
```

## 🚀 FreeCAD GUI로 파일 열기

### 방법 1: 명령어로 열기 (추천)
```bash
# 프로젝트 디렉토리에서
cd /Users/shkim5/Documents/cadai

# 간단한 박스 보기
/opt/homebrew/bin/freecad simple_box.FCStd

# 여러 객체 보기
/opt/homebrew/bin/freecad positioned_objects.FCStd

# 의자 보기
/opt/homebrew/bin/freecad simple_chair.FCStd
```

### 방법 2: 간편 스크립트 사용
```bash
# 새로운 모델 자동 생성 + GUI로 열기
python3 create_and_view_freecad.py
```

이 스크립트는 자동으로:
1. 3가지 테스트 모델 생성
2. .FCStd 파일로 저장
3. FreeCAD GUI로 첫 번째 파일 열기

## 🎨 FreeCAD GUI 사용 팁

### 기본 조작
| 동작 | 방법 |
|------|------|
| **회전** | 마우스 가운데 버튼 드래그 |
| **확대/축소** | 마우스 휠 |
| **이동** | Shift + 마우스 가운데 드래그 |
| **전체 보기** | V, F 또는 View > Fit All |

### 유용한 단축키
- `V, F`: Fit All (전체 보기)
- `V, 1`: 정면 보기
- `V, 2`: 후면 보기
- `V, 3`: 왼쪽 보기
- `V, 4`: 오른쪽 보기
- `V, 5`: 위쪽 보기
- `V, 6`: 아래쪽 보기

### 뷰 설정
```
View > Std View Menu > Isometric
View > Std View Menu > Orthographic
View > Draw Style > Flat Lines (와이어프레임)
View > Draw Style > Shaded (쉐이딩)
```

### 내보내기
```
File > Export
  - STEP (.step, .stp): 다른 CAD 프로그램과 호환
  - STL (.stl): 3D 프린팅용
  - OBJ (.obj): 3D 모델링 프로그램용
  - SVG (.svg): 2D 벡터 그래픽
```

## 🤖 Agent와 FreeCAD 연동

### 현재 상태
현재 Agent는 **시뮬레이션 모드**로 작동합니다:
- ✅ 모든 도구 호출 가능
- ✅ 파라미터 검증
- ⚠️ 실제 FreeCAD 파일은 생성하지 않음

### 실제 파일 생성 방법

#### 방법 1: Python 스크립트 사용 (추천)
`create_and_view_freecad.py` 스크립트를 사용하면 Agent 없이도 FreeCAD 파일을 생성할 수 있습니다.

```python
# 간단한 사용
python3 create_and_view_freecad.py

# 생성되는 모델:
# 1. simple_box.FCStd - 10x10x10 박스
# 2. positioned_objects.FCStd - 3개 객체
# 3. simple_chair.FCStd - 의자 (6 부품)
```

#### 방법 2: Agent 출력을 FreeCAD 스크립트로 변환

Agent가 생성한 명령어들을 FreeCAD Python 스크립트로 변환하여 실행할 수 있습니다.

**예시**: Agent 실행
```python
from src.agent import ToolCallingAgent

agent = ToolCallingAgent()
result = agent.run("10x10x10 박스를 만들어줘")
```

**변환**: FreeCAD 스크립트
```python
# freecad_script.py
import FreeCAD
import Part

doc = FreeCAD.newDocument("MyDesign")

box = doc.addObject("Part::Box", "Box")
box.Length = 10
box.Width = 10
box.Height = 10

doc.recompute()
doc.saveAs("output.FCStd")
```

**실행**:
```bash
/opt/homebrew/bin/freecad -c freecad_script.py
/opt/homebrew/bin/freecad output.FCStd
```

## 📊 테스트 결과

### 테스트 1: 간단한 박스 ✅
```
파일: simple_box.FCStd
객체: 10x10x10 박스 1개
크기: 2.4 KB
```

### 테스트 2: 위치가 있는 객체들 ✅
```
파일: positioned_objects.FCStd
객체:
  - 실린더 (반지름 5, 높이 20) at (0, 0, 0)
  - 구 (반지름 8) at (25, 0, 10)
  - 박스 (15x10x5) at (50, 0, 0)
크기: 3.7 KB
```

### 테스트 3: 간단한 의자 ✅
```
파일: simple_chair.FCStd
객체: 6 부품
  - 좌판 (40x40x5) at (0, 0, 45)
  - 다리1 (5x5x45) at (0, 0, 0)
  - 다리2 (5x5x45) at (35, 0, 0)
  - 다리3 (5x5x45) at (0, 35, 0)
  - 다리4 (5x5x45) at (35, 35, 0)
  - 등받이 (40x5x50) at (0, 35, 45)
크기: 6.8 KB
```

## 🛠️ 문제 해결

### 문제: FreeCAD를 찾을 수 없음
```bash
# 설치 확인
which freecad

# 없다면 설치
brew install freecad
```

### 문제: GUI가 열리지 않음
```bash
# 직접 열기
/opt/homebrew/bin/freecad simple_chair.FCStd

# 또는 절대 경로 사용
/opt/homebrew/bin/freecad /Users/shkim5/Documents/cadai/simple_chair.FCStd
```

### 문제: 파일이 생성되지 않음
```bash
# 스크립트를 다시 실행
python3 create_and_view_freecad.py

# 권한 확인
ls -la *.FCStd
```

### 문제: 3DconnexionNavlib 오류
```
Error: Failed to open library "/Library/Frameworks/3DconnexionNavlib.framework/3DconnexionNavlib"
```

이것은 3D 마우스 라이브러리 관련 경고입니다. **무시해도 됩니다**. FreeCAD는 정상적으로 작동합니다.

## 🚀 다음 단계

### 1. 더 복잡한 모델 만들기
```python
# create_and_view_freecad.py를 수정하여 새로운 모델 추가
{
    "name": "table",
    "description": "테이블",
    "objects": [
        # 상판
        {
            "type": "box",
            "name": "Top",
            "params": {
                "length": 80,
                "width": 60,
                "height": 5,
                "position": [0, 0, 70]
            }
        },
        # 다리 4개
        # ...
    ]
}
```

### 2. Agent 통합 개선
현재 시뮬레이션 모드를 실제 FreeCAD 연동으로 업그레이드:
- Agent가 직접 FreeCAD Python 스크립트 생성
- `freecad -c` 명령어로 스크립트 실행
- 생성된 .FCStd 파일 자동으로 GUI에서 열기

### 3. 고급 기능
- Boolean 연산 (합치기, 빼기, 교집합)
- Fillet (모서리 둥글게)
- Chamfer (모서리 깎기)
- Array (배열 복사)
- Sketch 기반 모델링

## 📁 관련 파일

### 스크립트
- `create_and_view_freecad.py` - FreeCAD 파일 생성 및 GUI 열기
- `setup_freecad_gui.py` - Agent와 FreeCAD 통합 (개발 중)

### 문서
- `FREECAD_SETUP.md` - FreeCAD 설치 및 설정 가이드
- `FREECAD_GUI_GUIDE.md` - 이 문서
- `test_results/07_position_parameters_success.md` - 위치 파라미터 구현

### 생성된 모델
- `simple_box.FCStd`
- `positioned_objects.FCStd`
- `simple_chair.FCStd`

## 💡 사용 예시

### 예시 1: 간단한 객체 확인
```bash
cd /Users/shkim5/Documents/cadai
python3 create_and_view_freecad.py
# FreeCAD GUI가 자동으로 열립니다
```

### 예시 2: 특정 파일 열기
```bash
/opt/homebrew/bin/freecad simple_chair.FCStd
```

### 예시 3: 여러 파일 비교
```bash
# 터미널 창 1
/opt/homebrew/bin/freecad simple_box.FCStd

# 터미널 창 2
/opt/homebrew/bin/freecad simple_chair.FCStd
```

### 예시 4: 파일 내보내기 (GUI에서)
1. FreeCAD에서 파일 열기
2. File > Export
3. 형식 선택 (STEP, STL, OBJ 등)
4. 저장

## 🎉 완료!

FreeCAD GUI 설정이 완료되었습니다! 

이제 Agent로 생성한 모델을 시각적으로 확인할 수 있습니다. 🏗️

### 빠른 시작
```bash
# 1. 모델 생성
cd /Users/shkim5/Documents/cadai
python3 create_and_view_freecad.py

# 2. FreeCAD GUI가 자동으로 열립니다

# 3. 다른 파일들도 확인
/opt/homebrew/bin/freecad positioned_objects.FCStd
/opt/homebrew/bin/freecad simple_chair.FCStd
```

---

**설정 완료**: 2025-10-26  
**테스트**: 성공 ✅  
**FreeCAD GUI**: 작동 확인 ✅

