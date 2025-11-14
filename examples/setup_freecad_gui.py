#!/usr/bin/env python3
"""
FreeCAD GUI 설정 및 테스트 스크립트
Agent로 객체를 만들고 FreeCAD GUI로 확인합니다.
"""

import sys
import os
import subprocess
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import ToolCallingAgent

print("="*70)
print("🎨 FreeCAD GUI 설정 및 테스트")
print("="*70)
print()

# Step 1: FreeCAD 설치 확인
print("📋 Step 1: FreeCAD 설치 확인")
print("-"*70)

freecad_paths = [
    "/opt/homebrew/bin/freecad",
    "/usr/local/bin/freecad",
    "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD",
]

freecad_path = None
for path in freecad_paths:
    if os.path.exists(path):
        freecad_path = path
        print(f"✅ FreeCAD 발견: {path}")
        break

if not freecad_path:
    print("❌ FreeCAD를 찾을 수 없습니다.")
    print()
    print("FreeCAD 설치 방법:")
    print("  macOS: brew install freecad")
    print("  Linux: sudo apt-get install freecad")
    print()
    sys.exit(1)

# FreeCAD 버전 확인
try:
    result = subprocess.run(
        [freecad_path, "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"✅ FreeCAD 버전 확인 완료")
except Exception as e:
    print(f"⚠️  버전 확인 실패 (계속 진행): {e}")

print()

# Step 2: Agent로 테스트 객체 생성
print("📋 Step 2: Agent로 테스트 객체 생성")
print("-"*70)

agent = ToolCallingAgent(model='groq/openai/gpt-oss-20b', verbose=False)

test_cases = [
    {
        "name": "간단한 박스",
        "prompt": "10x10x10 박스를 만들고 문서를 test_box.FCStd로 저장한 후 finish 해줘",
        "filename": "test_box.FCStd"
    },
    {
        "name": "실린더와 구",
        "prompt": """
        다음 객체들을 만들어줘:
        1. 5mm 반지름, 20mm 높이 실린더를 위치 (0, 0, 0)에 만들기
        2. 10mm 반지름 구를 위치 (20, 0, 10)에 만들기
        3. 문서를 test_cylinder_sphere.FCStd로 저장
        4. finish 호출
        """,
        "filename": "test_cylinder_sphere.FCStd"
    },
    {
        "name": "간단한 의자",
        "prompt": """
        간단한 의자를 만들어줘:
        1. 좌판: 40x40x5 박스를 위치 (0, 0, 45)에
        2. 다리1: 5x5x45 박스를 위치 (0, 0, 0)에
        3. 다리2: 5x5x45 박스를 위치 (35, 0, 0)에
        4. 다리3: 5x5x45 박스를 위치 (0, 35, 0)에
        5. 다리4: 5x5x45 박스를 위치 (35, 35, 0)에
        6. 문서를 test_chair.FCStd로 저장
        7. finish 호출
        """,
        "filename": "test_chair.FCStd"
    }
]

created_files = []

for i, test in enumerate(test_cases, 1):
    print(f"\n테스트 {i}: {test['name']}")
    print(f"  프롬프트: {test['prompt'][:50]}...")
    
    try:
        result = agent.run(test['prompt'], max_iterations=16)
        
        if result['success']:
            filepath = project_root / test['filename']
            if filepath.exists():
                print(f"  ✅ 성공: {test['filename']} 생성됨")
                created_files.append(str(filepath))
            else:
                print(f"  ⚠️  Agent 성공했지만 파일이 없음")
        else:
            print(f"  ❌ 실패: {result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"  ❌ 오류: {e}")
    
    # 다음 테스트를 위해 히스토리 초기화
    agent.reset()

print()
print("-"*70)

# Step 3: FreeCAD GUI로 파일 열기
print()
print("📋 Step 3: FreeCAD GUI로 파일 열기")
print("-"*70)
print()

if not created_files:
    print("❌ 생성된 파일이 없습니다.")
    print()
    print("대체 방법: 수동으로 파일 생성")
    print()
    print("다음 명령어를 실행하세요:")
    print()
    print("  python3 -c \"")
    print("  from src.agent import ToolCallingAgent")
    print("  agent = ToolCallingAgent()")
    print("  agent.run('10x10x10 박스를 만들고 test.FCStd로 저장해줘')")
    print("  \"")
    print()
    sys.exit(1)

print(f"✅ {len(created_files)}개 파일 생성 완료:")
for f in created_files:
    print(f"  - {f}")

print()
print("🚀 FreeCAD GUI로 파일을 여는 중...")
print()

# 첫 번째 파일을 FreeCAD GUI로 열기
first_file = created_files[0]

try:
    # macOS
    if sys.platform == 'darwin':
        print(f"명령어: open -a FreeCAD {first_file}")
        subprocess.Popen(['open', '-a', 'FreeCAD', first_file])
        print(f"✅ FreeCAD GUI가 {os.path.basename(first_file)}을(를) 열었습니다!")
    
    # Linux
    elif sys.platform == 'linux':
        print(f"명령어: freecad {first_file}")
        subprocess.Popen([freecad_path, first_file])
        print(f"✅ FreeCAD GUI가 {os.path.basename(first_file)}을(를) 열었습니다!")
    
    else:
        print(f"⚠️  자동 실행 미지원 OS. 수동으로 파일을 여세요:")
        print(f"  {first_file}")

except Exception as e:
    print(f"❌ FreeCAD GUI 실행 실패: {e}")
    print()
    print("수동으로 여세요:")
    print(f"  macOS: open -a FreeCAD {first_file}")
    print(f"  Linux: freecad {first_file}")

print()
print("="*70)
print("🎉 설정 완료!")
print("="*70)
print()
print("📚 추가 파일들을 열려면:")
for f in created_files:
    print(f"  open -a FreeCAD {f}")
print()
print("💡 팁:")
print("  - FreeCAD에서 View > Std View Menu > Fit All (V, F)로 전체 보기")
print("  - Tools > View Parameters로 렌더링 옵션 조정")
print("  - File > Export로 다른 형식(STEP, STL 등)으로 내보내기")
print()

