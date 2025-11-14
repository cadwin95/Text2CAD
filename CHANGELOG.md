# 📝 CHANGELOG

프로젝트의 모든 주요 변경사항을 기록합니다.

---

## [2025-10-26] - 프로젝트 시작 및 초기 개발

### 🎉 Added - 새로운 기능

#### 인프라 및 설정
- Docker Compose 설정 (llama.cpp, litellm-proxy, postgres, prometheus)
- LiteLLM 프록시 설정 파일 (`litellm_config.yaml`)
- 환경 변수 템플릿 (`.env.template`)
- `pyproject.toml` 의존성 관리 (uv 사용)
- Groq OSS 모델 라우팅 추가

#### FreeCAD 통합
- FreeCAD primitives 도구 (box, cylinder, sphere, cone)
- Position 파라미터 (x, y, z) 추가
- Rotation 파라미터 추가
- FreeCAD 문서 관리 (생성, 저장, 정보)
- 시뮬레이션 모드 (FreeCAD 없이도 동작)
- FreeCAD GUI 자동 열기 (macOS)
- macOS AppleScript로 포그라운드 활성화

#### MCP 서버
- FastMCP 서버 구현
- FreeCAD 도구를 OpenAI function calling 형식으로 노출
- Tool 스키마 자동 생성

#### Tool-Calling Agent
- 핵심 Agent 로직 구현
- LiteLLM과 통합
- 대화 히스토리 관리
- 도구 실행 및 결과 처리
- `finish` 도구 추가 (명시적 종료)
- max_iterations 16턴으로 확장
- 모델 이름 표시

#### 합성 데이터 및 Fine-tuning
- OpenPipe 형식 합성 데이터 생성
- FreeCAD 명령어를 tool_calls로 변환
- Position 파라미터 파싱
- Unsloth fine-tuning 스크립트
- Vision 모듈 placeholder

#### Interactive Mode
- 인터랙티브 FreeCAD 세션
- 연속 채팅 지원
- FreeCAD GUI 실시간 업데이트
- 세션 파일 관리

#### 웹 뷰어
- Flask 웹 서버
- Socket.IO 실시간 통신
- Three.js 3D 렌더링
- STL 파일 변환 및 표시
- 채팅 인터페이스
- Agent 진행 상황 실시간 표시
- 파일 브라우저 (이전 모델 로드)
- 서버 종료 버튼 (웹 UI)
- 새 문서 생성 버튼
- 객체 목록 패널
- 개별 객체 삭제 기능

#### 유틸리티 스크립트
- 호환성 체크 (`check_compatibility.py`)
- 모델 호환성 테스트 (`check_model_compatibility.py`)
- 헬스 체크 (`health_check.py`)
- 간편 서버 시작 (`start_server.sh`)
- 간편 서버 종료 (`stop_server.sh`)

#### 테스트
- 기본 Agent 테스트
- Groq OSS 모델 테스트
- finish 도구 테스트
- 복잡한 객체 생성 테스트 (의자, 사다리, 테이블)
- FreeCAD GUI 테스트
- Interactive mode 테스트

#### 문서
- README.md (프로젝트 개요)
- QUICKSTART.md (빠른 시작)
- QUICK_START_GUIDE.md (서버 관리)
- IMPLEMENTATION_SUMMARY.md (구현 요약)
- FREECAD_SETUP.md (FreeCAD 설치)
- FREECAD_GUI_GUIDE.md (GUI 통합)
- INTERACTIVE_MODE_GUIDE.md (인터랙티브 모드)
- COMPLEX_OBJECTS_PLAN.md (복잡한 객체 계획)
- FIX_SUMMARY.md (수정 요약)
- PROBLEM_SOLVED.md (문제 해결 상세)
- TROUBLESHOOTING.md (문제 해결 가이드)
- web_viewer/README.md (웹 뷰어 가이드)
- web_viewer/PROGRESS_FEATURE.md (진행 상황 표시)
- web_viewer/NEW_FEATURES.md (새 기능)
- web_viewer/OBJECT_MANAGEMENT.md (객체 관리)
- PROJECT_STATUS.md (프로젝트 진행 상황)
- CHANGELOG.md (이 문서)

### 🔧 Changed - 변경사항

#### 파라미터 확장
- `create_box()`: length, width, height → + x, y, z, rotation, name
- `create_cylinder()`: radius, height → + x, y, z, rotation, name
- `create_sphere()`: radius → + x, y, z, name
- `create_cone()`: radius1, radius2, height → + x, y, z, rotation, name

#### 설정 변경
- max_iterations: 5 → 16턴
- FreeCAD 스크립트 타임아웃: 10초 → 60초 (generate), 30초 (export)
- LiteLLM 모델 설정: Groq OSS 추가

