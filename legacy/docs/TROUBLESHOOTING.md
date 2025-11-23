# FreeCAD Web Viewer 문제 해결 가이드 🔧

## 🐛 일반적인 문제들

### 1. 메시지가 Agent로 전달되지 않음

#### 증상
- 채팅창에 메시지 입력 가능
- 하지만 응답이 없음
- 서버 터미널에 `📨 메시지 수신` 로그가 안 보임

#### 원인
- Socket.IO 연결 문제
- 이벤트 핸들러 미등록

#### 해결
1. **브라우저 콘솔 확인 (F12)**
   ```javascript
   // Socket.IO 연결 확인
   socket.connected  // true여야 함
   ```

2. **서버 터미널 확인**
   ```
   Client connected  // 이게 보여야 함
   ```

3. **테스트 페이지 사용**
   ```
   http://localhost:5000/test_socket.html
   ```

---

### 2. 서버가 계속 재시작됨

#### 증상
```
* Detected change in '.../models/generate_script.py', reloading
* Restarting with stat
```

#### 원인
- Flask debug 모드가 켜져 있음
- models 폴더의 파일 변경 감지

#### 해결 ✅
```python
# app.py 마지막 줄
socketio.run(app, host='0.0.0.0', port=5000, debug=False)
#                                            ^^^^^^^^^^^^
```

---

### 3. ModuleNotFoundError: No module named 'flask'

#### 증상
```
ModuleNotFoundError: No module named 'flask'
```

#### 원인
- venv가 활성화되지 않음
- 패키지 미설치

#### 해결
```bash
# 프로젝트 루트에서
source .venv/bin/activate

# 또는
cd /Users/shkim5/Documents/cadai/web_viewer
uv run python app.py
```

---

### 4. 3D 모델이 표시되지 않음

#### 증상
- 채팅은 작동
- 하지만 3D 뷰어에 아무것도 안 보임

#### 원인
- STL 변환 실패
- FreeCAD 경로 문제
- Three.js 로딩 실패

#### 해결
1. **서버 로그 확인**
   ```
   ✅ FreeCAD 업데이트 완료 (N개 객체)
   ```

2. **models 폴더 확인**
   ```bash
   ls -lh web_viewer/models/
   # .stl 파일이 있어야 함
   ```

3. **브라우저 콘솔 확인**
   ```javascript
   // Three.js 오류 확인
   // STL 로딩 오류 확인
   ```

---

### 5. Port 5000 already in use

#### 증상
```
OSError: [Errno 48] Address already in use
```

#### 원인
- 다른 프로세스가 5000 포트 사용 중

#### 해결
```bash
# 프로세스 찾기
lsof -i :5000

# 종료
kill -9 <PID>

# 또는 다른 포트 사용
# app.py에서 port=5001로 변경
```

---

## 🔍 디버깅 단계

### Step 1: 서버 로그 확인
```bash
cd /Users/shkim5/Documents/cadai/web_viewer
python3 app.py

# 다음이 보여야 함:
# ✅ 초기 문서 생성
# Client connected
```

### Step 2: 브라우저 콘솔 확인 (F12)
```javascript
// 다음 명령어 실행
socket.connected
// true가 나와야 함

// 이벤트 리스너 확인
socket.listeners('assistant_message')
// 함수가 나와야 함
```

### Step 3: 테스트 메시지 전송
```javascript
// 브라우저 콘솔에서
socket.emit('send_message', { message: '테스트' });

// 서버 터미널에서 다음이 보여야 함:
// 📨 메시지 수신: 테스트
```

### Step 4: Agent 응답 확인
```
서버 터미널:
  🤖 Agent 실행 시작...
  - Agent 초기화 중...
  - Agent 실행 중...
  - Agent 실행 완료: True
```

---

## 🚀 완전 초기화

모든 게 꼬였다면:

```bash
cd /Users/shkim5/Documents/cadai

# 1. 서버 종료
# Ctrl+C

# 2. venv 재생성
rm -rf .venv
uv venv
source .venv/bin/activate

# 3. 패키지 재설치
uv sync

# 4. models 폴더 정리
rm -rf web_viewer/models/*
mkdir -p web_viewer/models

# 5. 서버 재시작
cd web_viewer
python3 app.py
```

---

## 📊 정상 작동 체크리스트

### 서버 시작 시
- [ ] ✅ 초기 문서 생성 메시지
- [ ] ✅ "웹 브라우저에서..." 메시지
- [ ] ✅ 오류 없음

### 브라우저 접속 시
- [ ] ✅ 3D 뷰어 표시
- [ ] ✅ 채팅창 표시
- [ ] ✅ "연결됨" 상태 표시
- [ ] ✅ 콘솔 오류 없음

### 메시지 전송 시
- [ ] ✅ 서버: "📨 메시지 수신" 로그
- [ ] ✅ 서버: "🤖 Agent 실행 시작..." 로그
- [ ] ✅ 브라우저: 응답 메시지 표시
- [ ] ✅ 3D 뷰어: 모델 업데이트

---

## 🆘 그래도 안 되면

### 1. 테스트 페이지 사용
```
http://localhost:5000/test_socket.html
```

### 2. 간단한 명령어 테스트
```
메시지: clear
응답: ✅ 모든 객체가 삭제되었습니다.
```

### 3. Agent 없이 테스트
```python
# app.py에서 임시로
@socketio.on('send_message')
def handle_message(data):
    emit('assistant_message', {'message': '테스트 응답'})
```

### 4. 로그 레벨 증가
```python
# app.py 상단에 추가
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 💡 유용한 명령어

### 서버 상태 확인
```bash
# 포트 확인
lsof -i :5000

# 프로세스 확인
ps aux | grep python
```

### 파일 확인
```bash
# 생성된 모델 확인
ls -lh web_viewer/models/

# 스크립트 확인
cat web_viewer/models/generate_script.py
```

### 네트워크 확인
```bash
# localhost 연결 테스트
curl http://localhost:5000

# Socket.IO 테스트
curl http://localhost:5000/socket.io/
```

---

## 📞 더 도움이 필요하면

1. **서버 로그 전체 복사**
2. **브라우저 콘솔 로그 복사**
3. **재현 단계 기록**

그리고 다음 정보 제공:
- Python 버전: `python3 --version`
- 패키지 버전: `uv pip list | grep flask`
- OS 정보: `uname -a`

---

**최종 업데이트**: 2025-10-26  
**버전**: 1.0

