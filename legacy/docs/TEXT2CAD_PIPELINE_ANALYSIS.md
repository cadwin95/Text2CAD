# Text2CAD: JSON → Vector → Mesh 변환 파이프라인 분석

## 📋 개요

Text2CAD는 DeepCAD JSON 형식의 CAD 데이터를 다음 3단계로 변환합니다:

```
DeepCAD JSON → CAD Vector (Quantized) → 3D Mesh/STEP
```

## 🔄 전체 파이프라인 다이어그램

```
┌─────────────────┐
│  DeepCAD JSON   │  원본 CAD 데이터 (좌표, 곡선, 연산 등)
└────────┬────────┘
         │ 1. from_dict()
         ▼
┌─────────────────┐
│  CADSequence    │  Sketch + Extrude 시퀀스 객체
│  (Float 좌표)   │  - SketchSequence: 2D 프로필 (Line, Arc, Circle)
└────────┬────────┘  - ExtrudeSequence: 3D 돌출 연산
         │ 2. normalize()
         ▼
┌─────────────────┐
│  Normalized     │  [0, 1] 범위로 정규화
│  CADSequence    │  - Global: Bounding Box 기준
└────────┬────────┘  - Local: Sketch 크기 기준
         │ 3. numericalize()
         ▼
┌─────────────────┐
│  Quantized Vec  │  8-bit 정수 (0~255)
│  (Integer)      │  - cad_vec: (N, 2) 토큰 시퀀스
└────────┬────────┘  - flag_vec: 토큰 타입
         │           - index_vec: Sketch/Extrude 인덱스
         │ 
         │ 4a. Model → decode()
         ▼
┌─────────────────┐
│  Predicted Vec  │  모델이 생성한 벡터
└────────┬────────┘
         │ 4b. from_vec()
         ▼
┌─────────────────┐
│  CADSequence    │  Sketch + Extrude 재구성
│  (Integer)      │
└────────┬────────┘
         │ 5. denumericalize()
         ▼
┌─────────────────┐
│  CADSequence    │  실제 좌표로 복원
│  (Float)        │
└────────┬────────┘
         │ 6. create_mesh() / save_stp()
         ▼
┌─────────────────┐
│   3D Mesh/STEP  │  최종 3D 모델
└─────────────────┘
```

---

## 🎯 1단계: JSON → CADSequence (from_dict)

### 입력: DeepCAD JSON

```json
{
  "sequence": [
    {
      "type": "ExtrudeFeature",
      "entity": "extrude_uid_123",
      "profiles": [
        {"sketch": "sketch_uid_1", "profile": "profile_uid_1"}
      ],
      "extent_one": {"distance": {"value": 10.5}},
      "extent_two": {"distance": {"value": 0.0}},
      "operation": "NewBodyFeatureOperation"
    }
  ],
  "entities": {
    "sketch_uid_1": {
      "type": "Sketch",
      "profiles": [
        {
          "loops": [
            {
              "curves": [
                {
                  "type": "Line",
                  "start_point": {"x": 0, "y": 0},
                  "end_point": {"x": 10, "y": 0}
                },
                {
                  "type": "Arc",
                  "center": {"x": 10, "y": 5},
                  "radius": 5,
                  "start_angle": -90,
                  "end_angle": 90
                }
              ]
            }
          ]
        }
      ]
    }
  }
}
```

### 코드: `CADSequence.from_dict()`

