#!/usr/bin/env python3
"""
FreeCAD Web Viewer with Chat Interface
채팅창과 3D 뷰어를 함께 제공하는 웹 인터페이스
"""

import sys
import os
from pathlib import Path
import json
import asyncio
from datetime import datetime

# 프로젝트 루트
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import tempfile

from src.agent import ToolCallingAgent

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = 'freecad-web-viewer-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 전역 변수
agent = None
freecad_path = "/opt/homebrew/bin/freecad"
work_dir = project_root / "web_viewer" / "models"
work_dir.mkdir(exist_ok=True)

# 현재 세션
current_session = {
    "session_id": None,
    "messages": [],
    "objects": [],
    "model_file": None
}


def initialize_agent():
    """Agent 초기화"""
    global agent
    if agent is None:
        agent = ToolCallingAgent(model="groq/openai/gpt-oss-20b", verbose=False)
    return agent


def export_to_stl(fcstd_file: Path, stl_file: Path) -> bool:
    """FreeCAD 문서를 STL로 내보내기"""
    print(f"    📤 STL 내보내기: {fcstd_file} -> {stl_file}")
    
    script = f"""
import FreeCAD
import Mesh
import sys

try:
    # 문서 열기
    print("1. Opening document...")
    doc = FreeCAD.openDocument("{fcstd_file}")
    print("2. Document opened: " + doc.Name + ", Objects: " + str(len(doc.Objects)))
    
    # 모든 객체를 하나의 메시로 합치기
    shapes = []
    for obj in doc.Objects:
        print("3. Checking object: " + obj.Name + ", Type: " + obj.TypeId)
        if hasattr(obj, 'Shape'):
            shapes.append(obj.Shape)
            print("   - Shape added")
    
    print("4. Total shapes collected: " + str(len(shapes)))
    
    if shapes:
        # 복합 Shape 생성
        import Part
        print("5. Creating compound shape...")
        compound = Part.makeCompound(shapes)
        
        # 메시로 변환
        print("6. Converting to mesh...")
        mesh = doc.addObject("Mesh::Feature", "TempMesh")
        mesh.Mesh = Mesh.Mesh(compound.tessellate(0.1))
        
        # STL 내보내기
        print("7. Exporting to STL...")
        Mesh.export([mesh], "{stl_file}")
        print("SUCCESS: STL export complete: {stl_file}")
        
        FreeCAD.closeDocument(doc.Name)
        sys.exit(0)
    else:
        print("ERROR: No shapes to export")
        FreeCAD.closeDocument(doc.Name)
        sys.exit(1)
    
except Exception as e:
    print("ERROR: STL export failed: " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    script_file = work_dir / "export_script.py"
    with open(script_file, 'w') as f:
        f.write(script)
    
    try:
        print("    🔄 FreeCAD 실행 중...")
        result = subprocess.run(
            [freecad_path, "-c", str(script_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"    📝 FreeCAD 출력:")
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"      {line}")
        
        if result.stderr:
            print(f"    ⚠️  오류 출력:")
            for line in result.stderr.split('\n'):
                if line.strip() and 'Error: Failed to open library' not in line:
                    print(f"      {line}")
        
        exists = stl_file.exists()
        print(f"    📦 STL 파일 생성: {exists}")
        return exists
        
    except Exception as e:
        print(f"    ❌ STL export failed: {e}")
        return False


def update_3d_model():
    """현재 객체들로 3D 모델 업데이트"""
    if not current_session["objects"]:
        return None
    
    # FreeCAD 스크립트 생성
    fcstd_file = work_dir / f"model_{current_session['session_id']}.FCStd"
    
    script = f"""
import FreeCAD
import Part

doc = FreeCAD.newDocument("WebModel")

"""
    
    for obj in current_session["objects"]:
        obj_type = obj['type']
        params = obj['params']
        name = obj['name']
        
        if obj_type == 'box':
            script += f"""
box = doc.addObject("Part::Box", "{name}")
box.Length = {params.get('length', 10)}
box.Width = {params.get('width', 10)}
box.Height = {params.get('height', 10)}
"""
            pos = params.get('position', {})
            if pos:
                script += f"box.Placement.Base = FreeCAD.Vector({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})\n"
        
        elif obj_type == 'cylinder':
            script += f"""
cylinder = doc.addObject("Part::Cylinder", "{name}")
cylinder.Radius = {params.get('radius', 5)}
cylinder.Height = {params.get('height', 10)}
"""
            pos = params.get('position', {})
            if pos:
                script += f"cylinder.Placement.Base = FreeCAD.Vector({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})\n"
        
        elif obj_type == 'sphere':
            script += f"""
