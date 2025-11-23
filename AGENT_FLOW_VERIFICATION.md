# AGENT_FLOW.md 검증 결과

> ⚠️ 이 문서는 이전 AGENT_FLOW.md 버전(직접 XML 생성 기반)에 대한 검증 기록입니다.  
>  새로운 Code-as-Intermediate 아키텍처로 문서가 갱신되었으므로, 최신 흐름에 맞춘 재검증이 필요합니다.

## ⚠️ 발견된 불일치 사항

### 1. **파일 형식 불일치** (중요)
**문서**: Line 30, 92-100
```
SaveFiles[파일 저장<br/>FCStd, STEP, PNG]
```
**실제 구현**: `backend/services/freecad_service.py`
```python
# 실제로는 STL 파일만 생성
stl_file = MODELS_DIR / f"{session_id}.stl"
model_url = f"/static/models/{session_id}.stl"
```

**권장 조치**: AGENT_FLOW.md를 업데이트하여 STL 파일 생성을 반영

---

### 2. **엔드포인트 경로 차이** (경미)
**문서**: Line 58
```
POST http://localhost:8000/api/chat
```
**실제 구현**: `backend/main.py` + `backend/api/chat.py`
```python
# main.py: app.include_router(chat.router, prefix="/api")
# chat.py: @router.post("")
# 결과 = POST /api (not /api/chat)
```

**실제**: `POST http://localhost:8000/api`

**권장 조치**: 문서 업데이트 또는 라우터에 `/chat` 추가

---

### 3. **Response 구조 차이** (경미)
**문서**: Line 34-35
```
Success Response: model_url, xml_url 반환
Error Response: debug_info 포함
```

**실제 구현**: `backend/api/chat.py`
```python
class ChatResponse(BaseModel):
    message: str                  # ← 문서에 누락
    model_url: Optional[str]
    xml_url: Optional[str]
    xml_content: Optional[str]    # ← 문서에 누락
    debug_info: Optional[dict]
```

**권장 조치**: 문서에 `message`와 `xml_content` 필드 추가

---

### 4. **OCX Importer 출력 파일** (중요)
**문서**: Line 97-100
```
생성 파일:
  - *.FCStd: FreeCAD 네이티브 파일
  - *.step: STEP CAD 표준 파일
  - *.png: 3D 렌더링 이미지
```

**실제 구현**: `src/freecad_tools/ocx_importer.py`
```python
def export_to_stl(doc, output_path):
    # STL 파일만 생성
    mesh.write(output_path)
```

**권장 조치**: 
- Option A: 문서를 STL로 수정
- Option B: 코드에 STEP/PNG 내보내기 추가

---

## ✅ 정확한 부분

1. **LiteLLM Fallback 로직** (Line 69-76): ✅ 정확
2. **Frontend 엔드포인트 호출** (Line 56-58): ✅ 로직 정확 (경로만 수정 필요)
3. **에러 처리 메커니즘** (Line 117-121): ✅ 정확
4. **환경 변수 설정** (Line 102-115): ✅ 정확

---

## 권장 수정 사항 우선순위

### High Priority
1. **Line 30, 92-100**: "STEP, PNG" → "STL"로 변경
2. **Line 58**: `/api/chat` → `/api`로 변경

### Medium Priority  
3. **Line 34-35**: Response 스키마에 `message`, `xml_content` 추가

### Low Priority (Optional)
4. 코드에 STEP/PNG export 기능 추가 (문서대로 구현)
