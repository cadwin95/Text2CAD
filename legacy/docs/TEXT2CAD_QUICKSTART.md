# Text2CAD 사전 학습 모델 빠른 시작 가이드

## 🎯 목표

**30분 안에** Text2CAD 사전 학습 모델로 텍스트에서 3D CAD 모델 생성하기!

## ✅ 사전 준비물

- **OS**: Linux (Ubuntu 20.04+ 권장)
- **Python**: 3.9
- **GPU**: CUDA 지원 GPU (권장: RTX 3060 이상, 4GB+ VRAM)
- **저장 공간**: ~10GB

---

## 📦 1단계: 환경 설정 (10분)

### Option A: Conda 환경 (권장)

```bash
# 1. 저장소 확인
cd /Users/kshs95/Study/Text2CAD/Text2CAD

# 2. Conda 환경 생성
conda env create --file environment.yml

# 3. 환경 활성화
conda activate text2cad

# 4. 설치 확인
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
python -c "from OCC.Core import BRep; print('PythonOCC: OK')"
python -c "import transformers; print('Transformers: OK')"
```

### Option B: 수동 설치 (문제 발생 시)

```bash
# 1. 새 Conda 환경 생성
conda create -n text2cad python=3.9 -y
conda activate text2cad

# 2. PyTorch 설치 (CUDA 11.8)
conda install pytorch=2.2.1 torchvision=0.17.1 pytorch-cuda=11.8 -c pytorch -c nvidia

# 3. PythonOCC 설치
conda install -c conda-forge pythonocc-core=7.7.2

# 4. 기타 패키지 설치
pip install transformers nltk gradio trimesh pillow pyvista loguru rich tensorboard
```

### 문제 해결

#### CUDA 오류
```bash
# CUDA 버전 확인
nvidia-smi

# PyTorch CUDA 버전 확인
python -c "import torch; print(torch.version.cuda)"

# 불일치 시 PyTorch 재설치
conda install pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia
```

#### PythonOCC 오류
```bash
# PythonOCC 재설치
conda remove pythonocc-core
conda install -c conda-forge pythonocc-core=7.7.2
```

---

## 📥 2단계: 모델 체크포인트 다운로드 (5분)

```bash
# 1. 체크포인트 디렉토리 생성
cd /Users/kshs95/Study/Text2CAD/Text2CAD
mkdir -p checkpoints
cd checkpoints

# 2. HuggingFace에서 다운로드
# Option A: wget (가장 간단)
wget https://huggingface.co/datasets/SadilKhan/Text2CAD/resolve/main/text2cad_v1.0/Text2CAD_1.0.pth

# Option B: curl
curl -L -o Text2CAD_1.0.pth https://huggingface.co/datasets/SadilKhan/Text2CAD/resolve/main/text2cad_v1.0/Text2CAD_1.0.pth

# Option C: huggingface-cli
pip install huggingface-hub
huggingface-cli download SadilKhan/Text2CAD text2cad_v1.0/Text2CAD_1.0.pth --local-dir ./

# 3. 다운로드 확인
ls -lh Text2CAD_1.0.pth
# 약 500-600MB 크기여야 함
```

---

## ⚙️ 3단계: Config 파일 수정 (3분)

```bash
cd /Users/kshs95/Study/Text2CAD/Text2CAD/Cad_VLM

# Config 파일 복사 (백업)
cp config/inference_user_input.yaml config/inference_user_input.yaml.bak

# Config 파일 편집
vim config/inference_user_input.yaml
# 또는
code config/inference_user_input.yaml
```

### 수정할 내용:

