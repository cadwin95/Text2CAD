# FreeCAD Web Viewer 🌐🎨

**채팅창과 3D 뷰어를 함께 제공하는 웹 기반 FreeCAD 인터페이스**

## 🎯 특징

- ✅ **실시간 3D 뷰어**: Three.js 기반 웹 3D 렌더링
- ✅ **채팅 인터페이스**: Socket.IO로 실시간 양방향 통신
- ✅ **자동 업데이트**: 객체 생성 시 3D 뷰 즉시 반영
- ✅ **반응형 디자인**: 데스크톱/모바일 모두 지원
- ✅ **세션 유지**: 대화 컨텍스트 유지

## 🚀 빠른 시작

### 1. 서버 실행
```bash
cd /Users/shkim5/Documents/cadai/web_viewer
python3 app.py
```

### 2. 브라우저 열기
```
http://localhost:5000
```

### 3. 채팅 시작!
```
👤: 10x10x10 박스를 만들어줘
🤖: ✅ 1개 객체가 생성되었습니다.
[왼쪽 3D 뷰어에 박스 표시됨]
```

## 📺 화면 구성

```
┌─────────────────────────────────┬─────────────────┐
│                                 │  💬 Chat        │
│                                 │  ┌───────────┐  │
│         🎨 3D Viewer            │  │ Messages  │  │
│      (Three.js 렌더링)           │  │           │  │
│                                 │  │           │  │
│  - 마우스: 회전                  │  │           │  │
│  - 휠: 확대/축소                 │  └───────────┘  │
│  - 실시간 업데이트               │  [입력창]      │
│                                 │  [전송]        │
└─────────────────────────────────┴─────────────────┘
```

## 💬 사용 예시

### 기본 객체 생성
```
👤: 10x10x10 박스를 만들어줘
👤: 박스 옆에 실린더 추가해줘. 반지름 5, 높이 20
👤: 구도 추가해줘. 반지름 8
```

### 복잡한 구조
```
👤: 간단한 의자를 만들어줘
👤: 의자 옆에 테이블도 추가해줘
```

### 특수 명령어
```
👤: clear (또는 초기화)
🤖: ✅ 모든 객체가 삭제되었습니다.
```

## 🔧 기술 스택

### 백엔드
- **Flask**: 웹 서버
- **Flask-SocketIO**: 실시간 통신
- **FreeCAD Python API**: 3D 모델 생성
- **ToolCallingAgent**: LLM 기반 자연어 처리

### 프론트엔드
- **Three.js**: 3D 렌더링
- **Socket.IO Client**: 실시간 통신
- **STLLoader**: STL 파일 로딩
- **OrbitControls**: 3D 뷰 조작

## 📁 파일 구조

```
web_viewer/
├── app.py                  # Flask 서버 (백엔드)
├── templates/
│   └── index.html         # 웹 인터페이스 (프론트엔드)
├── models/                # 생성된 3D 모델 (STL, FCStd)
└── README.md             # 이 파일
```

## 🎨 작동 방식

### 1. 사용자 입력
```
사용자: "10x10x10 박스를 만들어줘"
  ↓ (Socket.IO)
백엔드: send_message 이벤트 수신
```

### 2. Agent 처리
```
백엔드: ToolCallingAgent 실행
  ↓
Agent: freecad_create_box(10, 10, 10) 호출
  ↓
백엔드: 객체 정보 저장
```

### 3. 3D 모델 생성
```
백엔드: FreeCAD Python 스크립트 생성
  ↓
FreeCAD: .FCStd 파일 생성
  ↓
백엔드: STL로 변환
```

### 4. 클라이언트 업데이트
```
백엔드: model_update 이벤트 전송
  ↓ (Socket.IO)
프론트엔드: Three.js로 STL 로딩
  ↓
3D 뷰어: 모델 렌더링
```

## 🎮 3D 뷰어 조작

| 동작 | 방법 |
|------|------|
| **회전** | 마우스 왼쪽 버튼 드래그 |
| **이동** | 마우스 오른쪽 버튼 드래그 |
| **확대/축소** | 마우스 휠 |
| **자동 회전** | 현재 미구현 (추가 예정) |

## 🚧 현재 제한사항

### 1. STL 변환
- 모든 객체를 하나의 STL 파일로 합침
- 색상 정보 미지원 (STL 제한)

### 2. 실시간 리로드
- 매번 페이지를 새로고침할 필요는 없음
- STL 파일 캐시 문제는 타임스탬프로 해결

### 3. 객체 개별 조작
- 현재는 전체 모델만 표시
- 개별 객체 선택/수정은 미구현

## 🚀 고급 기능 (예정)

### 1. 실시간 협업
```python
# 여러 사용자가 동시에 작업
# 각 사용자의 변경사항을 실시간 동기화
```

### 2. 객체 선택 및 수정
```python
# 3D 뷰어에서 객체 클릭
# 채팅창에서 "선택된 객체를 빨간색으로 변경해줘"
```

### 3. 카메라 프리셋
```python
# "정면 보기", "위에서 보기" 등 버튼 추가
```

### 4. 스크린샷 캡처
```python
# 현재 뷰를 이미지로 저장
```

### 5. VR/AR 지원
```python
# WebXR API 사용
```

## 🐛 문제 해결

### 문제: 3D 모델이 표시되지 않음
```bash
# 1. 서버 로그 확인
# 2. models/ 디렉토리에 STL 파일 확인
# 3. 브라우저 콘솔 확인 (F12)
```

### 문제: Socket.IO 연결 실패
```bash
# 1. 포트 5000이 이미 사용 중인지 확인
lsof -i :5000

# 2. 다른 포트 사용
# app.py에서 port=5001로 변경
```

### 문제: FreeCAD 스크립트 오류
```bash
# 1. FreeCAD 경로 확인
which freecad

# 2. app.py에서 freecad_path 수정
freecad_path = "/your/path/to/freecad"
```

## 📊 성능

### 권장 사양
- **메모리**: 2GB 이상
- **브라우저**: Chrome/Firefox/Safari 최신 버전
- **네트워크**: localhost (로컬)

### 렌더링 성능
- **10개 객체**: 즉시 렌더링
- **50개 객체**: 1-2초
- **100개 객체**: 3-5초

## 🎉 데모 스크립트

### 자동 데모
```bash
cd /Users/shkim5/Documents/cadai

# 서버 시작
python3 web_viewer/app.py &

# 브라우저 열기
open http://localhost:5000

# 또는 직접 실행
```

## 📝 개발 로그

### 버전 1.0 (2025-10-26)
- ✅ 기본 웹 인터페이스 구현
- ✅ Three.js 3D 뷰어 통합
- ✅ Socket.IO 실시간 통신
- ✅ FreeCAD STL 내보내기
- ✅ Agent 통합

## 🤝 기여

### 개선 아이디어
1. 객체별 색상 지정
2. 애니메이션 효과
3. 측정 도구 (거리, 각도)
4. 단면 보기
5. 다중 뷰포트

## 📚 참고 자료

- [Three.js Documentation](https://threejs.org/docs/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [FreeCAD Python API](https://wiki.freecad.org/Python_scripting_tutorial)

---

**만든 날짜**: 2025-10-26  
**버전**: 1.0.0  
**라이선스**: MIT

## 🚀 바로 시작하기

```bash
# 1. 서버 시작
cd /Users/shkim5/Documents/cadai/web_viewer
python3 app.py

# 2. 브라우저에서
# http://localhost:5000

# 3. 채팅창에 입력
# "10x10x10 박스를 만들어줘"
```

**즐거운 3D 모델링 되세요!** 🎨✨

