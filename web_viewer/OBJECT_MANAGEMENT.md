# 📦 객체 관리 기능

**날짜**: 2025-10-26  
**버전**: Web Viewer v1.2

---

## 🎉 새로운 기능

### 1️⃣ **새 문서 생성** 📄

현재 작업을 지우고 깨끗한 상태에서 새로 시작할 수 있습니다.

**위치**: 채팅 헤더 우측 상단  
**버튼**: 📄 새문서

**사용 방법**:
1. "📄 새문서" 버튼 클릭
2. 확인 대화상자에서 "확인" 클릭
3. 모든 객체가 삭제되고 새 세션 시작

**특징**:
- ✅ 모든 객체 삭제
- ✅ 3D 뷰어 초기화
- ✅ 새 세션 ID 생성
- ✅ 확인 대화상자로 실수 방지

---

### 2️⃣ **객체 목록 패널** 📦

현재 문서에 있는 모든 객체를 한눈에 볼 수 있습니다.

**위치**: 3D 뷰어 왼쪽 하단  
**패널**: 📦 객체 목록

**표시 정보**:
- 📝 객체 이름 (Box, Cylinder 등)
- 🔧 객체 타입 (box, cylinder, sphere 등)
- 🗑️ 삭제 버튼

**특징**:
- ✅ 실시간 업데이트
- ✅ 자동으로 표시
- ✅ 접기/펼치기 가능 (−/+ 버튼)
- ✅ 스크롤 가능 (많은 객체)

---

### 3️⃣ **개별 객체 삭제** 🗑️

원하는 객체만 선택해서 삭제할 수 있습니다.

**사용 방법**:
1. 객체 목록 패널에서 삭제할 객체 찾기
2. 해당 객체의 "🗑️" 버튼 클릭
3. 확인 대화상자에서 "확인" 클릭
4. 객체 삭제 후 3D 모델 자동 재생성

**특징**:
- ✅ 개별 객체만 삭제
- ✅ 나머지 객체는 그대로 유지
- ✅ 3D 모델 자동 업데이트
- ✅ 확인 대화상자로 실수 방지

---

## 🎨 UI 레이아웃

### 전체 화면
```
┌─────────────────────────────────────────────────────┐
│  3D 뷰어                    │  채팅 & 컨트롤         │
│                             │  📄 📁 🛑              │
│  ┌───────────────────┐      │                       │
│  │  🎨 Viewer Info   │      │  💬 메시지            │
│  └───────────────────┘      │                       │
│                             │                       │
│  ┌───────────────────┐      │  💬 메시지            │
│  │📦 객체 목록     − │      │                       │
│  ├───────────────────┤      │                       │
│  │ 📄 Box      🗑️   │      │  📝 입력창            │
│  │ 📄 Cylinder 🗑️   │      │                       │
│  └───────────────────┘      │                       │
└─────────────────────────────────────────────────────┘
```

### 객체 목록 패널 (상세)
```
┌───────────────────────────┐
│ 📦 객체 목록            − │  ← 클릭하면 접힘
├───────────────────────────┤
│ ┌───────────────────────┐ │
│ │ 📄 Box                │ │
│ │    box             🗑️ │ │  ← 삭제 버튼
│ └───────────────────────┘ │
│ ┌───────────────────────┐ │
│ │ 📄 Cylinder           │ │
│ │    cylinder        🗑️ │ │
│ └───────────────────────┘ │
│ ┌───────────────────────┐ │
│ │ 📄 Sphere             │ │
│ │    sphere          🗑️ │ │
│ └───────────────────────┘ │
└───────────────────────────┘
```

### 버튼 배치
```
┌─────────────────────────────────────┐
│ 💬 FreeCAD Agent                    │
│                 📄 새문서 📁 파일 🛑 종료│
│ 🟢 연결됨                            │
└─────────────────────────────────────┘
```

---

## 🔧 기술 구현

### 백엔드 API

#### 1. 새 문서 생성
```python
@app.route('/new_document', methods=['POST'])
def new_document():
    """새 문서 생성 (모든 객체 삭제)"""
    global current_session
    
    current_session = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "messages": [],
        "objects": [],
        "model_file": None
    }
    
    return jsonify({
        "success": True,
        "message": "새 문서가 생성되었습니다",
        "session_id": current_session['session_id']
    })
```

