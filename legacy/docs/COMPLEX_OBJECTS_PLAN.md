# 복잡한 객체 생성 계획 (의자, 사다리 등)

## 문제점
현재 구조로는 기본 도형만 생성 가능하고, 모든 객체가 원점(0,0,0)에 생성됨

## 해결 방안

### 방법 1: 위치/회전 파라미터 추가 ⭐ (추천)

#### 1.1 기존 도구 확장

```python
# src/freecad_tools/primitives.py

def create_box_at_position(
    length: float,
    width: float, 
    height: float,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    rotation: float = 0,
    name: str = "Box"
) -> Dict:
    """위치와 회전을 지정하여 박스 생성"""
    
    doc = FreeCAD.activeDocument() or FreeCAD.newDocument()
    box = doc.addObject("Part::Box", name)
    box.Length = length
    box.Width = width
    box.Height = height
    
    # 위치 설정
    box.Placement.Base = FreeCAD.Vector(x, y, z)
    
    # 회전 설정 (Z축 기준)
    if rotation != 0:
        box.Placement.Rotation = FreeCAD.Rotation(
            FreeCAD.Vector(0, 0, 1), rotation
        )
    
    doc.recompute()
    return {"success": True, "object_name": name}
```

#### 1.2 Agent 사용 예시

```
사용자: "의자를 만들어줘"

Agent:
1. create_box(40, 40, 5, x=0, y=0, z=45, name="Seat")     # 좌판
2. create_box(5, 5, 45, x=0, y=0, z=0, name="Leg1")       # 다리1
3. create_box(5, 5, 45, x=35, y=0, z=0, name="Leg2")      # 다리2
4. create_box(5, 5, 45, x=0, y=35, z=0, name="Leg3")      # 다리3
5. create_box(5, 5, 45, x=35, y=35, z=0, name="Leg4")     # 다리4
6. create_box(40, 5, 50, x=0, y=0, z=45, name="Back")     # 등받이
7. finish("의자가 완성되었습니다")
```

### 방법 2: 복합 객체 템플릿 추가 ⚡ (빠른 결과)

#### 2.1 고수준 도구 추가

```python
# src/freecad_tools/complex_objects.py

def create_chair(
    width: float = 40,
    depth: float = 40,
    height: float = 45,
    back_height: float = 50,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str = "Chair"
) -> Dict:
    """의자 생성 (좌판 + 4개 다리 + 등받이)"""
    
    doc = FreeCAD.activeDocument() or FreeCAD.newDocument()
    
    # 그룹 생성
    chair_group = doc.addObject("App::DocumentObjectGroup", name)
    
    # 좌판
    seat = doc.addObject("Part::Box", f"{name}_Seat")
    seat.Length = width
    seat.Width = depth
    seat.Height = 5
    seat.Placement.Base = FreeCAD.Vector(x, y, z + height)
    chair_group.addObject(seat)
    
    # 다리 4개
    leg_height = height
    leg_size = 5
    leg_positions = [
        (x, y, z),                           # 앞 왼쪽
        (x + width - leg_size, y, z),        # 앞 오른쪽
        (x, y + depth - leg_size, z),        # 뒤 왼쪽
        (x + width - leg_size, y + depth - leg_size, z)  # 뒤 오른쪽
    ]
    
    for i, (lx, ly, lz) in enumerate(leg_positions):
        leg = doc.addObject("Part::Box", f"{name}_Leg{i+1}")
        leg.Length = leg_size
        leg.Width = leg_size
        leg.Height = leg_height
        leg.Placement.Base = FreeCAD.Vector(lx, ly, lz)
        chair_group.addObject(leg)
    
    # 등받이
    back = doc.addObject("Part::Box", f"{name}_Back")
    back.Length = width
    back.Width = 5
    back.Height = back_height
    back.Placement.Base = FreeCAD.Vector(x, y + depth - 5, z + height)
    chair_group.addObject(back)
    
    doc.recompute()
    
    return {
        "success": True,
        "object_name": name,
        "type": "Chair",
        "components": 6  # 좌판 + 다리4개 + 등받이
    }


def create_ladder(
    width: float = 40,
    height: float = 200,
    steps: int = 5,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str = "Ladder"
) -> Dict:
    """사다리 생성"""
    
    doc = FreeCAD.activeDocument() or FreeCAD.newDocument()
    
    # 그룹 생성
    ladder_group = doc.addObject("App::DocumentObjectGroup", name)
    
    # 양쪽 기둥
    pole_width = 5
    pole_depth = 5
    
    # 왼쪽 기둥
    left_pole = doc.addObject("Part::Box", f"{name}_LeftPole")
    left_pole.Length = pole_width
    left_pole.Width = pole_depth
    left_pole.Height = height
    left_pole.Placement.Base = FreeCAD.Vector(x, y, z)
    ladder_group.addObject(left_pole)
    
    # 오른쪽 기둥
    right_pole = doc.addObject("Part::Box", f"{name}_RightPole")
    right_pole.Length = pole_width
    right_pole.Width = pole_depth
    right_pole.Height = height
    right_pole.Placement.Base = FreeCAD.Vector(x + width - pole_width, y, z)
    ladder_group.addObject(right_pole)
    
    # 발판들
    step_height = 5
    step_spacing = (height - step_height) / (steps + 1)
    
    for i in range(steps):
        step = doc.addObject("Part::Box", f"{name}_Step{i+1}")
        step.Length = width
        step.Width = pole_depth
        step.Height = step_height
        step_z = z + step_spacing * (i + 1)
        step.Placement.Base = FreeCAD.Vector(x, y, step_z)
        ladder_group.addObject(step)
    
    doc.recompute()
    
    return {
        "success": True,
        "object_name": name,
        "type": "Ladder",
        "components": 2 + steps  # 기둥2개 + 발판들
    }
```

