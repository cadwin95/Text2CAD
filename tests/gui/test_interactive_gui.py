#!/usr/bin/env python3
"""
FreeCAD 인터랙티브 모드 GUI 자동 열기 테스트
"""

import sys
import subprocess
import time
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*70)
print("🧪 FreeCAD GUI 자동 열기 테스트")
print("="*70)
print()

print("📋 테스트 항목:")
print("  1. FreeCAD 실행 파일 직접 실행")
print("  2. AppleScript로 포그라운드 활성화")
print("  3. 인터랙티브 세션 시작")
print()

# 테스트 1: FreeCAD 경로 확인
print("테스트 1: FreeCAD 경로 확인")
print("-"*70)

freecad_path = "/opt/homebrew/bin/freecad"
if Path(freecad_path).exists():
    print(f"✅ FreeCAD 발견: {freecad_path}")
else:
    print(f"❌ FreeCAD를 찾을 수 없습니다: {freecad_path}")
    sys.exit(1)

print()

# 테스트 2: 간단한 문서 생성
print("테스트 2: 테스트 문서 생성")
print("-"*70)

test_file = project_root / "test_gui_autoopen.FCStd"

script_content = f"""
import FreeCAD

doc = FreeCAD.newDocument("TestDoc")

# 간단한 박스 추가
box = doc.addObject("Part::Box", "TestBox")
box.Length = 10
box.Width = 10
box.Height = 10

doc.recompute()
doc.saveAs("{test_file}")
FreeCAD.closeDocument(doc.Name)
print("✅ 테스트 문서 생성 완료")
"""

script_file = project_root / "test_gui_script.py"
with open(script_file, 'w') as f:
    f.write(script_content)

try:
    result = subprocess.run(
        [freecad_path, "-c", str(script_file)],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if test_file.exists():
        print(f"✅ 테스트 문서 생성 성공: {test_file}")
    else:
        print("❌ 테스트 문서 생성 실패")
        print(f"출력: {result.stdout}")
        print(f"오류: {result.stderr}")
        sys.exit(1)
except Exception as e:
    print(f"❌ 오류: {e}")
    sys.exit(1)

print()

# 테스트 3: FreeCAD GUI 자동 열기
print("테스트 3: FreeCAD GUI 자동 열기 (포그라운드)")
print("-"*70)
print("🚀 FreeCAD를 여는 중...")

try:
    # FreeCAD 실행 파일로 직접 열기
    freecad_process = subprocess.Popen(
        [freecad_path, str(test_file)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # 잠시 대기
    time.sleep(4)
    
    print("✅ FreeCAD 프로세스 시작됨")
    print()
    
    # AppleScript로 포그라운드로 가져오기
    print("📱 FreeCAD를 포그라운드로 활성화 중...")
    
    result = subprocess.run(
        ['osascript', '-e', 'tell application "FreeCAD" to activate'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print("✅ FreeCAD가 포그라운드로 활성화되었습니다!")
        print()
        print("💡 FreeCAD 창이 보이시나요?")
        print("   - 보인다면: ✅ 테스트 성공!")
        print("   - 안 보인다면: ❌ 수동으로 FreeCAD 아이콘을 클릭하세요")
    else:
        print("⚠️  포그라운드 활성화 실패 (하지만 FreeCAD는 실행 중)")
        print(f"오류: {result.stderr}")
        print()
        print("💡 Dock이나 Command+Tab으로 FreeCAD를 찾아보세요")

except Exception as e:
    print(f"❌ 오류: {e}")

print()
print("="*70)
print("🎉 테스트 완료!")
print("="*70)
print()
print("📝 정리:")
print(f"  - 테스트 문서: {test_file}")
print(f"  - 테스트 스크립트: {script_file}")
print()
print("🚀 실제 인터랙티브 모드를 실행하려면:")
print("  python3 interactive_freecad.py")
print()

# 사용자 입력 대기
try:
    input("Enter를 눌러 FreeCAD를 종료하고 테스트를 마칩니다...")
    
    # FreeCAD 프로세스 종료
    if freecad_process:
        freecad_process.terminate()
        freecad_process.wait(timeout=5)
        print("✅ FreeCAD 프로세스 종료됨")
    
    # 테스트 파일 정리
    if test_file.exists():
        test_file.unlink()
    if script_file.exists():
        script_file.unlink()
    
    print("✅ 정리 완료")
    
except KeyboardInterrupt:
    print("\n키보드 인터럽트")
    if freecad_process:
        freecad_process.terminate()