```yaml
# config/inference_user_input.yaml

text_encoder:
  text_embedder:
    model_name: "bert_large_uncased"
    max_seq_len: 512
    cache_dir: "/Users/kshs95/.cache/huggingface"  # ← 수정 (HuggingFace 캐시 디렉토리)

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
  num_workers: 4  # ← CPU 코어 수에 맞게 조정
  prefetch_factor: 2
  log_dir: "/Users/kshs95/Study/Text2CAD/Text2CAD/outputs"  # ← 수정
  checkpoint_path: "/Users/kshs95/Study/Text2CAD/Text2CAD/checkpoints/Text2CAD_1.0.pth"  # ← 수정
  nucleus_prob: 0
  sampling_type: "max"
  prompt_file: ""  # 파일 사용 시에만 지정

debug: False
info: "Inference"
```

### 빠른 수정 스크립트:

```bash
cd /Users/kshs95/Study/Text2CAD/Text2CAD/Cad_VLM

cat > config/inference_user_input.yaml << 'EOF'
text_encoder:
  text_embedder:
    model_name: "bert_large_uncased"
    max_seq_len: 512
    cache_dir: "/Users/kshs95/.cache/huggingface"

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
  num_workers: 4
  prefetch_factor: 2
  log_dir: "/Users/kshs95/Study/Text2CAD/Text2CAD/outputs"
  checkpoint_path: "/Users/kshs95/Study/Text2CAD/Text2CAD/checkpoints/Text2CAD_1.0.pth"
  nucleus_prob: 0
  sampling_type: "max"
  prompt_file: ""

debug: False
info: "Inference"
EOF
```

---

## 🚀 4단계: 테스트 실행 (5분)

### A. 단일 프롬프트 테스트

```bash
cd /Users/kshs95/Study/Text2CAD/Text2CAD/Cad_VLM

# 간단한 링 생성
python test_user_input.py \
    --config_path config/inference_user_input.yaml \
    --prompt "A simple ring."

# 출력 확인
ls -lh ../outputs/
# output.stl 또는 output_*.pkl 파일 확인
```

### B. 다양한 프롬프트 테스트

```bash
# 실린더
python test_user_input.py \
    --config_path config/inference_user_input.yaml \
    --prompt "A cylindrical object."

# 구멍 뚫린 블록
python test_user_input.py \
    --config_path config/inference_user_input.yaml \
    --prompt "A rectangular prism with a circular hole in the center."

# 복잡한 형상
python test_user_input.py \
    --config_path config/inference_user_input.yaml \
    --prompt "The CAD model features a rectangular metal plate with four holes along its length."
```

### C. 배치 프롬프트 테스트

```bash
# 프롬프트 파일 생성
cat > prompts.txt << 'EOF'
A simple ring.
A rectangular prism.
A cylindrical object with a hole through the center.
A 3D star shape with 5 points.
EOF

# 배치 실행
python test_user_input.py \
    --config_path config/inference_user_input.yaml \
    --prompt_file prompts.txt
```

---

## 🎨 5단계: Gradio 데모 실행 (2분)

```bash
cd /Users/kshs95/Study/Text2CAD/Text2CAD/App

# Config 파일 경로 확인
head -70 app.py | tail -5
# config_path = "../Cad_VLM/config/inference_user_input.yaml" 인지 확인

# Gradio 실행
python app.py

# 또는 포트 지정
python app.py --server-port 7860
```

### 브라우저에서 접속:
```
http://localhost:7860
```

### 예제 프롬프트들:
- "A ring."
- "A rectangular prism."
- "A 3D star shape with 5 points."
- "The CAD model features a cylindrical object with a cylindrical hole in the center."
- "The CAD model features a rectangular metal plate with four holes along its length."

---

## 🐍 6단계: Python 스크립트로 사용 (5분)

### 간단한 스크립트 작성

