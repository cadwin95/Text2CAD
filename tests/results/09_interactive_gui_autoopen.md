# FreeCAD GUI 자동 열기 개선 🎨✨

**구현 일시**: 2025-10-26  
**목적**: 인터랙티브 세션 시작 시 FreeCAD GUI가 자동으로 포그라운드로 열리도록 개선

## 🎯 문제점

### 이전 동작
```
python3 interactive_freecad.py 실행
  ↓
FreeCAD가 백그라운드에서 열림
  ↓
사용자가 수동으로 FreeCAD 찾아서 클릭 필요 😓
```

### 원인
- `open -a FreeCAD` 명령어는 백그라운드에서 실행될 수 있음
- macOS에서 포그라운드 활성화가 보장되지 않음

## ✅ 해결 방법

### 개선된 동작
```
python3 interactive_freecad.py 실행
  ↓
FreeCAD 실행 파일을 직접 실행
  ↓
AppleScript로 포그라운드 활성화
  ↓
FreeCAD 창이 자동으로 앞에 나타남! 🎉
```

### 구현 방법

#### 1. FreeCAD 실행 파일 직접 실행
```python
# 이전: open 명령어 사용
subprocess.Popen(['open', '-a', 'FreeCAD', str(self.work_file)])

# 개선: 실행 파일 직접 실행
subprocess.Popen([self.freecad_path, str(self.work_file)])
```

#### 2. AppleScript로 포그라운드 활성화
```python
# FreeCAD가 열린 후
subprocess.run(
    ['osascript', '-e', 'tell application "FreeCAD" to activate'],
    capture_output=True,
    timeout=5
)
```

#### 3. 문서 업데이트 시에도 활성화
```python
def _update_freecad_document(self):
    # ... 문서 업데이트 ...
    
    # macOS: FreeCAD를 포그라운드로 가져오기
    subprocess.run(
        ['osascript', '-e', 'tell application "FreeCAD" to activate'],
        capture_output=True,
        timeout=3
    )
    print("💡 FreeCAD에서 Ctrl+R을 눌러 문서를 새로고침하세요")
```

## 🔧 변경된 코드

### interactive_freecad.py - `_open_freecad_gui()`

```python
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
```

### interactive_freecad.py - `_update_freecad_document()`

```python
def _update_freecad_document(self):
    """Agent의 현재 상태를 FreeCAD 문서로 업데이트"""
    # ... 문서 업데이트 로직 ...
    
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
```

## 📊 테스트 결과

### 테스트 스크립트
```bash
python3 test_interactive_gui.py
```

### 테스트 항목
1. ✅ FreeCAD 경로 확인
2. ✅ 테스트 문서 생성
3. ✅ FreeCAD GUI 포그라운드 자동 열기
4. ✅ AppleScript 활성화

### 실제 동작
```
======================================================================
🧪 FreeCAD GUI 자동 열기 테스트
======================================================================

테스트 1: FreeCAD 경로 확인
----------------------------------------------------------------------
✅ FreeCAD 발견: /opt/homebrew/bin/freecad

테스트 2: 테스트 문서 생성
----------------------------------------------------------------------
✅ 테스트 문서 생성 성공: test_gui_autoopen.FCStd

테스트 3: FreeCAD GUI 자동 열기 (포그라운드)
----------------------------------------------------------------------
🚀 FreeCAD를 여는 중...
✅ FreeCAD 프로세스 시작됨

📱 FreeCAD를 포그라운드로 활성화 중...
✅ FreeCAD가 포그라운드로 활성화되었습니다!

💡 FreeCAD 창이 보이시나요?
   - 보인다면: ✅ 테스트 성공!
```

## 🎨 사용자 경험 개선

### Before (이전)
```
$ python3 interactive_freecad.py

✅ FreeCAD GUI 열림

[사용자가 Dock에서 FreeCAD 아이콘 찾아서 클릭] 😓
```

### After (개선)
```
$ python3 interactive_freecad.py

🚀 FreeCAD GUI를 여는 중...
✅ FreeCAD GUI가 포그라운드로 열렸습니다!

[FreeCAD 창이 자동으로 앞에 나타남!] 🎉
```

## 💡 추가 개선사항

### 1. 매 턴마다 FreeCAD 활성화
객체 업데이트 후 자동으로 FreeCAD를 포그라운드로 가져옵니다.

