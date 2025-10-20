# FreeCAD Runtime & Visualization Guide

- 목적: FreeCAD 소스를 로컬에서 빌드하고 LiteLLM Proxy + LLM 백엔드를 통해 에이전트가 CAD 작업을 자동화하도록 한다.
- 결론: `freecad/`에서 FreeCADCmd를 빌드하고 `.env`에 경로/키를 정의한 뒤, LiteLLM Proxy(4000)와 llama.cpp 서버(8080)를 기동해 `app.cli`를 실행한다.

## FreeCAD 소스 위치
- 루트: `freecad/`
- 주요 바이너리: `freecad/build/debug/bin/FreeCADCmd`, `freecad/build/debug/bin/FreeCAD`

## 빌드 준비
1. 기존 가상환경이 있다면 비활성화 후 새 셸을 연다.
2. `cd freecad`
3. (최초 1회) `curl -Ls https://pixi.sh/install.sh | bash`
4. 의존성 설치: `pixi install`
5. CMake 설정: `pixi run configure`
6. 빌드: `pixi run build-debug`

## 환경 변수
루트 `.env`에 아래 예시를 추가한다.
```
FREECAD_CMD=/Users/shkim5/Documents/cadai/freecad/build/debug/bin/FreeCADCmd
OPENAI_API_KEY=...
GROQ_API_KEY=...
```
`app/utils/env.load_env()`가 자동으로 읽어 사용한다.

## LiteLLM Proxy & LLM 백엔드
### Docker Compose (권장)
```
docker compose up -d litellm-proxy llama-server
```
- `litellm-proxy`: 4000 포트에서 OpenAI 호환 LiteLLM Proxy.
- `llama-server`: 8080 포트에서 OpenAI 스타일 llama.cpp 서버.
- `curl http://localhost:4000/v1/models`로 모델 목록을 확인한다.
- Compose는 `ghcr.io/berriai/litellm:v1.77.5-stable` 이미지를 고정 사용하며 호스트/컨테이너 모두 4000 포트에 바인딩된다.
- 모델 라우팅은 `litellm_config.yaml`에서 관리하며 `OPENAI_CHAT_MODEL`, `GROQ_MODEL`, `LLAMACPP_MODEL`, `LLAMACPP_API_KEY` 환경 변수로 손쉽게 오버라이드할 수 있다(지정하지 않으면 파일의 기본값이 적용된다).

### 수동 실행 (대안)
```
uv pip install "litellm[proxy]"
uv run litellm --config litellm_config.yaml --host 0.0.0.0 --port 4000
```
- 동시에 `docker compose up llama-server`로 로컬 모델을 띄운다.
- 기본 URL은 `http://localhost:4000/v1`이며 `.env`에서 `LITELLM_PROXY_URL`로 오버라이드 가능.

## 에이전트 실행
- 기본(OpenAI 통한 프록시):
  ```bash
  python3 -m app.cli --demo-freecad --transcript-path /tmp/cadai_proxy_demo.txt
  ```
- 로컬 llama.cpp 모델(프록시 → llama.cpp):
  ```bash
  python3 -m app.cli --local --demo-freecad --transcript-path /tmp/cadai_local_proxy.txt
  ```
- transcript에는 시스템 메시지, LLM JSON 응답, `freecad.create_box` 실행 결과가 기록된다.
- OpenAI/Groq 계정 한도가 부족하면 프록시에서 429(Quota) 오류가 날 수 있으니 주의한다.

## 통합 테스트
```
pytest -m "integration"
```
`FREECAD_CMD`가 설정되지 않았으면 테스트가 자동으로 skip 된다.

## CAD 결과 시각화
- GUI: `pixi run freecad demo.FCStd`
- STL 변환:
  ```bash
  "$FREECAD_CMD" --console --cmd "
  import FreeCAD, ImportGui
  doc = FreeCAD.open('demo.FCStd')
  ImportGui.export(doc.Objects, 'demo.stl')
  FreeCAD.closeDocument(doc.Name)
  "
  ```
- OBJ 변환:
  ```bash
  python3 - <<'PY'
  import FreeCAD, Mesh, Part
  doc = FreeCAD.open('demo.FCStd')
  mesh = Mesh.Mesh()
  for obj in doc.Objects:
      if hasattr(obj, "Shape"):
          mesh.addFacet(Part.__toPython__(obj.Shape.tessellate(1.0)))
  mesh.export('demo.obj')
  FreeCAD.closeDocument(doc.Name)
  PY
  ```
- 생성된 STL/OBJ는 Meshlab, Blender, React Three Fiber 뷰어 등에서 확인한다.

## 문제 해결
- `freecad.status` 툴로 FreeCADCmd 경로 확인: `uv run python - <<'PY' ...` 형식으로 호출.
- 스타일 토큰 경고: FreeCAD GUI에서 `Edit ▸ Preferences ▸ General ▸ Style`을 기본 테마로 변경.
- 소프트웨어 렌더링 경고: `QT_OPENGL=desktop` 환경 변수 설정 후 재시작.
- 프록시 연결 문제: `docker compose ps`, `curl http://localhost:4000/v1/models`로 상태 확인.