```python
# CadSeqProc/cad_sequence.py:372
@staticmethod
def from_dict(all_stat):
    sketch_seq = []
    extrude_seq = []
    
    # JSON에서 ExtrudeFeature를 순회
    for item in all_stat["sequence"]:
        if item["type"] == "ExtrudeFeature":
            # 1. Extrude 정보 파싱
            extrude_ops = ExtrudeSequence.from_dict(all_stat, item["entity"])
            uid_pairs = extrude_ops.get_profile_uids()  # [(sketch_uid, profile_uid)]
            
            # 2. Sketch 정보 파싱
            sketch_ops = SketchSequence.from_dict(all_stat, uid_pairs)
            
            # 3. Coordinate System 연결
            extrude_ops.coordsystem = sketch_ops.coordsystem
            extrude_ops.add_info("sketch_size", sketch_ops.bbox_size)
            
            sketch_seq.append(sketch_ops)
            extrude_seq.append(extrude_ops)
    
    # 4. Bounding Box 정보
    bbox = extract_bbox(all_stat["properties"]["bounding_box"])
    
    return CADSequence(sketch_seq, extrude_seq, bbox)
```

### 출력: CADSequence 객체

```python
CADSequence:
  - SketchSequence:
      - CoordinateSystem: rotation=[1,0,0,0,1,0,0,0,1], translation=[0,0,0]
      - FaceSequence:
          - LoopSequence:
              - Line: start=[0.0, 0.0], end=[10.0, 0.0]
              - Arc: center=[10.0, 5.0], radius=5.0
  - ExtrudeSequence:
      extent_one=10.5, extent_two=0.0, boolean=0, sketch_size=10.0
```

---

## 🔢 2단계: 정규화 (normalize)

### 목적
- **Global Normalization**: 전체 모델을 [0, 0.75] 범위로 정규화 (Extrude 파라미터)
- **Local Normalization**: 각 Sketch를 [0, 2^8-1] 범위로 정규화 (Sketch 좌표)

### 코드: `CADSequence.normalize()`

```python
# CadSeqProc/cad_sequence.py:565
def normalize(self, size=1, bit=N_BIT):
    # 1. Global Scale 계산 (Bounding Box 기준)
    bbox_max, bbox_min = self.bbox[0], self.bbox[1]
    scale = size * NORM_FACTOR / np.max(np.abs(bbox_max - bbox_min))
    # NORM_FACTOR = 0.75
    
    # 2. 각 Sketch-Extrude 쌍 정규화
    for i, ext in enumerate(self.extrude_seq):
        # Sketch 시작점 계산
        translate = self.sketch_seq[i].start_point
        
        # Extrude 파라미터 정규화
        ext.transform(
            translate=ext.coordsystem.rotate_vec(translate) - bbox_min,
            scale=scale
        )
        
        # Sketch 프로필 정규화 (Local)
        self.sketch_seq[i].normalize(translate=None, bit=bit)
        self.sketch_seq[i].coordsystem = ext.coordsystem
    
    return self
```

### 정규화 효과

**Before:**
```python
Line: start=[0.0, 0.0], end=[100.0, 0.0]
ExtrudeSequence: extent_one=50.0, extent_two=0.0
```

**After:**
```python
Line: start=[0.0, 0.0], end=[0.75, 0.0]  # Global scale
ExtrudeSequence: extent_one=0.375, extent_two=0.0  # Global scale
```

---

## 🔢 3단계: 양자화 (numericalize)

### 목적
- Float 좌표를 8-bit Integer (0~255)로 변환
- 신경망 학습을 위한 discrete 토큰 생성

### 코드: `CADSequence.numericalize()`

```python
# CadSeqProc/cad_sequence.py:554
def numericalize(self, bit=N_BIT):
    size = 2**bit  # 256 (8-bit)
    
    for skt in self.sketch_seq:
        skt.numericalize(bit=bit)
    
    for ext in self.extrude_seq:
        ext.numericalize(bit=bit)
    
    return self

# Sketch 양자화
def numericalize(self, bit=N_BIT):
    for face in self.facedata:
        for loop in face.loopdata:
            for curve in loop.curvedata:
                # 좌표를 정수로 변환
                curve.start_point = int_round(curve.start_point * (2**bit - 1))
                curve.end_point = int_round(curve.end_point * (2**bit - 1))
                if curve.type == "Arc" or curve.type == "Circle":
                    curve.center = int_round(curve.center * (2**bit - 1))
                    curve.radius = int_round(curve.radius * (2**bit - 1))

# Extrude 양자화
def numericalize(self, bit=N_BIT):
    self.quantized_metadata = {}
    self.quantized_metadata['extent_one'] = int_round(
        self.metadata['extent_one'] * (2**bit - 1)
    )
    self.quantized_metadata['extent_two'] = int_round(
        self.metadata['extent_two'] * (2**bit - 1)
    )
    # boolean, sketch_size 등은 그대로 유지
```

