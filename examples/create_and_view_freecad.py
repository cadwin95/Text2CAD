#!/usr/bin/env python3
"""
FreeCAD 객체를 생성하고 GUI로 보는 간단한 스크립트
Agent 없이 직접 FreeCAD 스크립트를 생성하고 실행합니다.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

def create_freecad_script(output_file: str, objects: list) -> str:
    """
    FreeCAD Python 스크립트를 생성합니다.
    
    Args:
        output_file: 저장할 파일 경로
        objects: 생성할 객체 리스트
        
    
    Returns:
        FreeCAD Python 스크립트 내용
    """
    script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import FreeCAD
import Part

# 새 문서 생성
doc = FreeCAD.newDocument("MyDesign")

"""
    
    for obj in objects:
        obj_type = obj['type']
        params = obj['params']
        name = obj.get('name', obj_type)
        
        if obj_type == 'box':
            script += f"""
# 박스 생성: {name}
box = doc.addObject("Part::Box", "{name}")
box.Length = {params['length']}
box.Width = {params['width']}
box.Height = {params['height']}
"""
            if 'position' in params:
                pos = params['position']
                script += f"box.Placement.Base = FreeCAD.Vector({pos[0]}, {pos[1]}, {pos[2]})\n"
        
        elif obj_type == 'cylinder':
            script += f"""
# 실린더 생성: {name}
cylinder = doc.addObject("Part::Cylinder", "{name}")
cylinder.Radius = {params['radius']}
cylinder.Height = {params['height']}
"""
            if 'position' in params:
                pos = params['position']
                script += f"cylinder.Placement.Base = FreeCAD.Vector({pos[0]}, {pos[1]}, {pos[2]})\n"
        
        elif obj_type == 'sphere':
            script += f"""
# 구 생성: {name}
sphere = doc.addObject("Part::Sphere", "{name}")
sphere.Radius = {params['radius']}
"""
            if 'position' in params:
                pos = params['position']
                script += f"sphere.Placement.Base = FreeCAD.Vector({pos[0]}, {pos[1]}, {pos[2]})\n"
    
    script += f"""
# 문서 재계산
doc.recompute()

# 문서 저장
doc.saveAs("{output_file}")
print(f"✅ 문서 저장 완료: {output_file}")

FreeCAD.closeDocument(doc.Name)
"""
    
    return script