#### 2. 객체 목록 조회
```python
@app.route('/get_objects')
def get_objects():
    """현재 문서의 객체 목록"""
    return jsonify({
        "objects": current_session.get("objects", []),
        "count": len(current_session.get("objects", []))
    })
```

#### 3. 객체 삭제
```python
@app.route('/delete_object/<object_name>', methods=['POST'])
def delete_object(object_name):
    """특정 객체 삭제"""
    global current_session
    
    # 객체 목록에서 제거
    objects = current_session.get("objects", [])
    objects = [obj for obj in objects if obj.get("name") != object_name]
    current_session["objects"] = objects
    
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
        return jsonify({
            "success": True,
            "message": "모든 객체가 삭제되었습니다",
            "remaining": 0,
            "model_file": None
        })
```

### 프론트엔드 JavaScript

#### 1. 새 문서 생성
```javascript
async function newDocument() {
    if (!confirm('새 문서를 만들면 현재 작업이 모두 지워집니다. 계속하시겠습니까?')) {
        return;
    }
    
    const response = await fetch('/new_document', { method: 'POST' });
    const data = await response.json();
    
    if (data.success) {
        // 3D 뷰어 초기화
        if (currentModel) {
            scene.remove(currentModel);
            currentModel = null;
        }
        
        // 객체 목록 업데이트
        updateObjectsList();
    }
}
```

#### 2. 객체 목록 업데이트
```javascript
async function updateObjectsList() {
    const response = await fetch('/get_objects');
    const data = await response.json();
    const objectsList = document.getElementById('objects-list');
    
    if (data.count === 0) {
        objectsList.innerHTML = '<div class="no-objects">객체가 없습니다</div>';
        return;
    }
    
    objectsList.innerHTML = data.objects.map(obj => `
        <div class="object-item">
            <div class="object-info">
                <div class="object-name">${obj.name}</div>
                <div class="object-type">${obj.type}</div>
            </div>
            <button class="btn-delete" onclick="deleteObject('${obj.name}')">🗑️</button>
        </div>
    `).join('');
}
```

#### 3. 객체 삭제
```javascript
async function deleteObject(objectName) {
    if (!confirm(`'${objectName}' 객체를 삭제하시겠습니까?`)) {
        return;
    }
    
    const response = await fetch(`/delete_object/${objectName}`, { method: 'POST' });
    const data = await response.json();
    
    if (data.success) {
        // 3D 모델 업데이트
        if (data.model_file) {
            loadModel(`/models/${data.model_file}?t=${Date.now()}`);
        } else {
            // 모든 객체 삭제됨
            scene.remove(currentModel);
            currentModel = null;
        }
        
        // 객체 목록 업데이트
        updateObjectsList();
    }
}
```

---

## 📖 사용 시나리오

### 시나리오 1: 새로 시작하기
```
1. 이전 작업이 있는 상태
2. "📄 새문서" 버튼 클릭
3. "새 문서를 만들면..." → 확인
4. 3D 뷰어 깨끗하게 초기화
5. "박스 만들어줘" → 새 작업 시작
```

### 시나리오 2: 의자 만들기 (단계별 확인)
```
1. "박스 4개 만들어줘" (다리)
   → 객체 목록: Box, Box001, Box002, Box003

2. 객체 목록 확인
   → 4개 박스 모두 표시됨

3. "실린더 하나 더" (등받이)
   → 객체 목록: Box, Box001, Box002, Box003, Cylinder

4. 다리 하나가 잘못됨!
   → "Box003" 옆 🗑️ 버튼 클릭
   → 확인
   → Box003만 삭제, 나머지는 유지

5. "박스 하나 더 만들어줘" (다리 다시 생성)
   → 완성!
```

### 시나리오 3: 여러 디자인 작업
```
1. 첫 번째 디자인: 의자
   - "의자 만들어줘"
   - 완성 후 파일로 저장됨 (자동)

2. 새 디자인 시작
   - "📄 새문서" 클릭
   - 깨끗한 상태에서 시작

3. 두 번째 디자인: 테이블
   - "테이블 만들어줘"
   - 완성

4. 이전 디자인 보기
   - "📁 파일" 버튼
   - 첫 번째 의자 디자인 선택
   - 3D 뷰어에 로드
```