### 양자화 효과

**Before (Float):**
```python
Line: start=[0.0, 0.0], end=[0.75, 0.0]
extent_one=0.375
```

**After (Integer):**
```python
Line: start=[0, 0], end=[191, 0]  # 0.75 * 255 = 191
extent_one=95  # 0.375 * 255 = 95
```

---

## 🎲 4단계: 벡터 변환 (to_vec)

### 목적
- CADSequence를 1D 토큰 시퀀스로 변환
- Transformer 입력 형식으로 변환

### 코드: `CADSequence.to_vec()`

```python
# CadSeqProc/cad_sequence.py:242
def to_vec(self, padding=False, max_cad_seq_len=MAX_CAD_SEQUENCE_LENGTH):
    self.cad_vec = [[END_TOKEN.index("START"), 0]]  # [1, 0]
    self.flag_vec = [0]  # 토큰 타입
    self.index_vec = [0]  # Sketch-Extrude 인덱스
    
    for i in range(len(self.sketch_seq)):
        # Sketch 벡터
        skt_vec = self.sketch_seq[i].to_vec()
        # Extrude 벡터
        ext_vec = self.extrude_seq[i].to_vec()
        
        # 연결
        self.cad_vec += skt_vec + ext_vec
        
        # Flag: 0=sketch, 1~10=extrude
        self.flag_vec += [0] * len(skt_vec)
        self.flag_vec += [1] + list(range(1, 11))
        
        # Index: 현재 Sketch-Extrude 쌍 인덱스
        self.index_vec += [i] * (len(skt_vec) + len(ext_vec))
    
    # END 토큰
    self.cad_vec.append([END_TOKEN.index("START"), 0])
    self.flag_vec.append(0)
    self.index_vec.append(self.index_vec[-1])
    
    # Padding (모델 학습용)
    if padding:
        num_pad = max_cad_seq_len - len(self.cad_vec)
        self.cad_vec = add_padding(self.cad_vec, num_pad)
        self.flag_vec += [11] * num_pad
        self.index_vec += [max(self.index_vec) + 1] * num_pad
    
    return self
```

### 토큰 구조

#### END_TOKEN (Special Tokens)
```python
END_TOKEN = [
    "PADDING",       # 0
    "START",         # 1
    "END_SKETCH",    # 2
    "END_FACE",      # 3
    "END_LOOP",      # 4
    "END_CURVE",     # 5
    "END_EXTRUSION"  # 6
]
```

#### CAD_VEC 형식: (N, 2)
```python
[
    [1, 0],              # START
    # Sketch tokens
    [195, 128],          # Line start_x, start_y
    [191, 0],            # Line end_x, end_y
    [5, 0],              # END_CURVE
    [4, 0],              # END_LOOP
    [3, 0],              # END_FACE
    [2, 0],              # END_SKETCH
    # Extrude tokens
    [95, 0],             # extent_one
    [0, 0],              # extent_two
    [0, 0, 0],           # euler angles (ox, oy, oz)
    [0],                 # boolean operation
    [128],               # sketch_size
    [6, 0],              # END_EXTRUSION
    [1, 0],              # START (END)
    [0, 0], [0, 0], ...  # PADDING
]
```

#### FLAG_VEC
```python
[0, 0, 0, 0, 0, 0, 0,  # Sketch tokens
 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,  # Extrude tokens (10개)
 0,  # END token
 11, 11, 11, ...]  # Padding
```

