# 📁 파일 정리 계획

**현재 상태**: 루트 디렉토리에 너무 많은 파일이 섞여있음  
**목표**: 깔끔하고 논리적인 구조

---

## 📊 현재 파일 분석

### 루트 디렉토리
- **마크다운 문서**: 14개
- **Python 스크립트**: 13개
- **Shell 스크립트**: 4개 (.sh)
- **FreeCAD 파일**: 5개 (.FCStd) + 1개 (.FCBak)
- **설정 파일**: 5개 (docker-compose.yml, pyproject.toml 등)

### 문제점
❌ 루트 디렉토리가 지저분함  
❌ 문서와 코드가 섞여있음  
❌ 테스트 파일이 여기저기 흩어짐  
❌ 예제 파일 위치 불분명

---

## 🎯 새로운 구조 제안

```
/Users/shkim5/Documents/cadai/
├── 📄 README.md                    # 메인 README (유지)
├── 📄 QUICKSTART.md                # 빠른 시작 (유지)
├── 📄 TODO.md                      # TODO (유지)
├── 📄 CHANGELOG.md                 # 변경 이력 (유지)
│
├── 🔧 docker-compose.yml           # 설정 파일 (유지)
├── 🔧 litellm_config.yaml
├── 🔧 prometheus.yml
├── 🔧 pyproject.toml
├── 🔧 uv.lock
├── 🔧 env.template
│
├── 🚀 start_server.sh              # 주요 스크립트 (유지)
├── 🚀 stop_server.sh
│
├── 📁 docs/                        # ✨ 모든 문서
│   ├── PROJECT_STATUS.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── TROUBLESHOOTING.md
│   ├── COMPLEX_OBJECTS_PLAN.md
│   ├── FIX_SUMMARY.md
│   ├── PROBLEM_SOLVED.md
│   ├── FREECAD_SETUP.md
│   ├── FREECAD_GUI_GUIDE.md
│   ├── INTERACTIVE_MODE_GUIDE.md
│   ├── QUICK_START_GUIDE.md
│   └── web_viewer/                 # 웹 뷰어 문서 (이미 있음)
│       ├── README.md
│       ├── NEW_FEATURES.md
│       ├── OBJECT_MANAGEMENT.md
│       └── PROGRESS_FEATURE.md
│
├── 📁 tests/                       # ✨ 모든 테스트
│   ├── unit/                       # 단위 테스트
│   │   ├── test_freecad_tools.py
│   │   └── test_mcp_server.py
│   ├── integration/                # 통합 테스트
│   │   ├── test_agent.py
│   │   ├── test_agent_simple.py
│   │   ├── test_with_groq_oss.py
│   │   ├── test_finish_tool.py
│   │   ├── test_complex_objects.py
│   │   └── test_with_freecad_gui.py
│   ├── gui/                        # GUI 테스트
│   │   ├── test_interactive_gui.py
│   │   ├── test_gui_script.py
│   │   └── test_timeout_fix.py
│   └── results/                    # 테스트 결과 (기존)
│       ├── 01_compatibility_check.txt
│       ├── ...
│       └── TEST_SUMMARY.md
│
├── 📁 examples/                    # ✨ 예제 파일
│   ├── simple_box.FCStd
│   ├── simple_chair.FCStd
│   ├── positioned_objects.FCStd
│   ├── interactive_session.FCStd
│   ├── test_gui_autoopen.FCStd
│   ├── create_and_view_freecad.py  # 예제 스크립트
│   ├── interactive_freecad.py      # 인터랙티브 모드
│   └── setup_freecad_gui.py        # GUI 설정
│
├── 📁 scripts/                     # 유틸리티 스크립트 (기존)
│   ├── check_compatibility.py
│   ├── check_model_compatibility.py
│   ├── health_check.py
│   └── run_demo.py
│
├── 📁 src/                         # 소스 코드 (기존)
│   ├── agent/
│   ├── freecad_tools/
│   ├── mcp_server/
│   └── training/
│
├── 📁 web_viewer/                  # 웹 뷰어 (기존)
│   ├── app.py
│   ├── templates/
│   └── models/
│
├── 📁 data/                        # 데이터 (기존)
│   ├── synthetic/
│   └── logs/
│
└── 📁 freecad/                     # FreeCAD 소스 (서브모듈)
```

---

## 🔄 이동할 파일

### 1. 문서 → `docs/`
```bash
mkdir -p docs

# 주요 가이드 문서
mv PROJECT_STATUS.md docs/
mv IMPLEMENTATION_SUMMARY.md docs/
mv TROUBLESHOOTING.md docs/
mv COMPLEX_OBJECTS_PLAN.md docs/
mv FIX_SUMMARY.md docs/
mv PROBLEM_SOLVED.md docs/

# FreeCAD 관련 문서
mv FREECAD_SETUP.md docs/
mv FREECAD_GUI_GUIDE.md docs/
mv INTERACTIVE_MODE_GUIDE.md docs/

# 기타 가이드
mv QUICK_START_GUIDE.md docs/
```