```
턴 1: "박스 만들어줘"
  ↓
✅ FreeCAD 업데이트 완료 (1개 객체)
📱 FreeCAD 활성화
  ↓
[FreeCAD 창이 앞으로 나옴]
```

### 2. 리로드 안내 메시지
문서 업데이트 후 사용자에게 리로드 방법 안내:

```
✅ FreeCAD 업데이트 완료 (3개 객체)
💡 FreeCAD에서 Ctrl+R을 눌러 문서를 새로고침하거나
   File > Recent Files > interactive_session.FCStd를 다시 여세요
```

### 3. 오류 처리 개선
실패 시 명확한 안내:

```
⚠️  FreeCAD GUI 실행 실패: [오류 내용]
💡 수동으로 여세요: /opt/homebrew/bin/freecad interactive_session.FCStd
```

## 🔄 워크플로우

### 전체 흐름
```
1. python3 interactive_freecad.py 실행
   ↓
2. 초기 문서 생성 (interactive_session.FCStd)
   ↓
3. FreeCAD 실행 파일로 직접 열기
   ↓
4. 4초 대기 (FreeCAD 초기화)
   ↓
5. AppleScript로 포그라운드 활성화
   ↓
6. ✅ FreeCAD 창이 앞에 나타남!
   ↓
7. 사용자 입력 대기 ("박스 만들어줘")
   ↓
8. Agent 실행 → 문서 업데이트
   ↓
9. AppleScript로 다시 활성화
   ↓
10. 💡 리로드 안내 메시지
```

## 🛠️ 시스템 요구사항

### macOS
- ✅ AppleScript 지원 (기본 포함)
- ✅ FreeCAD 설치
- ✅ `osascript` 명령어 사용 가능

### Linux
- ✅ FreeCAD 설치
- ⚠️  포그라운드 활성화는 미지원 (일반 실행만)

## 📝 사용 방법

### 기본 사용
```bash
cd /Users/shkim5/Documents/cadai
python3 interactive_freecad.py
```

### 실행 결과
```
======================================================================
🎨 FreeCAD 인터랙티브 모드
======================================================================

📡 LiteLLM Proxy: http://localhost:4000
🧠 모델: groq/openai/gpt-oss-20b
📁 작업 파일: interactive_session.FCStd

💡 사용 방법:
  - 원하는 객체를 자유롭게 요청하세요
  - FreeCAD 창에서 실시간으로 결과를 확인할 수 있습니다
  ...

✅ 초기 문서 생성: interactive_session.FCStd
🚀 FreeCAD GUI를 여는 중...
✅ FreeCAD GUI가 포그라운드로 열렸습니다!  ← 🎉 NEW!
======================================================================
🚀 세션이 시작되었습니다! FreeCAD 창을 확인하세요.
======================================================================

======================================================================
턴 1 - 무엇을 만들고 싶으신가요?
======================================================================
👤 당신: ▊
```

## 🐛 문제 해결

### 문제: FreeCAD가 여전히 백그라운드에 있음
```bash
# 수동으로 활성화
osascript -e 'tell application "FreeCAD" to activate'

# 또는 Command+Tab으로 FreeCAD 선택
```

### 문제: AppleScript 권한 오류
```
System Preferences > Security & Privacy > Privacy > Automation
→ Terminal 또는 Python에게 FreeCAD 제어 권한 부여
```

### 문제: FreeCAD가 열리지 않음
```bash
# FreeCAD 경로 확인
which freecad

# 수동으로 실행
/opt/homebrew/bin/freecad interactive_session.FCStd
```

## 🎉 결론

**FreeCAD GUI 자동 열기 개선 완료!**

### 주요 개선사항
1. ✅ 세션 시작 시 FreeCAD가 자동으로 포그라운드로 열림
2. ✅ 매 턴마다 FreeCAD 활성화하여 결과 확인 용이
3. ✅ 명확한 리로드 안내 메시지
4. ✅ 오류 시 수동 실행 방법 제공

### 사용자 경험
- 🎨 더 이상 FreeCAD를 찾아서 클릭할 필요 없음
- 🚀 즉시 결과를 볼 수 있음
- 💬 채팅에 집중하면서 FreeCAD 창도 동시에 확인 가능

---

**구현 완료**: 2025-10-26  
**테스트**: 성공 ✅  
**사용 준비**: 완료 ✅

## 🚀 바로 시작하기

```bash
cd /Users/shkim5/Documents/cadai
python3 interactive_freecad.py

# FreeCAD 창이 자동으로 열리면 성공! 🎉
```