#### INDEX_VEC
```python
[0, 0, 0, 0, 0, 0, 0,  # Sketch 0
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Extrude 0
 0,  # END token
 1, 1, 1, ...]  # Padding (다음 인덱스)
```

---

## 🧠 5단계: 모델 추론 및 역변환

### A. 모델 추론 (Text → Vector)

```python
# Cad_VLM/models/text2cad.py:35
def test_decode(self, texts: list[str], maxlen: int, 
                nucleus_prob, topk_index, device='cuda'):
    # 1. 텍스트 임베딩
    ZE, key_padding_mask = self.base_text_embedder.get_embedding(texts)
    
    # 2. Adaptive Layer
    ZE, _ = self.adaptive_layer(ZE, mask, False)
    
    # 3. Autoregressive Decoding
    S_output = self.cad_decoder.decode(
        ZE=ZE,                    # 텍스트 컨텍스트
        cross_attn_mask_dict=ca_mask,
        maxlen=maxlen,            # 272
        nucleus_prob=nucleus_prob, # Top-p sampling
        topk_index=topk_index,    # Top-k sampling
        device=device
    )
    
    return S_output  # {"cad_vec": tensor (B, 272, 2)}
```

### B. 벡터 → CADSequence (from_vec)

```python
# CadSeqProc/cad_sequence.py:167
@staticmethod
def from_vec(cad_vec, bit=N_BIT, post_processing=False, 
             denumericalize=True):
    # 1. Padding 제거
    cad_vec = cad_vec[np.where(cad_vec[:, 0] != END_TOKEN.index("PADDING"))[0]]
    
    # 2. START/END 토큰 처리
    if post_processing:
        if cad_vec[-1, 0] != END_TOKEN.index("START"):
            cad_vec = np.concatenate([cad_vec, [[1, 0]]])
        if len(np.where(cad_vec[1:, 0] == END_TOKEN.index("START"))[0]) == 0:
            cad_vec = np.concatenate([[[1, 0]], cad_vec])
    
    # 3. START 토큰으로 분할
    cad_vec = split_array(cad_vec, END_TOKEN.index("START"))[1]
    
    # 4. END_EXTRUSION으로 분할 (Sketch-Extrude 쌍)
    skt_ext_seq = split_array(cad_vec, END_TOKEN.index("END_EXTRUSION"), False, False)
    
    sketch_seq = []
    extrude_seq = []
    
    for i, skt_ext in enumerate(skt_ext_seq):
        # Sketch 부분 (END_SKETCH 전까지)
        sketch = split_array(skt_ext, END_TOKEN.index("END_SKETCH"), False, False)[0]
        # Extrude 부분 (마지막 10 토큰)
        extrude = skt_ext[-10:]
        
        # 재구성
        sketch_seq.append(SketchSequence.from_vec(sketch, bit, post_processing))
        extrude_seq.append(ExtrudeSequence.from_vec(extrude, bit, post_processing))
    
    # 5. 역양자화 (Integer → Float)
    if denumericalize:
        return CADSequence(sketch_seq, extrude_seq).denumericalize(bit=bit)
    else:
        return CADSequence(sketch_seq, extrude_seq)
```

### C. 역양자화 (denumericalize)

```python
# CadSeqProc/cad_sequence.py:597
def denumericalize(self, bit=N_BIT):
    size = 2**bit  # 256
    
    # 1. Extrude 역양자화
    for ext in self.extrude_seq:
        ext.denumericalize(bit=bit)
    
    # 2. Sketch 역정규화 (Local)
    for i, skt in enumerate(self.sketch_seq):
        skt.coordsystem = self.extrude_seq[i].coordsystem
        skt.denormalize(
            bbox_size=self.extrude_seq[i].metadata["sketch_size"],
            translate=0,
            bit=bit
        )
    
    return self

# Extrude 역양자화
def denumericalize(self, bit=N_BIT):
    self.metadata['extent_one'] = dequantize_verts(
        self.quantized_metadata['extent_one'], 
        n_bits=bit
    )
    # 191 / 255 = 0.749 ≈ 0.75

# Sketch 역정규화
def denormalize(self, bbox_size, translate, bit):
    for face in self.facedata:
        for loop in face.loopdata:
            for curve in loop.curvedata:
                # 1. 역양자화: Integer → [0, 1]
                curve.start_point = dequantize_verts(curve.start_point, bit)
                # 2. 역정규화: [0, 1] → 실제 크기
                curve.start_point = curve.start_point * bbox_size
```

