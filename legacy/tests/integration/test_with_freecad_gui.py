#!/usr/bin/env python3
"""
FreeCAD GUI 통합 테스트
실제 FreeCAD가 설치되어 있어야 합니다.
"""

import sys
from pathlib import Path

# FreeCAD 경로 추가 (macOS 기준)
FREECAD_PATH = "/Applications/FreeCAD.app/Contents/Resources/lib"
if Path(FREECAD_PATH).exists():
    sys.path.insert(0, FREECAD_PATH)
    print(f"✓ FreeCAD 경로 추가: {FREECAD_PATH}")
else:
    print(f"⚠ FreeCAD를 찾을 수 없습니다: {FREECAD_PATH}")
    print("시뮬레이션 모드로 계속 진행합니다...")

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import FreeCAD
    import Part
    FREECAD_AVAILABLE = True
    print(f"✓ FreeCAD 버전: {FreeCAD.Version()}")
except ImportError:
    FREECAD_AVAILABLE = False
    print("○ FreeCAD 미설치 - 시뮬레이션 모드")

print()
print("="*60)
print("FreeCAD GUI 통합 테스트")
print("="*60)
print()

# Agent로 모델 생성
from src.agent import ToolCallingAgent

agent = ToolCallingAgent(verbose=True)

# 테스트 명령
commands = [
    "새 문서를 만들어줘",
    "10mm x 10mm x 10mm 크기의 박스를 만들어줘",
    "반지름 5mm, 높이 20mm인 실린더를 추가해줘",
    "반지름 7mm인 구도 추가해줘",
]

for cmd in commands:
    result = agent.run(cmd)
    print()

# 파일 저장
print("="*60)
print("모델 저장")
print("="*60)
result = agent.run("현재 문서를 output/agent_model.FCStd로 저장해줘")
print()

if FREECAD_AVAILABLE:
    print("="*60)
    print("FreeCAD GUI 실행")
    print("="*60)
    print()
    print("FreeCAD GUI를 실행하려면:")
    print("  1. FreeCAD 앱을 실행하세요")
    print("  2. File > Open 메뉴에서 'output/agent_model.FCStd' 열기")
    print()
    print("또는 터미널에서:")
    print("  open -a FreeCAD output/agent_model.FCStd")
    print()
    
    # GUI 자동 실행 (선택사항)
    try:
        import FreeCADGui
        
        user_input = input("FreeCAD GUI를 지금 실행하시겠습니까? (y/N): ")
        if user_input.lower() == 'y':
            print("FreeCAD GUI 실행 중...")
            FreeCADGui.showMainWindow()
            
            # 저장된 문서 열기
            if Path("output/agent_model.FCStd").exists():
                FreeCAD.openDocument("output/agent_model.FCStd")
            
            FreeCADGui.exec_loop()
    except Exception as e:
        print(f"GUI 실행 실패: {e}")
        print("수동으로 FreeCAD를 실행하고 파일을 열어주세요.")
else:
    print("="*60)
    print("FreeCAD 설치 안내")
    print("="*60)
    print()
    print("실제 3D 모델을 보려면 FreeCAD를 설치하세요:")
    print()
    print("macOS:")
    print("  brew install --cask freecad")
    print()
    print("공식 사이트:")
    print("  https://www.freecad.org/downloads.php")
    print()
    print("설치 후 다시 이 스크립트를 실행하세요!")
    print()

print("="*60)
print("테스트 완료")
print("="*60)