### 시나리오 4: 복잡한 모델 정리
```
1. "박스 10개 만들어줘"
   → 객체 목록: Box, Box001, ..., Box009

2. 객체 목록 확인
   → 스크롤하면서 모든 객체 확인

3. 필요없는 객체 삭제
   - Box002 🗑️
   - Box005 🗑️
   - Box007 🗑️
   
4. 객체 목록에서 삭제된 것 확인
   → 7개만 남음

5. 3D 뷰어에서도 확인
   → 삭제된 박스들이 사라짐
```

---

## 🎯 장점

### 작업 효율성
- ✅ **빠른 시작**: 새 문서로 즉시 새 작업 시작
- ✅ **정밀한 편집**: 개별 객체만 선택해서 삭제
- ✅ **실시간 확인**: 객체 목록으로 현재 상태 파악

### 사용자 경험
- ✅ **직관적**: 객체 목록이 눈에 보임
- ✅ **안전함**: 확인 대화상자로 실수 방지
- ✅ **자동 업데이트**: 모든 변경사항 즉시 반영

### 워크플로우
- ✅ **반복 작업**: 새 문서로 빠르게 시작
- ✅ **시행착오**: 잘못된 객체만 삭제하고 계속 진행
- ✅ **실험**: 여러 버전 쉽게 만들기

---

## 💡 팁

### 1. 객체 패널 접기/펼치기
```
- 화면이 복잡할 때: "−" 버튼 클릭 → 패널 접기
- 객체 확인할 때: "+" 버튼 클릭 → 패널 펼치기
```

### 2. 실수로 삭제한 경우
```
- 객체 삭제는 되돌릴 수 없음
- Agent에게 다시 요청: "박스 하나 더 만들어줘"
- 또는 "📁 파일"에서 이전 버전 불러오기
```

### 3. 여러 객체 삭제
```
한 번에 하나씩:
1. 첫 번째 객체 🗑️ → 확인
2. 두 번째 객체 🗑️ → 확인
3. ...

모두 삭제하려면:
- "📄 새문서" 버튼이 더 빠름
```

### 4. 객체 이름 확인
```
- 같은 타입은 자동으로 번호가 붙음
  Box, Box001, Box002, ...
  
- 헷갈리면 3D 뷰어에서 위치 확인
- 삭제 전 확인 대화상자에서 한 번 더 체크
```

---

## 🚀 테스트 방법

### 1. 서버 시작
```bash
cd /Users/shkim5/Documents/cadai
./start_server.sh
```

### 2. 브라우저 접속
```
http://localhost:5000
```

### 3. 새 문서 테스트
```
1. "박스 만들어줘"
2. 객체 목록 확인 → "Box" 표시됨
3. "📄 새문서" 클릭 → 확인
4. 객체 목록 확인 → "객체가 없습니다"
5. 3D 뷰어 → 빈 화면
```

### 4. 객체 삭제 테스트
```
1. "박스 3개 만들어줘"
2. 객체 목록 → Box, Box001, Box002
3. "Box001" 옆 🗑️ 클릭 → 확인
4. 객체 목록 → Box, Box002 (2개만 남음)
5. 3D 뷰어 → 박스 2개만 표시됨
```

### 5. 패널 토글 테스트
```
1. 객체 목록 패널 표시 중
2. "−" 버튼 클릭 → 패널 사라짐
3. "+" 버튼 클릭 → 패널 다시 나타남
```

---

## 📝 앞으로 추가할 기능 (향후)

### 객체 편집
- [ ] 객체 이름 변경
- [ ] 객체 색상 변경
- [ ] 객체 위치 조정 (UI에서)
- [ ] 객체 크기 조정 (UI에서)

### 선택 기능
- [ ] 3D 뷰어에서 클릭하여 선택
- [ ] 여러 객체 한 번에 선택
- [ ] 선택한 객체만 삭제
- [ ] 선택한 객체 그룹화

### 레이어/그룹
- [ ] 객체를 레이어로 구분
- [ ] 레이어별 표시/숨기기
- [ ] 그룹 만들기
- [ ] 그룹 통째로 삭제

---

## 🎉 결론

이제 FreeCAD Web Viewer는 단순한 뷰어가 아니라 **본격적인 편집 도구**입니다!

**핵심 기능**:
1. ✅ 📄 새 문서 생성
2. ✅ 📦 객체 목록 보기
3. ✅ 🗑️ 개별 객체 삭제

**사용해보세요!** 🚀

---

**문서 작성**: 2025-10-26  
**작성자**: FreeCAD Web Viewer Team  
**버전**: 1.2