---

## 🎨 6단계: 3D Mesh/STEP 생성

### A. Mesh 생성 (create_mesh)

```python
# CadSeqProc/cad_sequence.py:800+
def create_mesh(self):
    # 1. CAD 솔리드 생성
    brep = self.create_solid()
    
    # 2. Brep → Mesh 변환
    self.mesh = brep2mesh(brep)
    
    return self

def create_solid(self):
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
    
    all_solids = []
    
    for i, skt in enumerate(self.sketch_seq):
        # 1. Sketch → 2D Face
        face = skt.create_skt_face()
        
        # 2. Extrude → 3D Solid
        ext = self.extrude_seq[i]
        direction = ext.coordsystem.normal
        distance = ext.metadata['extent_one'] + ext.metadata['extent_two']
        
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
        prism = BRepPrimAPI_MakePrism(face, direction * distance)
        solid = prism.Shape()
        
        # 3. Boolean 연산
        if i == 0:
            result = solid
        else:
            boolean_op = ext.metadata['boolean']
            if boolean_op == 0:  # NewBody
                result = solid
            elif boolean_op == 1:  # Join (Union)
                result = BRepAlgoAPI_Fuse(result, solid).Shape()
            elif boolean_op == 2:  # Cut (Subtract)
                result = BRepAlgoAPI_Cut(result, solid).Shape()
            # ... IntersectFeatureOperation
        
        all_solids.append(result)
    
    return result

def brep2mesh(brep):
    """OpenCASCADE Brep → Trimesh"""
    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    
    # Mesh 생성
    mesh = BRepMesh_IncrementalMesh(brep, 0.01)
    mesh.Perform()
    
    # Vertices와 Faces 추출
    vertices = []
    faces = []
    # ... OpenCASCADE API로 추출
    
    import trimesh
    return trimesh.Trimesh(vertices=vertices, faces=faces)
```

### B. STEP 파일 저장

```python
# CadSeqProc/cad_sequence.py
def save_stp(self, filename, output_dir, type="step"):
    # 1. Brep 생성
    brep = self.create_solid()
    
    # 2. STEP 파일로 저장
    if type == "step":
        from OCC.Extend.DataExchange import write_step_file
        filepath = os.path.join(output_dir, filename + ".step")
        write_step_file(brep, filepath)
    
    # 3. STL 파일로 저장
    elif type == "stl":
        mesh = brep2mesh(brep)
        filepath = os.path.join(output_dir, filename + ".stl")
        mesh.export(filepath)
    
    return brep
```

---

## 💻 전체 파이프라인 실행 예제

### 예제 1: JSON → Vector (학습 데이터 준비)

```bash
# DeepCAD JSON → CAD Vector
cd CadSeqProc
python json2vec.py \
    --input_dir ./deepcad_json \
    --split_json ./train_test_val.json \
    --output_dir ./cad_vec \
    --bit 8 \
    --padding \
    --max_workers 32
```