#### UI/UX 개선
- 채팅 헤더: 버튼 3개 추가 (새문서, 파일, 종료)
- 3D 뷰어: 객체 목록 패널 추가 (좌측 하단)
- Agent 응답: 진행 단계 실시간 표시

### 🐛 Fixed - 버그 수정

#### Critical Fixes
- **FreeCAD 인터랙티브 모드 타임아웃**: `sys.exit(0)` 추가로 60초+ → 2-4초
- **이모지 인코딩 오류**: ASCII 오류 방지를 위해 영어로 변경
- **합성 데이터 tool_calls 비어있음**: Regex 파싱 및 tool_call 생성 로직 추가
- **Groq OSS tool validation 실패**: litellm_config.yaml에 groq-oss 모델 재추가

#### Minor Fixes
- LiteLLM authentication: `.env`에 `LITELLM_API_KEY` 추가
- Flask Werkzeug 경고: `allow_unsafe_werkzeug=True` 추가
- 백그라운드 프로세스 관리: 시작/종료 스크립트로 해결
- FreeCAD 문서 저장: `.FCStd` 확장자 자동 처리, 디렉토리 생성
- Interactive mode 타임아웃: 60초로 증가

### 🚀 Performance - 성능 개선

- FreeCAD 스크립트 실행: **15배 빠름** (60초+ → 2-4초)
- STL 변환: 자동 캐싱으로 중복 변환 방지
- 객체 목록: 실시간 업데이트로 서버 부하 최소화

### 🔒 Security - 보안

- `.env` 파일 gitignore 추가
- API 키 환경 변수로 관리
- 서버 종료 확인 대화상자

### 📚 Documentation - 문서

- **15개 이상의 가이드 문서** 작성
- 모든 주요 기능에 대한 상세 설명
- 코드 예제 및 스크린샷
- 문제 해결 가이드
- API 문서 (MCP 서버)

---

## 버전 기록

### v0.1.0 - 초기 인프라 (2025-10-26 오전)
- Docker Compose 설정
- LiteLLM 프록시
- FreeCAD 기본 도구
- MCP 서버

### v0.2.0 - Agent 구현 (2025-10-26 오전)
- Tool-calling Agent
- 합성 데이터 생성
- Fine-tuning 준비

### v0.3.0 - Position 파라미터 (2025-10-26 오후)
- x, y, z 좌표 추가
- rotation 파라미터
- 복잡한 객체 생성 가능

### v0.4.0 - GUI 통합 (2025-10-26 오후)
- FreeCAD GUI 자동 열기
- Interactive mode
- macOS 포그라운드 활성화

### v0.5.0 - 문제 해결 (2025-10-26 저녁)
- 타임아웃 문제 해결
- 이모지 인코딩 수정
- 15배 성능 개선

### v1.0.0 - 웹 뷰어 (2025-10-26 저녁)
- Flask + Socket.IO + Three.js
- 채팅 인터페이스
- 3D 렌더링
- 실시간 진행 상황

### v1.1.0 - 파일 관리 (2025-10-26 밤)
- 파일 브라우저
- 서버 종료 버튼
- 시작/종료 스크립트

### v1.2.0 - 객체 관리 (2025-10-26 밤)
- 새 문서 생성
- 객체 목록 패널
- 개별 객체 삭제

---

## 다음 버전 계획

### v1.3.0 - Fine-tuning (예정)
- [ ] OpenPipe 데이터 업로드
- [ ] Fine-tuning 실행
- [ ] Fine-tuned 모델 테스트

### v1.4.0 - 고급 도구 (예정)
- [ ] Boolean operations
- [ ] Fillet/Chamfer
- [ ] Extrude/Revolve

### v2.0.0 - Vision 통합 (예정)
- [ ] LLaVA 또는 Qwen-VL
- [ ] 이미지 기반 수정
- [ ] 시각적 피드백

---

## 기여자

- **shkim5** - 프로젝트 오너, 주요 개발자
- **AI Assistant (Claude Sonnet 4.5)** - 코드 구현, 문서 작성, 디버깅

---

**포맷**: [YYYY-MM-DD] - 제목
- Added: 새로운 기능
- Changed: 기존 기능 변경
- Fixed: 버그 수정
- Performance: 성능 개선
- Security: 보안 관련
- Documentation: 문서 변경

**Semantic Versioning**: MAJOR.MINOR.PATCH
- MAJOR: 호환되지 않는 API 변경
- MINOR: 하위 호환되는 기능 추가
- PATCH: 하위 호환되는 버그 수정


