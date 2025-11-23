# FreeCAD vs Text2CAD: 어떤 것을 사용해야 할까?

## 🎯 TL;DR (결론부터)

### ✅ **사전 학습 모델 사용 가능!**
Text2CAD는 **사전 학습된 모델**을 제공합니다:
- 📦 **모델 체크포인트**: [HuggingFace에서 다운로드](https://huggingface.co/datasets/SadilKhan/Text2CAD/blob/main/text2cad_v1.0/Text2CAD_1.0.pth)
- 🎨 **Gradio 데모 앱**: 바로 실행 가능
- 📊 **학습 데이터**: DeepCAD 50,000+ 모델로 학습됨

### 🤔 **FreeCAD vs Text2CAD 선택 기준**

| 상황 | 추천 | 이유 |
|------|------|------|
| **빠른 프로토타입** | Text2CAD ⭐ | 사전 학습 모델 바로 사용 |
| **정밀한 제어** | FreeCAD 🔧 | 파라미터 세밀 조정 |
| **복잡한 형상** | Text2CAD ⭐ | End-to-end 학습 |
| **실시간 생성** | Text2CAD ⭐ | 추론 속도 빠름 |
| **다양한 CAD 기능** | FreeCAD 🔧 | 모든 FreeCAD 기능 사용 |
| **커스텀 도형** | FreeCAD 🔧 | Python API 유연성 |
| **학습 데이터 있음** | Text2CAD ⭐ | Fine-tuning 가능 |
| **학습 데이터 없음** | FreeCAD 🔧 | LLM으로 충분 |

---

## 📊 상세 비교

### 1. 접근 방식

#### FreeCAD (Tool Calling)
```python
# LLM이 도구를 호출
tools = [
    "freecad_create_box",
    "freecad_create_cylinder",
    "freecad_boolean_cut"
]

# 단계적 실행
llm → "박스 생성하고 구멍 뚫기"
  ↓
1. create_box(length=10, width=10, height=10)
2. create_cylinder(radius=2, height=15)
3. boolean_cut(box, cylinder)
```

**장점:**
- ✅ 명령어가 명확하고 해석 가능
- ✅ 실패 시 디버깅 쉬움
- ✅ FreeCAD의 모든 기능 사용 가능
- ✅ 학습 데이터 불필요
- ✅ 파라미터 정밀 제어

**단점:**
- ❌ 복잡한 형상은 여러 단계 필요
- ❌ LLM의 tool calling 품질에 의존
- ❌ 형상 생성 품질이 LLM 성능에 좌우됨

#### Text2CAD (End-to-End)
```python
# 텍스트 → 3D 모델 직접 생성
text = "A rectangular prism with a circular hole in the center."
  ↓
model.decode(text)
  ↓
CAD Vector [START, 195, 128, ..., END]
  ↓
3D Mesh (STL/STEP)
```

**장점:**
- ✅ **한 번에 전체 형상 생성**
- ✅ 복잡한 형상도 단일 추론
- ✅ 학습 데이터로 품질 향상
- ✅ **빠른 추론 속도** (~1초)
- ✅ 일관성 있는 출력

**단점:**
- ❌ **제한된 표현력** (Sketch + Extrude만)
- ❌ 학습 데이터에 없는 형상은 실패
- ❌ Fine-tuning 필요 (맞춤형 형상)
- ❌ 디버깅 어려움 (블랙박스)
- ❌ 8-bit 양자화로 정밀도 제한

---

## 🚀 Text2CAD 사전 학습 모델 사용하기

### 1. 환경 설정

```bash
# Conda 환경 생성
cd Text2CAD
conda env create --file environment.yml
conda activate text2cad

# 의존성 확인
python -c "import torch; print(torch.__version__)"
python -c "from OCC.Core import BRep; print('PythonOCC OK')"
```

### 2. 사전 학습 모델 다운로드

```bash
# HuggingFace에서 다운로드
mkdir -p checkpoints
cd checkpoints

# Option 1: wget
wget https://huggingface.co/datasets/SadilKhan/Text2CAD/resolve/main/text2cad_v1.0/Text2CAD_1.0.pth

# Option 2: huggingface-cli
pip install huggingface-hub
huggingface-cli download SadilKhan/Text2CAD text2cad_v1.0/Text2CAD_1.0.pth --local-dir ./
```

### 3. Config 파일 수정

```yaml
# Cad_VLM/config/inference_user_input.yaml
text_encoder:
  text_embedder:
    model_name: "bert_large_uncased"
    max_seq_len: 512
    cache_dir: "/path/to/huggingface/cache"  # ← 수정

  adaptive_layer:
    in_dim: 1024
    out_dim: 1024
    num_heads: 8
    dropout: 0.1

cad_decoder:
  tdim: 1024
  cdim: 256
  num_layers: 8
  num_heads: 8
  dropout: 0.1
  ca_level_start: 2

test:
  batch_size: 1
  log_dir: "./outputs"  # ← 수정
  checkpoint_path: "./checkpoints/Text2CAD_1.0.pth"  # ← 수정
  nucleus_prob: 0
  sampling_type: "max"

debug: False
```

### 4. 단일 프롬프트로 테스트

```bash
cd Text2CAD/Cad_VLM

# 간단한 형상
python test_user_input.py \
    --config_path config/inference_user_input.yaml \
    --prompt "A simple ring."

# 복잡한 형상
python test_user_input.py \
    --config_path config/inference_user_input.yaml \
    --prompt "The CAD model features a rectangular metal plate with four holes along its length."
```

### 5. Gradio 데모 실행

```bash
cd Text2CAD/App
python app.py

# 브라우저에서 http://localhost:7860 접속
```

### 6. Python 스크립트로 사용

```python
import torch
import yaml
from Cad_VLM.models.text2cad import Text2CAD
from CadSeqProc.cad_sequence import CADSequence
from CadSeqProc.utility.macro import MAX_CAD_SEQUENCE_LENGTH, N_BIT

# 1. Config 로드
with open("Cad_VLM/config/inference_user_input.yaml", "r") as f:
    config = yaml.safe_load(f)

# 2. 모델 로드
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

cad_config = config["cad_decoder"]
cad_config["cad_seq_len"] = MAX_CAD_SEQUENCE_LENGTH

model = Text2CAD(
    text_config=config["text_encoder"],
    cad_config=cad_config
).to(device)

# 3. 체크포인트 로드
checkpoint = torch.load(
    config["test"]["checkpoint_path"],
    map_location=device
)

# 모듈 프리픽스 제거
pretrained_dict = {}
for key, value in checkpoint["model_state_dict"].items():
    if key.startswith("module."):
        pretrained_dict[key[7:]] = value
    else:
        pretrained_dict[key] = value

model.load_state_dict(pretrained_dict, strict=False)
model.eval()

# 4. 추론
text_prompt = "A cylindrical object with a hole through the center."

with torch.no_grad():
    pred_cad_seq_dict = model.test_decode(
        texts=[text_prompt],
        maxlen=MAX_CAD_SEQUENCE_LENGTH,
        nucleus_prob=0,    # Greedy decoding
        topk_index=1,
        device=device
    )

# 5. Vector → CADSequence
pred_cad = CADSequence.from_vec(
    pred_cad_seq_dict["cad_vec"][0].cpu().numpy(),
    bit=N_BIT,
    post_processing=True
)

# 6. Mesh 생성 및 저장
try:
    pred_cad.create_mesh()
    pred_cad.mesh.export("output.stl")
    print("✅ STL 파일 생성 성공: output.stl")
except Exception as e:
    print(f"❌ Mesh 생성 실패: {e}")
    # STEP 파일로 시도
    try:
        pred_cad.save_stp("output", "./", type="step")
        print("✅ STEP 파일 생성 성공: output.step")
    except Exception as e2:
        print(f"❌ STEP 파일도 실패: {e2}")
```

---

## 📈 성능 비교

### 추론 속도

| 방법 | 단일 모델 생성 시간 | 배치 처리 |
|------|-------------------|----------|
| **Text2CAD** | ~1초 | ✅ 가능 (GPU) |
| **FreeCAD Tool Calling** | ~5-10초 | ❌ 순차 처리 |

### 품질 비교

#### Text2CAD가 잘하는 것:
- ✅ **회전 대칭 형상** (Ring, Cylinder, Gear)
- ✅ **돌출 기반 형상** (Prism, Block with holes)
- ✅ **단순 Boolean 연산** (Join, Cut)
- ✅ **일관성 있는 출력** (같은 프롬프트 → 같은 결과)

#### FreeCAD Tool Calling이 잘하는 것:
- ✅ **복잡한 형상** (Loft, Sweep, Pattern)
- ✅ **파라메트릭 모델** (치수 변경)
- ✅ **정밀한 제약조건** (Tangent, Parallel)
- ✅ **어셈블리** (여러 부품 조립)

### 메모리 사용량

| 방법 | GPU 메모리 | CPU 메모리 |
|------|-----------|-----------|
| **Text2CAD** | ~4GB (BERT + Decoder) | ~2GB |
| **FreeCAD** | ~0GB (LLM API 사용 시) | ~500MB |

---

## 🎨 실제 사용 예제

### 예제 1: Text2CAD로 빠른 프로토타입

```python
# 시나리오: 100개의 다양한 링 형상 생성

texts = [
    "A simple ring.",
    "A ring with hexagonal outer shape.",
    "A ring with rectangular cross-section.",
    # ... 97개 더
]

# Text2CAD: 배치 처리로 ~100초
for i in range(0, len(texts), 8):  # Batch size 8
    batch = texts[i:i+8]
    results = model.test_decode(batch, ...)
    # 8개를 ~8초에 처리

# FreeCAD Tool Calling: ~500-1000초
for text in texts:
    result = agent.run(text)  # 각각 5-10초
```

### 예제 2: FreeCAD로 정밀한 모델

```python
# 시나리오: 기어 설계 (정밀한 치형 필요)

prompt = """
Create a spur gear with:
- Module: 2mm
- Number of teeth: 20
- Pressure angle: 20°
- Face width: 10mm
- Bore diameter: 8mm
"""

# Text2CAD: 학습 데이터에 없으면 실패 가능
# → 대략적인 기어 형상만 생성

# FreeCAD Tool Calling: 정밀한 기어 생성
# → LLM이 involute_gear 도구 호출
# → 정확한 파라미터로 기어 생성
```

---

## 🔄 하이브리드 접근법 (추천!)

두 가지를 결합하면 최고의 결과를 얻을 수 있습니다:

```python
class HybridCADGenerator:
    def __init__(self):
        self.text2cad_model = load_text2cad_model()
        self.freecad_agent = ToolCallingAgent()
    
    def generate(self, prompt: str):
        # 1. 복잡도 분석
        complexity = self.analyze_complexity(prompt)
        
        # 2. 형상 타입 분류
        shape_type = self.classify_shape(prompt)
        
        # 3. 적절한 방법 선택
        if complexity == "simple" and shape_type in ["ring", "cylinder", "prism"]:
            # Text2CAD 사용 (빠름)
            print("Using Text2CAD for fast generation...")
            result = self.text2cad_model.decode(prompt)
            return self.vec_to_freecad(result)
        
        elif complexity == "moderate":
            # Text2CAD로 초안 생성 → FreeCAD로 정제
            print("Using hybrid approach...")
            draft = self.text2cad_model.decode(prompt)
            refined = self.freecad_agent.refine(draft, prompt)
            return refined
        
        else:
            # FreeCAD Tool Calling (정밀함)
            print("Using FreeCAD for precise generation...")
            return self.freecad_agent.run(prompt)
    
    def analyze_complexity(self, prompt: str) -> str:
        # LLM으로 복잡도 판단
        keywords = ["gear", "thread", "loft", "sweep", "pattern"]
        if any(k in prompt.lower() for k in keywords):
            return "complex"
        elif len(prompt.split()) > 20:
            return "moderate"
        else:
            return "simple"
    
    def classify_shape(self, prompt: str) -> str:
        # LLM으로 형상 분류
        shape_keywords = {
            "ring": ["ring", "circular", "hollow cylinder"],
            "cylinder": ["cylinder", "tube", "pipe"],
            "prism": ["rectangular", "box", "block", "prism"],
        }
        # ... 분류 로직
        return "unknown"
    
    def vec_to_freecad(self, cad_vec):
        # Text2CAD 결과를 FreeCAD로 변환
        cad_seq = CADSequence.from_vec(cad_vec)
        return convert_to_freecad_document(cad_seq)
```

### 사용 예제

```python
generator = HybridCADGenerator()

# Case 1: 간단한 형상 → Text2CAD
result1 = generator.generate("A simple ring.")
# → Text2CAD 사용 (~1초)

# Case 2: 중간 복잡도 → 하이브리드
result2 = generator.generate("A rectangular prism with 4 circular holes.")
# → Text2CAD로 초안 + FreeCAD로 정제 (~5초)

# Case 3: 복잡한 형상 → FreeCAD
result3 = generator.generate("A helical gear with 30 teeth and 20° pressure angle.")
# → FreeCAD Tool Calling (~10초)
```

---

## 💰 비용 비교

### Text2CAD
- **모델 실행**: 무료 (로컬 GPU)
- **초기 투자**: GPU 필요 (~RTX 3090 수준)
- **전기세**: 높음 (GPU 상시 가동)
- **Fine-tuning**: 가능 (데이터 있을 때)

### FreeCAD Tool Calling
- **LLM API**: 유료 (Groq는 무료)
- **초기 투자**: 없음 (CPU만 있으면 됨)
- **전기세**: 낮음
- **Fine-tuning**: 불필요 (LLM 활용)

---

## 📋 의사결정 체크리스트

### Text2CAD를 선택하세요 (✅):
- [ ] GPU가 있다 (RTX 3080 이상)
- [ ] 빠른 배치 처리가 필요하다
- [ ] DeepCAD와 유사한 형상을 생성한다
- [ ] 학습 데이터가 있다 (Fine-tuning용)
- [ ] Sketch + Extrude로 표현 가능한 형상이다
- [ ] 실시간 생성이 중요하다
- [ ] 일관성 있는 출력이 중요하다

### FreeCAD Tool Calling을 선택하세요 (🔧):
- [ ] GPU가 없다
- [ ] 정밀한 제어가 필요하다
- [ ] 다양한 CAD 기능이 필요하다 (Loft, Sweep, Pattern)
- [ ] 커스텀 형상을 만들어야 한다
- [ ] 디버깅과 수정이 잦다
- [ ] 파라메트릭 모델이 필요하다
- [ ] LLM API 비용이 부담스럽지 않다

### 하이브리드를 선택하세요 (⚡):
- [ ] 두 가지 모두 장점을 취하고 싶다
- [ ] 형상의 복잡도가 다양하다
- [ ] 개발 리소스가 충분하다
- [ ] 최고의 품질을 원한다

---

## 🎓 학습 및 Fine-tuning

### Text2CAD Fine-tuning 가능 여부

**✅ 가능합니다!** 하지만 조건이 있습니다:

#### 필요한 것:
1. **학습 데이터**: 10,000+ CAD 모델 + 텍스트 주석
2. **GPU**: A100 80GB (batch_size=16) 또는 RTX 3090 24GB (batch_size=4)
3. **시간**: ~3-7일 (150 epochs)
4. **저장 공간**: ~500GB (모델 + 데이터)

#### 학습 절차:

```bash
# 1. 데이터 준비
cd Text2CAD/CadSeqProc
python json2vec.py \
    --input_dir ./your_cad_json \
    --output_dir ./cad_vec \
    --split_json ./your_split.json \
    --padding --deduplicate

# 2. 텍스트 주석 준비
# your_annotations.pkl 형식:
# {
#     "0000/00000001": "A simple ring with...",
#     "0000/00000002": "A rectangular prism...",
#     ...
# }

# 3. Config 수정
vim Cad_VLM/config/trainer.yaml
# - cad_seq_dir: ./cad_vec
# - prompt_path: ./your_annotations.pkl
# - split_filepath: ./your_split.json

# 4. 학습 시작
cd Cad_VLM
python train.py --config_path config/trainer.yaml
```

#### Fine-tuning 시나리오:

**시나리오 1: 특정 도메인 특화**
```python
# 예: 자동차 부품만 학습
data = filter_automotive_parts(deepcad_data)
train_text2cad(data)  # 자동차 부품 생성에 특화
```

**시나리오 2: 한국어 프롬프트**
```python
# 영어 → 한국어 데이터셋
annotations_kr = translate_to_korean(annotations_en)
train_text2cad(cad_vec, annotations_kr)  # 한국어 지원
```

---

## 🚦 실전 권장사항

### 초기 프로토타입 단계
1. **Text2CAD 사전 학습 모델부터 시작**
   - Gradio 데모로 빠른 검증
   - 어떤 형상이 잘 되는지 파악
   - 2-3일 내에 프로토타입 완성

2. **성능 평가**
   - 생성 품질 확인
   - 실패 케이스 분석
   - 사용자 피드백 수집

### 개발 단계
3. **FreeCAD Tool Calling 구현**
   - 범용성 확보
   - 정밀한 제어 가능
   - 1-2주 내에 기본 기능 완성

4. **하이브리드 시스템 구축**
   - 두 가지 장점 결합
   - 자동 방법 선택 로직
   - 최적화된 성능

### 프로덕션 단계
5. **Fine-tuning (선택)**
   - 충분한 데이터가 있다면
   - 특정 도메인 특화
   - 2-4주 소요

---

## 📊 최종 권장사항

### ⚡ **빠른 시작을 원한다면: Text2CAD**

```bash
# 오늘 시작해서 내일 데모 가능
git clone https://github.com/sadilkhan/text2cad
cd text2cad
conda env create -f environment.yml
# 체크포인트 다운로드
cd App && python app.py
```

### 🔧 **장기적 관점이라면: FreeCAD Tool Calling**

```python
# 유연성과 확장성
# 모든 CAD 기능 활용 가능
# LLM 발전에 따라 자동 개선
```

### 🎯 **최적의 선택: 하이브리드**

```python
# 단계별 진행:
# Week 1-2: Text2CAD 프로토타입
# Week 3-4: FreeCAD Tool Calling 추가
# Week 5-6: 하이브리드 시스템 구축
# Week 7+: Fine-tuning (선택)
```

---

## 🔗 리소스

- **Text2CAD 논문**: https://arxiv.org/abs/2409.17106
- **사전 학습 모델**: https://huggingface.co/datasets/SadilKhan/Text2CAD
- **DeepCAD 데이터**: https://github.com/ChrisWu1997/DeepCAD
- **FreeCAD API**: https://wiki.freecad.org/Python_scripting_tutorial

---

**결론**: Text2CAD 사전 학습 모델로 시작하되, 장기적으로는 FreeCAD Tool Calling과 결합하는 하이브리드 접근이 최선입니다! 🚀