```python
# 내부 실행 흐름
def process_json(json_path, args):
    # 1. JSON 읽기
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # 2. JSON → CADSequence → Vector
    cad_obj, cad_vec, flag_vec, index_vec = CADSequence.json_to_vec(
        data=data,
        bit=args.bit,              # 8
        padding=args.padding,      # True
        max_cad_seq_len=272
    )
    
    # 3. Attention Mask 생성
    cad_seq_dict = {
        "vec": {
            "cad_vec": cad_vec,       # (272, 2) torch.int32
            "flag_vec": flag_vec,     # (272,) torch.int32
            "index_vec": index_vec,   # (272,) torch.int32
        },
        "mask_cad_dict": {
            "attn_mask": generate_attention_mask(271),  # Causal mask
            "key_padding_mask": cad_vec == 0,  # Padding mask
        }
    }
    
    # 4. 저장
    torch.save(cad_seq_dict, output_path)
```

### 예제 2: Text → Mesh (추론)

```python
# App/app.py
from Cad_VLM.models.text2cad import Text2CAD
from CadSeqProc.cad_sequence import CADSequence

# 1. 모델 로드
model = Text2CAD(text_config, cad_config).eval()
model.load_state_dict(checkpoint)

# 2. 텍스트 → Vector
text = "A rectangular prism with a circular hole in the center."
pred_cad_seq_dict = model.test_decode(
    texts=[text],
    maxlen=272,
    nucleus_prob=0,    # Greedy decoding
    topk_index=1,
    device="cuda"
)

# 3. Vector → CADSequence
pred_cad = CADSequence.from_vec(
    pred_cad_seq_dict["cad_vec"][0].cpu().numpy(),
    bit=8,
    post_processing=True
)

# 4. CADSequence → Mesh
pred_cad.create_mesh()
mesh = pred_cad.mesh

# 5. 저장
mesh.export("output.stl")
```

### 예제 3: JSON → STEP (검증)

```bash
# DeepCAD JSON → STEP 파일
cd CadSeqProc
python json2step.py \
    --input_dir ./deepcad_json \
    --output_dir ./step_files \
    --save_type step \
    --max_workers 8
```

```python
# 내부 실행 흐름
def process_json(json_path, args):
    # 1. JSON 읽기
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # 2. JSON → Normalized CAD (역정규화 불가능한 형태)
    cad_seq = CADSequence.json_to_NormalizedCAD(data=data, bit=args.bit)
    
    # 3. CADSequence → STEP
    cad_seq.save_stp(
        filename=uid,
        output_dir=args.output_dir,
        type=args.save_type  # "step" or "stl"
    )
```

---

## 🔍 핵심 데이터 구조

### 1. CADSequence
```python
class CADSequence:
    sketch_seq: List[SketchSequence]     # 2D 프로필들
    extrude_seq: List[ExtrudeSequence]   # 3D 돌출 연산들
    bbox: np.ndarray                     # Bounding box (2, 3)
    cad_vec: torch.Tensor                # (N, 2) 토큰 시퀀스
    flag_vec: torch.Tensor               # (N,) 토큰 타입
    index_vec: torch.Tensor              # (N,) Sketch-Extrude 인덱스
```

### 2. SketchSequence
```python
class SketchSequence:
    facedata: List[FaceSequence]         # 2D Face들
    coordsystem: CoordinateSystem        # 좌표계 (회전, 이동)
    
class FaceSequence:
    loopdata: List[LoopSequence]         # 2D Loop들
    
class LoopSequence:
    curvedata: List[Curve]               # Line, Arc, Circle
    
class Line:
    start_point: np.ndarray (2,)
    end_point: np.ndarray (2,)
    
class Arc:
    center: np.ndarray (2,)
    radius: float
    start_angle: float
    end_angle: float
    
class Circle:
    center: np.ndarray (2,)
    radius: float
```

### 3. ExtrudeSequence
```python
class ExtrudeSequence:
    metadata: dict
        - extent_one: float              # 정방향 돌출 거리
        - extent_two: float              # 역방향 돌출 거리
        - boolean: int                   # 0=New, 1=Join, 2=Cut, 3=Intersect
        - sketch_size: float             # Sketch 크기 (역정규화용)
        - profile_uids: List[List[str]]  # [(sketch_uid, profile_uid)]
    coordsystem: CoordinateSystem        # 좌표계
```