```python
# test_text2cad.py
import torch
import yaml
import sys
import os

# Path 설정
sys.path.append("/Users/kshs95/Study/Text2CAD/Text2CAD")

from Cad_VLM.models.text2cad import Text2CAD
from CadSeqProc.cad_sequence import CADSequence
from CadSeqProc.utility.macro import MAX_CAD_SEQUENCE_LENGTH, N_BIT

def load_model(config_path, device):
    """모델 로드"""
    # Config 로드
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # 모델 초기화
    cad_config = config["cad_decoder"]
    cad_config["cad_seq_len"] = MAX_CAD_SEQUENCE_LENGTH
    
    model = Text2CAD(
        text_config=config["text_encoder"],
        cad_config=cad_config
    ).to(device)
    
    # 체크포인트 로드
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
    
    return model

def generate_cad(model, text, device, output_path="output.stl"):
    """텍스트 → 3D 모델"""
    print(f"📝 프롬프트: {text}")
    
    # 추론
    with torch.no_grad():
        pred_cad_seq_dict = model.test_decode(
            texts=[text],
            maxlen=MAX_CAD_SEQUENCE_LENGTH,
            nucleus_prob=0,
            topk_index=1,
            device=device
        )
    
    # Vector → CADSequence
    pred_cad = CADSequence.from_vec(
        pred_cad_seq_dict["cad_vec"][0].cpu().numpy(),
        bit=N_BIT,
        post_processing=True
    )
    
    # Mesh 생성
    try:
        pred_cad.create_mesh()
        pred_cad.mesh.export(output_path)
        print(f"✅ STL 파일 생성: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Mesh 생성 실패: {e}")
        # STEP 파일로 시도
        try:
            step_path = output_path.replace(".stl", ".step")
            pred_cad.save_stp(
                filename=os.path.basename(step_path).replace(".step", ""),
                output_dir=os.path.dirname(step_path) or ".",
                type="step"
            )
            print(f"✅ STEP 파일 생성: {step_path}")
            return True
        except Exception as e2:
            print(f"❌ STEP 파일도 실패: {e2}")
            return False

def main():
    # 설정
    config_path = "/Users/kshs95/Study/Text2CAD/Text2CAD/Cad_VLM/config/inference_user_input.yaml"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"🖥️  Device: {device}")
    
    # 모델 로드
    print("📦 모델 로드 중...")
    model = load_model(config_path, device)
    print("✅ 모델 로드 완료!")
    
    # 테스트 프롬프트들
    prompts = [
        "A simple ring.",
        "A rectangular prism with a hole in the middle.",
        "A cylindrical object.",
    ]
    
    # 생성
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'='*60}")
        print(f"테스트 {i}/{len(prompts)}")
        print(f"{'='*60}")
        generate_cad(model, prompt, device, f"output_{i}.stl")
    
    print(f"\n{'='*60}")
    print("✅ 모든 테스트 완료!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
```

### 실행:

```bash
cd /Users/kshs95/Study/Text2CAD/Text2CAD
python test_text2cad.py
```

---

## 🔍 출력 확인

### STL 파일 뷰어로 열기

```bash
# macOS
open output.stl

# Linux (MeshLab)
meshlab output.stl

# Online Viewer
# https://3dviewer.net/ 에서 업로드
```

### Python으로 시각화

```python
import trimesh
import matplotlib.pyplot as plt

# STL 로드
mesh = trimesh.load("output.stl")

# 정보 출력
print(f"Vertices: {len(mesh.vertices)}")
print(f"Faces: {len(mesh.faces)}")
print(f"Volume: {mesh.volume:.2f}")
print(f"Surface Area: {mesh.area:.2f}")

# 시각화
mesh.show()
```

---

## 🎯 성능 벤치마크

### 예상 실행 시간:

| 단계 | CPU | GPU (RTX 3060) | GPU (RTX 4090) |
|------|-----|----------------|----------------|
| **모델 로드** | 10초 | 5초 | 3초 |
| **BERT 임베딩** | 2초 | 0.5초 | 0.2초 |
| **CAD Decoding** | 8초 | 1초 | 0.5초 |
| **Mesh 생성** | 3초 | 3초 | 3초 |
| **총 시간** | ~23초 | ~9.5초 | ~6.7초 |

### 배치 처리 (8개):

| Device | 시간 | 모델당 평균 |
|--------|------|------------|
| CPU | ~120초 | ~15초 |
| RTX 3060 | ~25초 | ~3.1초 |
| RTX 4090 | ~15초 | ~1.9초 |

