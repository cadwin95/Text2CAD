#!/usr/bin/env python3
"""
FreeCAD 인터랙티브 모드
실시간으로 FreeCAD GUI를 보면서 채팅으로 객체를 추가/수정합니다.
"""

import sys
import os
import subprocess
import tempfile
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import ToolCallingAgent

class InteractiveFreeCAD:
    """FreeCAD 인터랙티브 세션"""
    
    def __init__(self, model: str = "groq/openai/gpt-oss-20b"):
        """
        초기화
        
        Args:
            model: 사용할 LLM 모델
        """
        self.model = model
        self.agent = ToolCallingAgent(model=model, verbose=True)
        
        # FreeCAD 경로 찾기
        self.freecad_path = self._find_freecad()
        if not self.freecad_path:
            print("❌ FreeCAD를 찾을 수 없습니다.")
            print("설치: brew install freecad")
            sys.exit(1)
        
        # 작업 파일
        self.work_file = project_root / "interactive_session.FCStd"
        self.script_file = project_root / "interactive_script.py"
        
        # FreeCAD 프로세스
        self.freecad_process = None
        
        # 세션 히스토리
        self.session_history = []
        self.object_count = 0
    
    def _find_freecad(self):
        """FreeCAD 경로 찾기"""
        paths = [
            "/opt/homebrew/bin/freecad",
            "/usr/local/bin/freecad",
            "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD",
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def start(self):
        """인터랙티브 세션 시작"""
        print("="*70)
        print("🎨 FreeCAD 인터랙티브 모드")
        print("="*70)
        print()
        print(f"📡 LiteLLM Proxy: http://localhost:4000")
        print(f"🧠 모델: {self.model}")
        print(f"📁 작업 파일: {self.work_file}")
        print()
        print("💡 사용 방법:")
        print("  - 원하는 객체를 자유롭게 요청하세요")
        print("  - FreeCAD 창에서 실시간으로 결과를 확인할 수 있습니다")
        print("  - 'quit', 'exit', 'q'를 입력하면 종료됩니다")
        print("  - 'clear'를 입력하면 모든 객체를 삭제합니다")
        print("  - 'save'를 입력하면 현재 상태를 저장합니다")
        print()
        
        # 초기 FreeCAD 문서 생성
        self._create_initial_document()
        
        # FreeCAD GUI 열기
        self._open_freecad_gui()
        
        print("="*70)
        print("🚀 세션이 시작되었습니다! FreeCAD 창을 확인하세요.")
        print("="*70)
        print()
        
        # 메인 루프
        self._run_loop()
    
    def _create_initial_document(self):
        """초기 FreeCAD 문서 생성"""
        script = """#!/usr/bin/env python3
import FreeCAD

# 새 문서 생성
doc = FreeCAD.newDocument("InteractiveSession")

# 문서 저장
doc.saveAs("{}")
print("✅ 초기 문서 생성 완료")

FreeCAD.closeDocument(doc.Name)
""".format(str(self.work_file))
        
        # 스크립트 파일 작성
        with open(self.script_file, 'w') as f:
            f.write(script)
        
        # FreeCAD로 실행
        try:
            subprocess.run(
                [self.freecad_path, "-c", str(self.script_file)],
                capture_output=True,
                timeout=30  # 초기 문서는 30초면 충분
            )
            print(f"✅ 초기 문서 생성: {self.work_file}")
        except Exception as e:
            print(f"⚠️  초기 문서 생성 실패: {e}")
    
    def _open_freecad_gui(self):
        """FreeCAD GUI 열기"""
        try:
            print("🚀 FreeCAD GUI를 여는 중...")
            
            # macOS
            if sys.platform == 'darwin':
                # 방법 1: FreeCAD 실행 파일을 직접 실행 (포그라운드)
                self.freecad_process = subprocess.Popen(
                    [self.freecad_path, str(self.work_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # FreeCAD가 열릴 때까지 대기
                time.sleep(4)
                
                # AppleScript로 FreeCAD를 포그라운드로 가져오기
                try:
                    subprocess.run(
                        ['osascript', '-e', 'tell application "FreeCAD" to activate'],
                        capture_output=True,
                        timeout=5
                    )
                    print("✅ FreeCAD GUI가 포그라운드로 열렸습니다!")
                except:
                    print("✅ FreeCAD GUI 열림 (수동으로 창을 클릭해주세요)")
            
            # Linux
            else:
                self.freecad_process = subprocess.Popen(
                    [self.freecad_path, str(self.work_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(3)
                print("✅ FreeCAD GUI 열림")
        
        except Exception as e:
            print(f"⚠️  FreeCAD GUI 실행 실패: {e}")
            print(f"💡 수동으로 여세요: {self.freecad_path} {self.work_file}")
    
    def _run_loop(self):
        """메인 인터랙티브 루프"""
        turn = 0
        
        while True:
            turn += 1
            
            # 사용자 입력
            try:
                print(f"\n{'='*70}")
                print(f"턴 {turn} - 무엇을 만들고 싶으신가요?")
                print(f"{'='*70}")
                user_input = input("👤 당신: ").strip()
                print()
            except (EOFError, KeyboardInterrupt):
                print("\n\n세션을 종료합니다...")
                break
            
            if not user_input:
                continue
            
            # 종료 명령
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("세션을 종료합니다...")
                break
            
            # 클리어 명령
            if user_input.lower() == 'clear':
                self._clear_all_objects()
                continue
            
            # 저장 명령
            if user_input.lower() == 'save':
                self._save_document()
                continue
            
            # Agent 실행
            try:
                # Agent가 finish를 호출하지 않도록 프롬프트 수정
                enhanced_prompt = f"{user_input}\n(이전 객체들을 유지하면서 새로운 객체를 추가해주세요. finish는 호출하지 마세요)"
                
                result = self.agent.run(enhanced_prompt, max_iterations=16)
                
                if result['success']:
                    # 모든 객체를 FreeCAD 파일로 저장
                    self._update_freecad_document()
                    
                    self.session_history.append({
                        'turn': turn,
                        'user': user_input,
                        'result': result
                    })
                else:
                    print(f"❌ 실패: {result.get('message', 'Unknown error')}")
            
            except Exception as e:
                print(f"❌ 오류: {e}")
                import traceback
                traceback.print_exc()
    
    def _update_freecad_document(self):
        """Agent의 현재 상태를 FreeCAD 문서로 업데이트"""
        # Agent의 대화 히스토리에서 모든 객체 추출
        objects = self._extract_objects_from_history()
        
        if not objects:
            print("⚠️  생성된 객체가 없습니다.")
            return
        
        # FreeCAD 스크립트 생성
        script = self._generate_freecad_script(objects)
        
        # 스크립트 파일 작성
        with open(self.script_file, 'w') as f:
            f.write(script)
        
        # FreeCAD로 실행
        try:
            print(f"⏳ FreeCAD 문서 업데이트 중... ({len(objects)}개 객체)")
            subprocess.run(
                [self.freecad_path, "-c", str(self.script_file)],
                capture_output=True,
                timeout=60  # 10초 → 60초로 증가
            )
            print(f"✅ FreeCAD 업데이트 완료 ({len(objects)}개 객체)")
            
            # macOS: FreeCAD를 포그라운드로 가져오기 + 리로드 안내
            if sys.platform == 'darwin':
                try:
                    # FreeCAD 활성화
                    subprocess.run(
                        ['osascript', '-e', 'tell application "FreeCAD" to activate'],
                        capture_output=True,
                        timeout=3
                    )
                    print("💡 FreeCAD에서 Ctrl+R을 눌러 문서를 새로고침하거나")
                    print("   File > Recent Files > interactive_session.FCStd를 다시 여세요")
                except:
                    pass
            else:
                print("💡 FreeCAD에서 File > Recent Files > interactive_session.FCStd를 다시 여세요")
            
        except Exception as e:
            print(f"❌ FreeCAD 업데이트 실패: {e}")
    
    def _extract_objects_from_history(self):
        """Agent 대화 히스토리에서 생성된 객체 추출"""
        objects = []
        
        for msg in self.agent.messages:
            if msg.get('role') == 'tool':
                try:
                    import json
                    content = json.loads(msg.get('content', '{}'))
                    
                    if content.get('success') and content.get('type'):
                        obj_type = content['type'].lower()
                        obj_name = content.get('object_name', f'{obj_type}_{len(objects)}')
                        params = content.get('parameters', {})
                        
                        objects.append({
                            'type': obj_type,
                            'name': obj_name,
                            'params': params
                        })
                except:
                    pass
        
        return objects
    
    def _generate_freecad_script(self, objects):
        """객체 리스트로부터 FreeCAD Python 스크립트 생성"""
        script = """#!/usr/bin/env python3
import FreeCAD
import Part

# 문서 열기 또는 생성
try:
    doc = FreeCAD.openDocument("{}")
except:
    doc = FreeCAD.newDocument("InteractiveSession")

# 기존 객체 모두 삭제
for obj in doc.Objects:
    doc.removeObject(obj.Name)

""".format(str(self.work_file))
        
        for obj in objects:
            obj_type = obj['type']
            params = obj['params']
            name = obj['name']
            
            if obj_type == 'box':
                script += f"""
# 박스: {name}
box = doc.addObject("Part::Box", "{name}")
box.Length = {params.get('length', 10)}
box.Width = {params.get('width', 10)}
box.Height = {params.get('height', 10)}
"""
                pos = params.get('position', {})
                if pos:
                    script += f"box.Placement.Base = FreeCAD.Vector({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})\n"
                
                rot = params.get('rotation', 0)
                if rot != 0:
                    script += f"box.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), {rot})\n"
            
            elif obj_type == 'cylinder':
                script += f"""
# 실린더: {name}
cylinder = doc.addObject("Part::Cylinder", "{name}")
cylinder.Radius = {params.get('radius', 5)}
cylinder.Height = {params.get('height', 10)}
"""
                pos = params.get('position', {})
                if pos:
                    script += f"cylinder.Placement.Base = FreeCAD.Vector({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})\n"
                
                rot = params.get('rotation', 0)
                if rot != 0:
                    script += f"cylinder.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), {rot})\n"
            
            elif obj_type == 'sphere':
                script += f"""
# 구: {name}
sphere = doc.addObject("Part::Sphere", "{name}")
sphere.Radius = {params.get('radius', 5)}
"""
                pos = params.get('position', {})
                if pos:
                    script += f"sphere.Placement.Base = FreeCAD.Vector({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})\n"
            
            elif obj_type == 'cone':
                script += f"""
# 원뿔: {name}
cone = doc.addObject("Part::Cone", "{name}")
cone.Radius1 = {params.get('radius1', 5)}
cone.Radius2 = {params.get('radius2', 2)}
cone.Height = {params.get('height', 10)}
"""
                pos = params.get('position', {})
                if pos:
                    script += f"cone.Placement.Base = FreeCAD.Vector({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})\n"
                
                rot = params.get('rotation', 0)
                if rot != 0:
                    script += f"cone.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), {rot})\n"
        
        script += f"""
# 문서 재계산
doc.recompute()

# 문서 저장
doc.saveAs("{str(self.work_file)}")

FreeCAD.closeDocument(doc.Name)
"""
        
        return script
    
    def _clear_all_objects(self):
        """모든 객체 삭제"""
        print("🗑️  모든 객체를 삭제합니다...")
        
        # Agent 히스토리 초기화
        self.agent.reset()
        
        # FreeCAD 문서 초기화
        self._create_initial_document()
        
        print("✅ 모든 객체가 삭제되었습니다.")
        print("💡 FreeCAD에서 File > Recent Files > interactive_session.FCStd를 다시 열어주세요.")
    
    def _save_document(self):
        """현재 상태 저장"""
        save_name = input("저장할 파일 이름 (예: my_design.FCStd): ").strip()
        
        if not save_name:
            save_name = f"saved_design_{int(time.time())}.FCStd"
        
        if not save_name.endswith('.FCStd'):
            save_name += '.FCStd'
        
        save_path = project_root / save_name
        
        # 현재 작업 파일 복사
        import shutil
        try:
            shutil.copy(self.work_file, save_path)
            print(f"✅ 저장 완료: {save_path}")
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
    
    def cleanup(self):
        """세션 정리"""
        print("\n세션을 정리하는 중...")
        
        # 임시 스크립트 파일 삭제
        try:
            if self.script_file.exists():
                self.script_file.unlink()
        except:
            pass
        
        print("✅ 정리 완료")


def main():
    """메인 함수"""
    # 모델 선택 (선택사항)
    if len(sys.argv) > 1:
        model = sys.argv[1]
    else:
        model = "groq/openai/gpt-oss-20b"
    
    # 인터랙티브 세션 시작
    session = InteractiveFreeCAD(model=model)
    
    try:
        session.start()
    except KeyboardInterrupt:
        print("\n\n키보드 인터럽트 감지...")
    finally:
        session.cleanup()
        print("\n👋 안녕히 가세요!")


if __name__ == "__main__":
    main()