---

## 📊 토큰 통계

### 토큰 길이 분포
```
MAX_CAD_SEQUENCE_LENGTH = 272

특수 토큰: 7개 (PADDING, START, END_SKETCH, ...)
Sketch 토큰: 0 ~ 150개 (가변)
Extrude 토큰: 10개 (고정)
```

### 토큰 어휘 크기
```python
vocab_size = 7 (special) + 4 (boolean) + 256 (8-bit) = 267

END_TOKEN (7) + BOOLEAN_PAD (4) + 2^N_BIT (256) = 267
```

---

## 🚀 성능 최적화

### 1. 병렬 처리
```python
# ProcessPoolExecutor로 JSON 처리
executor = ProcessPoolExecutor(max_workers=32)
futures = [executor.submit(process_json, json_path) for json_path in all_files]
```

### 2. 중복 제거
```python
# Hash 기반 중복 모델 제거
param = cad_vec[torch.where(cad_vec >= len(END_TOKEN))[0]].tolist()
hash_vec = hash_map(param)
if hash_vec in unique_model_hash:
    skip_this_model()
```

### 3. Curriculum Learning
```python
# 복잡도 기준으로 정렬
complexity = len(cad_obj.all_curves)  # 곡선 개수
sorted_uid = sorted(unique_uid.keys(), key=lambda k: unique_uid[k])
```

---

## 🎯 주요 차이점: Text2CAD vs FreeCAD

| 항목 | Text2CAD | FreeCAD (우리 프로젝트) |
|------|----------|------------------------|
| **CAD 표현** | Sketch + Extrude 시퀀스 | Python API 명령 |
| **데이터 형식** | Vector (Quantized) | Document 객체 |
| **추론 방식** | Autoregressive Decoding | LLM Tool Calling |
| **정밀도** | 8-bit (0~255) | Float (무제한) |
| **Boolean 연산** | 4종류 (New/Join/Cut/Intersect) | FreeCAD API (모든 연산) |
| **곡선 타입** | Line, Arc, Circle | 모든 FreeCAD 도형 |
| **3D 엔진** | PythonOCC (OpenCASCADE) | FreeCAD |
| **출력 형식** | STL, STEP | FCStd, STL, STEP, ... |

---

## 💡 통합 아이디어

### 1. Text2CAD 모델을 FreeCAD로 변환
```python
def text2cad_to_freecad(pred_cad: CADSequence):
    """Text2CAD 예측 → FreeCAD 객체"""
    import FreeCAD
    import Part
    
    doc = FreeCAD.newDocument()
    
    for i, skt in enumerate(pred_cad.sketch_seq):
        # 1. Sketch → FreeCAD Wire
        edges = []
        for curve in skt.all_curves:
            if curve.type == "Line":
                edge = Part.makeLine(
                    FreeCAD.Vector(*curve.start_point, 0),
                    FreeCAD.Vector(*curve.end_point, 0)
                )
            elif curve.type == "Arc":
                edge = Part.makeCircle(
                    curve.radius,
                    FreeCAD.Vector(*curve.center, 0),
                    FreeCAD.Vector(0, 0, 1),
                    curve.start_angle,
                    curve.end_angle
                )
            edges.append(edge)
        
        wire = Part.Wire(edges)
        face = Part.Face(wire)
        
        # 2. Extrude → FreeCAD Solid
        ext = pred_cad.extrude_seq[i]
        direction = FreeCAD.Vector(0, 0, ext.metadata['extent_one'])
        solid = face.extrude(direction)
        
        # 3. Boolean 연산
        boolean_op = ext.metadata['boolean']
        if boolean_op == 1:  # Join
            obj1.Shape = obj1.Shape.fuse(solid)
        elif boolean_op == 2:  # Cut
            obj1.Shape = obj1.Shape.cut(solid)
        
        doc.addObject("Part::Feature", f"Shape{i}").Shape = solid
    
    return doc
```