### 2. 테스트 → `tests/`
```bash
# 테스트 디렉토리 재구성
mkdir -p tests/unit tests/integration tests/gui

# 단위 테스트 (이미 tests/에 있음)
# tests/test_freecad_tools.py (유지)
# tests/test_mcp_server.py (유지)
mv tests/test_*.py tests/unit/

# 통합 테스트
mv test_agent.py tests/integration/
mv test_agent_simple.py tests/integration/
mv test_with_groq_oss.py tests/integration/
mv test_finish_tool.py tests/integration/
mv test_complex_objects.py tests/integration/
mv test_with_freecad_gui.py tests/integration/

# GUI 테스트
mv test_interactive_gui.py tests/gui/
mv test_gui_script.py tests/gui/
mv test_timeout_fix.py tests/gui/

# 테스트 결과 (이미 있음)
# test_results/ → tests/results/ (이름 변경)
mv test_results tests/results
```

### 3. 예제 → `examples/`
```bash
mkdir -p examples

# FreeCAD 파일
mv simple_box.FCStd examples/
mv simple_chair.FCStd examples/
mv positioned_objects.FCStd examples/
mv interactive_session.FCStd examples/
mv test_gui_autoopen.FCStd examples/

# 예제 스크립트
mv create_and_view_freecad.py examples/
mv interactive_freecad.py examples/
mv setup_freecad_gui.py examples/
```

### 4. 삭제할 파일
```bash
# 백업 파일 (필요시 복구 가능)
rm interactive_session.*.FCBak

# 임시 파일
rm -f test.py  # 테스트용 임시 파일
rm -f idea.txt  # 메모 파일 (내용 확인 후)
```

### 5. 웹 뷰어 정리
```bash
cd web_viewer

# 테스트 파일 정리
rm -f test_*.py test_*.html

# 로그 파일은 gitignore 추가
```

---

## ✅ 정리 후 루트 디렉토리

```
/Users/shkim5/Documents/cadai/
├── README.md                # 📖 메인 문서
├── QUICKSTART.md
├── TODO.md
├── CHANGELOG.md
│
├── docker-compose.yml       # ⚙️ 설정
├── litellm_config.yaml
├── prometheus.yml
├── pyproject.toml
├── uv.lock
├── env.template
│
├── start_server.sh          # 🚀 주요 스크립트
├── stop_server.sh
│
├── docs/                    # 📚 문서
├── examples/                # 💡 예제
├── tests/                   # 🧪 테스트
├── scripts/                 # 🔧 스크립트
├── src/                     # 💻 소스 코드
├── web_viewer/              # 🌐 웹 뷰어
├── data/                    # 📊 데이터
└── freecad/                 # 🛠️ FreeCAD
```

**총 파일 수 (루트)**: ~14개 (현재 40개+에서 감소)

---

## 📝 업데이트 필요한 파일

### 1. README.md
```markdown
## 📁 프로젝트 구조

- `docs/` - 모든 문서
- `examples/` - 예제 및 데모
- `tests/` - 테스트 파일
- `scripts/` - 유틸리티 스크립트
- `src/` - 소스 코드
- `web_viewer/` - 웹 인터페이스
```

### 2. 스크립트 내 경로 수정
- `start_server.sh` - 경로 확인
- `stop_server.sh` - 경로 확인
- 테스트 파일 - import 경로 확인

### 3. .gitignore 추가
```
# Logs
web_viewer/server.log
*.log

# FreeCAD backups
*.FCBak

# Temporary files
test.py
idea.txt

# Test artifacts
*.pyc
__pycache__/
```

---

## 🚀 실행 계획

### 단계별 실행
1. ✅ 백업 생성 (선택적)
2. ✅ 새 디렉토리 생성
3. ✅ 문서 이동
4. ✅ 테스트 파일 이동
5. ✅ 예제 파일 이동
6. ✅ 불필요한 파일 삭제
7. ✅ README 업데이트
8. ✅ .gitignore 업데이트
9. ✅ 경로 수정 및 테스트

### 검증
- [ ] 서버 시작 확인
- [ ] 테스트 실행 확인
- [ ] 문서 링크 확인
- [ ] 예제 실행 확인

---

## ⚠️ 주의사항

1. **Git 상태 확인**: 커밋되지 않은 변경사항 확인
2. **백업**: 중요한 파일은 백업 생성
3. **경로 수정**: import 경로가 깨지지 않도록 주의
4. **테스트**: 정리 후 반드시 테스트 실행

---

**준비 완료!** 실행할까요?