---

## 🐛 문제 해결

### 1. CUDA Out of Memory

```python
# Config 파일에서 batch_size 줄이기
test:
  batch_size: 1  # 이미 1이면 문제 없음
```

```bash
# 또는 CPU로 실행
export CUDA_VISIBLE_DEVICES=""
python test_user_input.py ...
```

### 2. BERT 모델 다운로드 실패

```bash
# 수동 다운로드
python -c "from transformers import BertModel; BertModel.from_pretrained('bert-large-uncased')"

# 또는 캐시 디렉토리 변경
export HF_HOME=/path/to/large/disk/.cache/huggingface
```

### 3. Mesh 생성 실패

```python
# CADSequence 정보 확인
print(pred_cad)
print(f"Sketches: {len(pred_cad.sketch_seq)}")
print(f"Extrudes: {len(pred_cad.extrude_seq)}")

# 각 Sketch 확인
for i, skt in enumerate(pred_cad.sketch_seq):
    try:
        face = skt.create_skt_face()
        print(f"Sketch {i}: OK")
    except Exception as e:
        print(f"Sketch {i}: FAILED - {e}")
```

### 4. 경로 오류

```bash
# 절대 경로 사용
pwd  # 현재 디렉토리 확인
# Config 파일에서 모든 경로를 절대 경로로 수정
```

---

## 📊 출력 품질 평가

### 좋은 출력 예제:
- ✅ "A simple ring." → 완벽한 원형 링
- ✅ "A rectangular prism." → 깔끔한 직육면체
- ✅ "A cylindrical object." → 정확한 원기둥

### 주의가 필요한 예제:
- ⚠️ "A gear with 20 teeth." → 대략적인 형상만 생성
- ⚠️ "A helical spring." → 학습 데이터에 없으면 실패
- ⚠️ "A human face." → CAD 모델이 아니므로 실패

### 실패하는 예제:
- ❌ 학습 데이터에 없는 복잡한 형상
- ❌ 자유 곡면 (Loft, Sweep)
- ❌ 패턴 (Pattern, Array)
- ❌ 어셈블리 (여러 부품)

---

## 🎓 다음 단계

### 1. Fine-tuning (선택)
- 자신만의 CAD 데이터로 모델 개선
- 특정 도메인 특화 (예: 자동차 부품, 건축)
- 2-4주 소요

### 2. FreeCAD 통합
- Text2CAD 출력을 FreeCAD로 변환
- 하이브리드 시스템 구축
- 1-2주 소요

### 3. API 서버 구축
```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/generate")
async def generate(prompt: str):
    result = model.test_decode([prompt], ...)
    return {"stl_url": save_and_return_url(result)}
```

---

## 📚 참고 자료

- **논문**: https://arxiv.org/abs/2409.17106
- **HuggingFace**: https://huggingface.co/datasets/SadilKhan/Text2CAD
- **GitHub**: https://github.com/sadilkhan/text2cad
- **데모**: https://sadilkhan.github.io/text2cad-project/

---

## ✅ 체크리스트

완료한 항목에 체크하세요:

- [ ] Conda 환경 생성 완료
- [ ] PyTorch + CUDA 작동 확인
- [ ] PythonOCC 설치 확인
- [ ] 체크포인트 다운로드 완료 (500MB)
- [ ] Config 파일 수정 완료
- [ ] 단일 프롬프트 테스트 성공
- [ ] STL 파일 생성 확인
- [ ] Gradio 데모 실행 성공
- [ ] 브라우저에서 3D 모델 확인

---

**축하합니다! 🎉** Text2CAD 사전 학습 모델을 성공적으로 실행했습니다!

이제 다음을 시도해보세요:
1. 다양한 프롬프트 테스트
2. FreeCAD와 통합
3. 자신만의 데이터로 Fine-tuning

질문이 있으면 언제든지 물어보세요! 🚀