### 2. FreeCAD → Text2CAD 학습 데이터 생성
```python
def freecad_to_text2cad_vec(doc):
    """FreeCAD 문서 → Text2CAD Vector"""
    # 1. FreeCAD → DeepCAD JSON 형식 변환
    json_data = export_freecad_to_deepcad_json(doc)
    
    # 2. JSON → Vector
    cad_obj, cad_vec, flag_vec, index_vec = CADSequence.json_to_vec(
        data=json_data,
        bit=8,
        padding=True
    )
    
    return cad_vec, flag_vec, index_vec
```

### 3. 하이브리드 시스템
```python
def hybrid_cad_generation(text: str):
    """LLM + Text2CAD 하이브리드"""
    # 1. LLM으로 복잡도 판단
    complexity = llm.analyze_complexity(text)
    
    if complexity == "simple":
        # 간단한 형상: FreeCAD Tool Calling
        result = tool_calling_agent.run(text)
    else:
        # 복잡한 형상: Text2CAD 모델
        pred_vec = text2cad_model.decode(text)
        pred_cad = CADSequence.from_vec(pred_vec)
        result = text2cad_to_freecad(pred_cad)
    
    return result
```

---

## 📚 참고 문서

- **Text2CAD 논문**: [NeurIPS 2024](https://arxiv.org/abs/2409.17106)
- **DeepCAD**: [GitHub](https://github.com/ChrisWu1997/DeepCAD)
- **OpenCASCADE**: [PythonOCC](https://github.com/tpaviot/pythonocc-core)
- **FreeCAD API**: [Documentation](https://wiki.freecad.org/Python_scripting_tutorial)

---

## 🔧 디버깅 팁

### 1. Vector 시각화
```python
# CAD Vector 출력
print(f"cad_vec shape: {cad_vec.shape}")
print(f"Sketch tokens: {torch.where(flag_vec == 0)[0].shape[0]}")
print(f"Extrude tokens: {torch.where(flag_vec != 0)[0].shape[0]}")
print(f"Number of Sketch-Extrude pairs: {len(sketch_seq)}")
```

### 2. 역변환 검증
```python
# JSON → Vec → CADSequence → Vec 일치성 검증
original_vec = CADSequence.json_to_vec(json_data)[1]
reconstructed_cad = CADSequence.from_vec(original_vec)
reconstructed_vec = reconstructed_cad.to_vec().cad_vec

assert torch.allclose(original_vec, reconstructed_vec)
```

### 3. Mesh 생성 실패 디버깅
```python
try:
    cad_seq.create_mesh()
except Exception as e:
    print(f"Mesh generation failed: {e}")
    # 개별 Sketch-Extrude 검증
    for i, skt in enumerate(cad_seq.sketch_seq):
        try:
            face = skt.create_skt_face()
            print(f"Sketch {i}: OK")
        except Exception as e:
            print(f"Sketch {i}: FAILED - {e}")
```

---

## ✅ 체크리스트

파이프라인 작동 확인:
- [ ] JSON 파일 로드 성공
- [ ] CADSequence 객체 생성 성공
- [ ] normalize() 실행 후 좌표 범위 [0, 0.75] 확인
- [ ] numericalize() 실행 후 모든 값 0~255 범위 확인
- [ ] to_vec() 실행 후 cad_vec shape = (272, 2) 확인
- [ ] from_vec() 실행 후 CADSequence 재구성 성공
- [ ] denumericalize() 실행 후 Float 좌표 복원 확인
- [ ] create_mesh() 실행 후 Mesh 생성 성공
- [ ] STL/STEP 파일 저장 및 뷰어에서 확인

---

이 파이프라인을 이해하면 Text2CAD 모델을 FreeCAD 프로젝트와 통합하거나, 새로운 CAD 생성 모델을 개발할 수 있습니다! 🚀