def main():
    print("="*70)
    print("🎨 FreeCAD 객체 생성 및 GUI 뷰어")
    print("="*70)
    print()
    
    # FreeCAD 경로 찾기
    freecad_paths = [
        "/opt/homebrew/bin/freecad",
        "/usr/local/bin/freecad",
        "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD",
    ]
    
    freecad_path = None
    for path in freecad_paths:
        if os.path.exists(path):
            freecad_path = path
            break
    
    if not freecad_path:
        print("❌ FreeCAD를 찾을 수 없습니다.")
        print("설치: brew install freecad")
        sys.exit(1)
    
    print(f"✅ FreeCAD 발견: {freecad_path}")
    print()
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "simple_box",
            "description": "간단한 박스",
            "objects": [
                {
                    "type": "box",
                    "name": "SimpleBox",
                    "params": {
                        "length": 10,
                        "width": 10,
                        "height": 10
                    }
                }
            ]
        },
        {
            "name": "positioned_objects",
            "description": "위치가 있는 여러 객체",
            "objects": [
                {
                    "type": "cylinder",
                    "name": "Cylinder1",
                    "params": {
                        "radius": 5,
                        "height": 20,
                        "position": [0, 0, 0]
                    }
                },
                {
                    "type": "sphere",
                    "name": "Sphere1",
                    "params": {
                        "radius": 8,
                        "position": [25, 0, 10]
                    }
                },
                {
                    "type": "box",
                    "name": "Box1",
                    "params": {
                        "length": 15,
                        "width": 10,
                        "height": 5,
                        "position": [50, 0, 0]
                    }
                }
            ]
        },
        {
            "name": "simple_chair",
            "description": "간단한 의자",
            "objects": [
                {
                    "type": "box",
                    "name": "Seat",
                    "params": {
                        "length": 40,
                        "width": 40,
                        "height": 5,
                        "position": [0, 0, 45]
                    }
                },
                {
                    "type": "box",
                    "name": "Leg1",
                    "params": {
                        "length": 5,
                        "width": 5,
                        "height": 45,
                        "position": [0, 0, 0]
                    }
                },
                {
                    "type": "box",
                    "name": "Leg2",
                    "params": {
                        "length": 5,
                        "width": 5,
                        "height": 45,
                        "position": [35, 0, 0]
                    }
                },
                {
                    "type": "box",
                    "name": "Leg3",
                    "params": {
                        "length": 5,
                        "width": 5,
                        "height": 45,
                        "position": [0, 35, 0]
                    }
                },
                {
                    "type": "box",
                    "name": "Leg4",
                    "params": {
                        "length": 5,
                        "width": 5,
                        "height": 45,
                        "position": [35, 35, 0]
                    }
                },
                {
                    "type": "box",
                    "name": "Back",
                    "params": {
                        "length": 40,
                        "width": 5,
                        "height": 50,
                        "position": [0, 35, 45]
                    }
                }
            ]
        }
    ]
    
    created_files = []
    
    # 각 테스트 케이스 실행
    for i, test in enumerate(test_cases, 1):
        print(f"📋 테스트 {i}: {test['description']}")
        print("-"*70)
        
        # 출력 파일 경로
        output_file = Path.cwd() / f"{test['name']}.FCStd"
        
        # FreeCAD 스크립트 생성
        script_content = create_freecad_script(str(output_file), test['objects'])
        
        # 임시 스크립트 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_file = f.name
        
        print(f"  스크립트 생성: {script_file}")
        print(f"  객체 개수: {len(test['objects'])}개")
        
        try:
            # FreeCAD로 스크립트 실행 (콘솔 모드)
            result = subprocess.run(
                [freecad_path, "-c", script_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if output_file.exists():
                print(f"  ✅ 성공: {output_file.name} 생성됨 ({output_file.stat().st_size} bytes)")
                created_files.append(str(output_file))
            else:
                print(f"  ❌ 실패: 파일이 생성되지 않음")
                if result.stdout:
                    print(f"  출력: {result.stdout[:200]}")
                if result.stderr:
                    print(f"  오류: {result.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            print(f"  ❌ 타임아웃")
        except Exception as e:
            print(f"  ❌ 오류: {e}")
        finally:
            # 임시 스크립트 파일 삭제
            try:
                os.unlink(script_file)
            except:
                pass
        
        print()
    
    # 결과 요약
    print("="*70)
    print(f"✅ {len(created_files)}/{len(test_cases)}개 파일 생성 완료")
    print("="*70)
    print()
    
    if not created_files:
        print("❌ 생성된 파일이 없습니다.")
        return
    
    # 첫 번째 파일을 GUI로 열기
    first_file = created_files[0]
    
    print(f"🚀 FreeCAD GUI로 {Path(first_file).name}을(를) 여는 중...")
    print()
    
    try:
        if sys.platform == 'darwin':
            subprocess.Popen(['open', first_file])
            print(f"✅ FreeCAD GUI가 열렸습니다!")
        elif sys.platform == 'linux':
            subprocess.Popen([freecad_path, first_file])
            print(f"✅ FreeCAD GUI가 열렸습니다!")
        else:
            print(f"⚠️  수동으로 여세요: {first_file}")
    except Exception as e:
        print(f"❌ GUI 실행 실패: {e}")
        print(f"\n수동으로 여세요:")
        print(f"  macOS: open {first_file}")
        print(f"  Linux: freecad {first_file}")
    
    print()
    print("📚 생성된 파일들:")
    for f in created_files:
        print(f"  - {f}")
    
    print()
    print("💡 FreeCAD GUI 팁:")
    print("  - View > Fit All (V, F): 전체 보기")
    print("  - 마우스 휠: 확대/축소")
    print("  - 마우스 가운데 버튼: 회전")
    print("  - Shift + 마우스 가운데: 이동")
    print("  - File > Export: STEP, STL 등 다른 형식으로 내보내기")
    print()

if __name__ == "__main__":
    main()

