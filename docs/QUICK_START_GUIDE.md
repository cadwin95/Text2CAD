# 🚀 빠른 시작 가이드

FreeCAD Web Viewer를 쉽게 시작하고 종료하는 방법입니다.

---

## ⚡ 간단한 사용법

### 서버 시작
```bash
cd /Users/shkim5/Documents/cadai
./start_server.sh
```

**또는**:
```bash
bash start_server.sh
```

### 서버 종료

#### 방법 1: 웹 인터페이스에서 (권장)
1. 브라우저에서 http://localhost:5000 접속
2. 우측 상단 "🛑 종료" 버튼 클릭
3. 확인 클릭

#### 방법 2: 터미널에서 Ctrl+C
서버가 실행 중인 터미널에서:
```
Ctrl + C
```

#### 방법 3: 스크립트로 종료
새 터미널 창에서:
```bash
cd /Users/shkim5/Documents/cadai
./stop_server.sh
```

---

## 📋 상세 가이드

### 1. 서버 시작하기

```bash
cd /Users/shkim5/Documents/cadai
./start_server.sh
```

**출력 예시**:
```
🚀 FreeCAD Web Viewer 시작 중...

======================================================================
🌐 FreeCAD Web Viewer 시작
======================================================================

📡 서버: http://localhost:5000
🧠 모델: groq/openai/gpt-oss-20b
📁 작업 디렉토리: /Users/shkim5/Documents/cadai/web_viewer/models

웹 브라우저에서 http://localhost:5000 을 열어주세요!

 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### 2. 웹 브라우저 열기

서버가 시작되면 브라우저에서 접속:
```
http://localhost:5000
```

### 3. 사용하기

#### 새로운 모델 만들기
채팅창에 입력:
```
박스 만들어줘
의자 만들어줘
10x20x30 크기의 실린더 만들어줘
```

#### 이전 모델 불러오기
1. 우측 상단 "📁 파일" 버튼 클릭
2. 원하는 파일 선택
3. 3D 뷰어에서 확인

### 4. 서버 종료하기

#### 웹에서 종료 (가장 깔끔함)
```
1. 우측 상단 "🛑 종료" 버튼
2. "정말로 서버를 종료하시겠습니까?" → 확인
3. "✅ 서버가 종료되었습니다." 메시지 확인
```

#### 터미널에서 종료
서버 실행 중인 터미널에서:
```
Ctrl + C
```

#### 스크립트로 강제 종료
```bash
./stop_server.sh
```

---

## 🔧 문제 해결

### 문제 1: "Address already in use" 오류

**증상**:
```
Address already in use
Port 5000 is in use by another program.
```

**해결**:
```bash
./stop_server.sh
./start_server.sh
```

### 문제 2: 서버가 응답하지 않음

**확인**:
```bash
# 서버 프로세스 확인
lsof -i :5000

# 없으면 다시 시작
./start_server.sh
```

### 문제 3: 웹 페이지가 로드되지 않음

**확인 사항**:
1. 서버가 실행 중인지 확인
2. 브라우저 캐시 삭제
3. http://localhost:5000 (https 아님!)
4. 방화벽 설정 확인

### 문제 4: 백그라운드 프로세스가 남아있음

**강제 정리**:
```bash
# 모든 서버 프로세스 종료
./stop_server.sh

# 확인
lsof -i :5000  # 아무것도 안 나와야 함
```

---

## 📁 스크립트 설명

### start_server.sh
```bash
#!/bin/bash
# 1. 기존 서버 종료 (충돌 방지)
# 2. 새 서버 시작 (포그라운드)
# 3. Ctrl+C로 깔끔하게 종료 가능
```

**특징**:
- ✅ 자동으로 기존 서버 정리
- ✅ 포그라운드 실행 (로그 실시간 확인)
- ✅ Ctrl+C로 안전하게 종료

### stop_server.sh
```bash
#!/bin/bash
# 1. 5000번 포트 사용 프로세스 종료
# 2. Flask 앱 프로세스 정리
# 3. 완전히 종료되었는지 확인
```

**특징**:
- ✅ 모든 관련 프로세스 정리
- ✅ 깔끔한 종료
- ✅ 다음 실행을 위한 준비

---

## 🎯 권장 워크플로우

### 개발/테스트 중
```bash
# 터미널 1
./start_server.sh

# 작업 완료 후
Ctrl + C
```

### 긴 시간 사용
```bash
# 서버 시작
./start_server.sh

# 브라우저에서 작업...

# 웹 UI에서 "🛑 종료" 버튼으로 종료
```

### 문제 발생 시
```bash
# 모든 프로세스 강제 종료
./stop_server.sh

# 깨끗하게 다시 시작
./start_server.sh
```

---

## 💡 팁

### 1. 터미널 탭 관리
```
탭 1: 서버 실행 (./start_server.sh)
탭 2: 개발 작업 (코드 수정 등)
```

### 2. 자동 브라우저 열기
`start_server.sh`에 추가 가능:
```bash
# macOS
open http://localhost:5000

# Linux
xdg-open http://localhost:5000
```

### 3. 로그 파일 저장
```bash
./start_server.sh 2>&1 | tee server.log
```

### 4. 백그라운드 실행 (비권장)
포그라운드 실행을 권장하지만, 필요하다면:
```bash
nohup ./start_server.sh > server.log 2>&1 &

# 종료
./stop_server.sh
```

---

## 📊 비교

| 방법 | 장점 | 단점 | 추천 |
|------|------|------|------|
| **start_server.sh** | 간단, 로그 실시간 | 터미널 점유 | ⭐⭐⭐⭐⭐ |
| **웹 UI 종료** | 가장 깔끔 | 서버가 살아있어야 함 | ⭐⭐⭐⭐⭐ |
| **Ctrl+C** | 빠름 | 터미널 필요 | ⭐⭐⭐⭐ |
| **stop_server.sh** | 강제 종료 | 약간 거침 | ⭐⭐⭐ |

---

## 🎉 요약

### 시작
```bash
./start_server.sh
```

### 종료
```
웹 UI에서 "🛑 종료" 또는 Ctrl+C
```

### 문제 해결
```bash
./stop_server.sh
./start_server.sh
```

**그게 다입니다!** 🚀

---

**작성일**: 2025-10-26  
**업데이트**: 2025-10-26

