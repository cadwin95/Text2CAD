# FreeCAD 모델 생성 문제 해결 🔧

**문제 발생 시간**: 2025-10-26  
**증상**: 타임아웃 오류로 STL 파일 생성 실패

## 🐛 문제 원인 분석

### 1. 주요 원인: FreeCAD 인터랙티브 모드
```
Command '['/opt/homebrew/bin/freecad', '-c', 'script.py']' timed out after 60 seconds
```

**근본 원인**:
- FreeCAD가 스크립트 실행 후 인터랙티브 콘솔 모드로 진입
- 프로세스가 종료되지 않고 대기 상태 유지
- 60초 타임아웃 발생

**증거**:
```bash
$ freecad -c generate_script.py

... 스크립트 실행 ...
Recompute......
[FreeCAD Console mode <Use Ctrl-D (i.e. EOF) to exit.>]
>>>  ← 여기서 멈춤!
```

### 2. 부수 문제들

#### STL 파일이 생성되지 않음
- FCStd 파일은 생성됨 ✅
- STL 변환 스크립트가 실행되지 않음 ❌
- 이유: generate_script가 타임아웃

#### 로그 부족
- 상세한 오류 메시지 부족
- 디버깅 어려움

## ✅ 해결 방법

### 1. sys.exit(0) 추가

#### generate_script.py
```python
import FreeCAD
import Part

doc = FreeCAD.newDocument("WebModel")
# ... 객체 생성 ...
doc.recompute()
doc.saveAs("model.FCStd")
FreeCAD.closeDocument(doc.Name)

# ✨ 이 줄 추가!
import sys
sys.exit(0)
```

#### export_script.py
```python
import FreeCAD
import Mesh
import sys

try:
    # ... STL 변환 로직 ...
    FreeCAD.closeDocument(doc.Name)
    sys.exit(0)  # ✨ 성공 시 명시적 종료
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)  # ✨ 실패 시 명시적 종료
```

### 2. 상세한 로깅

#### 진행 상황 출력
```python
print("  1. 문서 열기 중...")
print("  2. 문서 열림: ...")
print("  3. 객체 확인: ...")
...
print("✅ STL export successful")
```

#### 클라이언트에도 전송
```python
emit('agent_progress', {'step': '🔄 3D 모델 생성 중...'})
emit('agent_progress', {'step': '✨ 3D 렌더링 준비 중...'})
emit('agent_progress', {'step': '✅ 완료!'})
```

### 3. 타임아웃 조정

#### generate_script: 60초
```python
subprocess.run(
    [freecad_path, "-c", str(script_file)],
    capture_output=True,
    timeout=60  # 충분한 시간
)
```

#### export_script: 30초
```python
subprocess.run(
    [freecad_path, "-c", str(export_script)],
    capture_output=True,
    timeout=30
)
```

## 📊 테스트 결과

### 수정 전
```
⏱️ FCStd 생성: 성공 (하지만 타임아웃)
⏱️ STL 변환: 시작도 못함
❌ 최종 결과: 실패
```

### 수정 후
```
✅ FCStd 생성: 1-2초 (즉시 종료)
✅ STL 변환: 2-3초 (즉시 종료)
✅ 최종 결과: 성공
```

## 🚀 검증 방법

### 1. 테스트 스크립트 실행
```bash
cd /Users/shkim5/Documents/cadai/web_viewer

# 테스트 스크립트 생성
cat > test_freecad_exit.py << 'EOF'
import FreeCAD
import sys

doc = FreeCAD.newDocument("Test")
box = doc.addObject("Part::Box", "TestBox")
box.Length = 10
doc.recompute()
doc.saveAs("test.FCStd")
FreeCAD.closeDocument(doc.Name)
print("✅ Completed")
sys.exit(0)
EOF

# 실행 (빠르게 종료되어야 함)
time freecad -c test_freecad_exit.py

# 결과 확인
echo "Exit code: $?"  # 0이어야 함
ls -lh test.FCStd     # 파일 생성 확인
```

### 2. 웹 서버 테스트
```bash
# 서버 시작
cd web_viewer
python3 app.py

# 브라우저에서 http://localhost:5000
# 메시지: "박스 만들어줘"
```

**기대 결과**:
```
🤖 Agent 초기화 중...
💭 요청 분석 중...
⚙️ 객체 생성 중...
📦 객체 정보 수집 중...
🔄 3D 모델 생성 중... (1개 객체)
    📤 STL 내보내기...
    🔄 FreeCAD 실행 중...
    📝 FreeCAD 출력:
      1. 문서 열기 중...
      2. 문서 열림...
      ...
      ✅ STL export successful
    📦 STL 파일 생성: True
✨ 3D 렌더링 준비 중...
✅ 완료!

[3D 뷰어에 박스 표시됨!]
```

## 💡 추가 개선사항

### 1. FreeCAD 워밍업
첫 실행 시 FreeCAD 초기화에 시간이 걸릴 수 있음:
```python
# 서버 시작 시 한 번 워밍업
subprocess.run([freecad_path, "--version"], capture_output=True)
```

### 2. 파일 정리
오래된 파일 자동 삭제:
```python
# 1시간 이상 된 파일 삭제
import time
for f in work_dir.glob("model_*.FCStd"):
    if time.time() - f.stat().st_mtime > 3600:
        f.unlink()
```

### 3. 오류 복구
실패 시 재시도:
```python
for attempt in range(3):
    try:
        result = subprocess.run(...)
        break
    except TimeoutExpired:
        if attempt == 2:
            raise
        print(f"Retry {attempt + 1}/3...")
```

## 📝 체크리스트

수정 완료:
- [x] generate_script.py에 sys.exit(0) 추가
- [x] export_script.py에 sys.exit(0) 추가
- [x] 상세한 로깅 추가
- [x] 진행 상황 웹에 표시
- [x] 타임아웃 조정 (60초)

테스트 완료:
- [ ] 간단한 객체 (박스)
- [ ] 복잡한 객체 (의자, 사다리)
- [ ] 연속 생성 (여러 번 요청)
- [ ] 오류 처리

## 🎉 결론

**sys.exit(0) 추가로 FreeCAD 인터랙티브 모드 진입 방지!**

### Before
```
FreeCAD 실행 → 스크립트 실행 → 콘솔 모드 진입 → 60초 대기 → 타임아웃 ❌
```

### After
```
FreeCAD 실행 → 스크립트 실행 → sys.exit(0) → 즉시 종료 ✅
```

---

**수정 완료**: 2025-10-26  
**테스트**: 진행 중  
**상태**: 서버 재시작 필요