sphere = doc.addObject("Part::Sphere", "{name}")
sphere.Radius = {params.get('radius', 5)}
"""
            pos = params.get('position', {})
            if pos:
                script += f"sphere.Placement.Base = FreeCAD.Vector({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})\n"
    
    script += f"""
doc.recompute()
doc.saveAs("{fcstd_file}")
FreeCAD.closeDocument(doc.Name)

# 명시적으로 종료 (인터랙티브 모드 진입 방지)
import sys
sys.exit(0)
"""
    
    # 스크립트 실행
    script_file = work_dir / "generate_script.py"
    with open(script_file, 'w') as f:
        f.write(script)
    
    try:
        subprocess.run(
            [freecad_path, "-c", str(script_file)],
            capture_output=True,
            timeout=60
        )
        
        # STL로 변환
        stl_file = work_dir / f"model_{current_session['session_id']}.stl"
        if export_to_stl(fcstd_file, stl_file):
            return f"model_{current_session['session_id']}.stl"
        
    except Exception as e:
        print(f"Model update failed: {e}")
    
    return None


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """서버 종료"""
    print("\n🛑 서버 종료 요청 받음...")
    socketio.stop()
    return jsonify({"success": True, "message": "서버가 종료됩니다..."})


@app.route('/list_files')
def list_files():
    """저장된 모델 파일 목록"""
    fcstd_files = []
    for f in sorted(work_dir.glob("model_*.FCStd"), reverse=True):
        stat = f.stat()
        fcstd_files.append({
            "name": f.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"files": fcstd_files})


@app.route('/load_file/<filename>')
def load_file(filename):
    """특정 파일 로드"""
    fcstd_file = work_dir / filename
    
    if not fcstd_file.exists():
        return jsonify({"success": False, "error": "파일을 찾을 수 없습니다"})
    
    # STL 파일명
    stl_file = work_dir / f"{fcstd_file.stem}.stl"
    
    # STL이 없거나 오래된 경우 다시 생성
    if not stl_file.exists() or stl_file.stat().st_mtime < fcstd_file.stat().st_mtime:
        print(f"📦 STL 변환 중: {filename}")
        if export_to_stl(fcstd_file, stl_file):
            print(f"✅ STL 변환 완료")
        else:
            return jsonify({"success": False, "error": "STL 변환 실패"})
    
    return jsonify({
        "success": True,
        "stl_file": stl_file.name,
        "fcstd_file": filename
    })


@app.route('/models/<path:filename>')
def serve_model(filename):
    """3D 모델 파일 제공"""
    return send_from_directory(work_dir, filename)


@app.route('/new_document', methods=['POST'])
def new_document():
    """새 문서 생성 (모든 객체 삭제)"""
    global current_session
    
    try:
        # 세션 초기화
        current_session = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "messages": [],
            "objects": [],
            "model_file": None
        }
        
        print(f"\n📄 새 문서 생성: {current_session['session_id']}")
        return jsonify({
            "success": True,
            "message": "새 문서가 생성되었습니다",
            "session_id": current_session['session_id']
        })
    except Exception as e:
        print(f"❌ 새 문서 생성 실패: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/get_objects')
def get_objects():
    """현재 문서의 객체 목록"""
    return jsonify({
        "objects": current_session.get("objects", []),
        "count": len(current_session.get("objects", []))
    })


@app.route('/delete_object/<object_name>', methods=['POST'])
def delete_object(object_name):
    """특정 객체 삭제"""
    global current_session
    
    try:
        # 객체 목록에서 제거
        objects = current_session.get("objects", [])
        original_count = len(objects)
        
        objects = [obj for obj in objects if obj.get("name") != object_name]
        current_session["objects"] = objects
        
        if len(objects) == original_count:
            return jsonify({
                "success": False,
                "error": f"객체 '{object_name}'을(를) 찾을 수 없습니다"
            })
        
        print(f"🗑️  객체 삭제: {object_name}")
        print(f"   남은 객체: {len(objects)}개")
        
        # 3D 모델 재생성
        if len(objects) > 0:
            model_file = update_3d_model()
            return jsonify({
                "success": True,
                "message": f"객체 '{object_name}'이(가) 삭제되었습니다",
                "remaining": len(objects),
                "model_file": model_file.name if model_file else None
            })
        else:
            # 모든 객체가 삭제된 경우
            current_session["model_file"] = None
            return jsonify({
                "success": True,
                "message": "모든 객체가 삭제되었습니다",
                "remaining": 0,
                "model_file": None
            })
            
    except Exception as e:
        print(f"❌ 객체 삭제 실패: {e}")
        return jsonify({"success": False, "error": str(e)})


@socketio.on('connect')
def handle_connect():
    """클라이언트 연결"""
    print('Client connected')
    
    # 세션 초기화
    if current_session["session_id"] is None:
        current_session["session_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    emit('connected', {'session_id': current_session['session_id']})


@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제"""
    print('Client disconnected')