#### 2.2 MCP 서버에 추가

```python
# src/mcp_server/server.py

from ..freecad_tools.complex_objects import create_chair, create_ladder

@mcp.tool()
def freecad_create_chair(
    width: float = 40,
    depth: float = 40,
    height: float = 45,
    back_height: float = 50,
    name: str = "Chair"
) -> str:
    """FreeCAD에서 의자를 생성합니다"""
    result = create_chair(width, depth, height, back_height, name=name)
    if result["success"]:
        return f"✓ 의자 '{result['object_name']}'를 생성했습니다. (구성요소: {result['components']}개)"
    else:
        return f"✗ 의자 생성 실패"

@mcp.tool()
def freecad_create_ladder(
    width: float = 40,
    height: float = 200,
    steps: int = 5,
    name: str = "Ladder"
) -> str:
    """FreeCAD에서 사다리를 생성합니다"""
    result = create_ladder(width, height, steps, name=name)
    if result["success"]:
        return f"✓ 사다리 '{result['object_name']}'를 생성했습니다. (발판: {steps}개)"
    else:
        return f"✗ 사다리 생성 실패"
```

#### 2.3 사용 예시

```python
from src.agent import ToolCallingAgent

agent = ToolCallingAgent()

# 의자 생성
agent.run("40x40 크기의 의자를 만들어줘")

# 사다리 생성  
agent.run("높이 200mm이고 발판이 5개인 사다리를 만들어줘")

# 커스터마이징
agent.run("너비 50, 깊이 45, 높이 50, 등받이 높이 60인 의자를 만들어줘")
```

### 방법 3: Agent가 순차적으로 조합 🤖 (고급)

#### 3.1 시스템 프롬프트 추가

```python
SYSTEM_PROMPT = """
당신은 FreeCAD 전문가입니다. 복잡한 객체를 만들 때는 기본 도형들을 
위치를 지정하여 조합해야 합니다.

예시 - 의자 만들기:
1. 좌판: create_box(40, 40, 5) at (0, 0, 45)
2. 다리1: create_box(5, 5, 45) at (0, 0, 0)
3. 다리2: create_box(5, 5, 45) at (35, 0, 0)
4. 다리3: create_box(5, 5, 45) at (0, 35, 0)
5. 다리4: create_box(5, 5, 45) at (35, 35, 0)
6. 등받이: create_box(40, 5, 50) at (0, 35, 45)
7. finish("의자 완성")

항상 finish 도구로 작업을 완료하세요.
"""
```

## 구현 우선순위

### Phase 1: 위치 파라미터 추가 (1-2시간)
- ✅ `x, y, z` 파라미터 추가
- ✅ `rotation` 파라미터 추가
- ✅ MCP 도구 업데이트
- ✅ 학습 데이터 생성

### Phase 2: 복합 객체 템플릿 (2-3시간)
- ✅ `create_chair` 구현
- ✅ `create_ladder` 구현
- ✅ `create_table` 구현
- ✅ MCP에 추가
- ✅ 학습 데이터 생성

### Phase 3: Boolean 연산 (3-4시간)
- ✅ `union` (합치기)
- ✅ `cut` (빼기)
- ✅ `intersect` (교집합)

### Phase 4: 고급 기능 (5+시간)
- ✅ 스케치 기반 모델링
- ✅ Extrude, Revolve
- ✅ Fillet, Chamfer

## 빠른 프로토타입 (방법 2 추천)

**장점:**
- ✅ 빠르게 결과 확인 가능
- ✅ 사용자 친화적
- ✅ 학습 데이터 생성 쉬움

**단점:**
- ❌ 새 객체마다 함수 추가 필요
- ❌ 유연성 제한

## 확장 가능한 방법 (방법 1 추천)

**장점:**
- ✅ 무한한 조합 가능
- ✅ Agent가 창의적으로 생성
- ✅ 새 객체 타입 추가 불필요

**단점:**
- ❌ Agent 학습 필요
- ❌ 복잡한 명령어 처리

## 다음 단계

어떤 방법으로 진행하시겠어요?

1. **방법 1 (위치 파라미터)** - 가장 유연함, Agent가 조합 학습
2. **방법 2 (템플릿)** - 빠른 결과, 즉시 사용 가능
3. **둘 다** - 방법 2로 시작 → 방법 1로 확장

추천: **방법 2 → 방법 1 순서로 진행**
- 먼저 의자/사다리 템플릿으로 빠르게 결과 확인
- 그 다음 위치 파라미터 추가하여 확장성 확보