@socketio.on('send_message')
def handle_message(data):
    """사용자 메시지 처리"""
    user_message = data.get('message', '').strip()
    
    print(f"\n{'='*70}")
    print(f"📨 메시지 수신: {user_message}")
    print(f"{'='*70}")
    
    if not user_message:
        print("⚠️  빈 메시지, 무시")
        return
    
    # 메시지 저장
    current_session["messages"].append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # 클라이언트에 사용자 메시지 전송
    emit('user_message', {'message': user_message})
    
    # 특수 명령어 처리
    if user_message.lower() in ['clear', '초기화']:
        print("🗑️  초기화 명령 실행")
        current_session["objects"] = []
        current_session["messages"] = []
        if agent:
            agent.reset()
        emit('assistant_message', {'message': '✅ 모든 객체가 삭제되었습니다.'})
        emit('model_update', {'model_url': None})
        print("✅ 초기화 완료")
        return
    
    # Agent 실행
    try:
        print("🤖 Agent 실행 시작...")
        
        # 단계 1: 초기화
        emit('agent_progress', {'step': '🤖 Agent 초기화 중...'})
        agent_instance = initialize_agent()
        
        # 단계 2: 프롬프트 처리
        enhanced_prompt = f"{user_message}\n(이전 객체들을 유지하면서 새로운 객체를 추가해주세요. finish는 호출하지 마세요)"
        emit('agent_progress', {'step': '💭 요청 분석 중...'})
        
        # 단계 3: Agent 실행
        emit('agent_progress', {'step': '⚙️ 객체 생성 중...'})
        result = agent_instance.run(enhanced_prompt, max_iterations=16)
        print(f"  - Agent 실행 완료: {result.get('success', False)}")
        
        emit('assistant_thinking', {'thinking': False})
        
        if result['success']:
            # 생성된 객체 추출
            emit('agent_progress', {'step': '📦 객체 정보 수집 중...'})
            objects = extract_objects_from_agent(agent_instance)
            print(f"  - 추출된 객체: {len(objects)}개")
            for obj in objects:
                print(f"    * {obj['name']} ({obj['type']})")
            
            current_session["objects"] = objects
            
            # 3D 모델 업데이트
            emit('agent_progress', {'step': f'🔄 3D 모델 생성 중... ({len(objects)}개 객체)'})
            model_file = update_3d_model()
            
            if model_file:
                emit('agent_progress', {'step': '✨ 3D 렌더링 준비 중...'})
            
            print(f"  - 모델 파일: {model_file}")
            
            # 클라이언트에 응답 전송
            response_message = f"✅ {len(objects)}개 객체가 생성되었습니다."
            
            current_session["messages"].append({
                "role": "assistant",
                "content": response_message,
                "timestamp": datetime.now().isoformat()
            })
            
            emit('assistant_message', {'message': response_message})
            
            if model_file:
                emit('agent_progress', {'step': '✅ 완료!'})
                print(f"  - 클라이언트에 모델 업데이트 전송: /models/{model_file}")
                emit('model_update', {'model_url': f'/models/{model_file}'})
            else:
                emit('agent_progress', {'step': '⚠️ 3D 모델 생성 실패'})
                print("  ⚠️  모델 파일 생성 실패!")
        
        else:
            emit('agent_progress', {'step': '❌ 처리 실패'})
            error_message = f"❌ 오류: {result.get('message', 'Unknown error')}"
            emit('assistant_message', {'message': error_message})
    
    except Exception as e:
        emit('agent_progress', {'step': f'❌ 오류: {str(e)}'})
        error_message = f"❌ 오류 발생: {str(e)}"
        emit('assistant_message', {'message': error_message})


def extract_objects_from_agent(agent_instance):
    """Agent 히스토리에서 객체 추출"""
    objects = []
    
    for msg in agent_instance.messages:
        if msg.get('role') == 'tool':
            try:
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


if __name__ == '__main__':
    print("="*70)
    print("🌐 FreeCAD Web Viewer 시작")
    print("="*70)
    print()
    print(f"📡 서버: http://localhost:5000")
    print(f"🧠 모델: groq/openai/gpt-oss-20b")
    print(f"📁 작업 디렉토리: {work_dir}")
    print()
    print("웹 브라우저에서 http://localhost:5000 을 열어주세요!")
    print()
    
    # debug=False로 설정하여 auto-reload 비활성화 (models 폴더 변경 무시)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

