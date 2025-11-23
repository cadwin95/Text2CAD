#!/usr/bin/env python3
"""
Text2CAD 사전 학습 모델 테스트 스크립트
"""
import torch
import yaml
import sys
import os
from pathlib import Path

# Path 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEXT2CAD_DIR = PROJECT_ROOT / "Text2CAD"

sys.path.insert(0, str(TEXT2CAD_DIR))

from Cad_VLM.models.text2cad import Text2CAD
from CadSeqProc.cad_sequence import CADSequence
from CadSeqProc.utility.macro import MAX_CAD_SEQUENCE_LENGTH, N_BIT


def load_model(config_path: str, device: torch.device):
    """모델 로드"""
    print(f"📦 모델 로드 중...")
    
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
    checkpoint_path = config["test"]["checkpoint_path"]
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(
            f"체크포인트를 찾을 수 없습니다: {checkpoint_path}\n"
            f"다음 명령으로 다운로드하세요:\n"
            f"wget https://huggingface.co/datasets/SadilKhan/Text2CAD/resolve/main/text2cad_v1.0/Text2CAD_1.0.pth -O {checkpoint_path}"
        )
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # 모듈 프리픽스 제거
    pretrained_dict = {}
    for key, value in checkpoint["model_state_dict"].items():
        if key.startswith("module."):
            pretrained_dict[key[7:]] = value
        else:
            pretrained_dict[key] = value
    
    model.load_state_dict(pretrained_dict, strict=False)
    model.eval()
    
    print(f"✅ 모델 로드 완료!")
    return model


def generate_cad(model, text: str, device: torch.device, output_path: str = "output.stl"):
    """텍스트 → 3D 모델"""
    print(f"\n{'='*60}")
    print(f"📝 프롬프트: {text}")
    print(f"{'='*60}")
    
    # 추론
    print("🧠 추론 중...")
    with torch.no_grad():
        pred_cad_seq_dict = model.test_decode(
            texts=[text],
            maxlen=MAX_CAD_SEQUENCE_LENGTH,
            nucleus_prob=0,
            topk_index=1,
            device=device
        )
    
    # Vector → CADSequence
    print("🔄 CAD 시퀀스 변환 중...")
    pred_cad = CADSequence.from_vec(
        pred_cad_seq_dict["cad_vec"][0].cpu().numpy(),
        bit=N_BIT,
        post_processing=True
    )
    
    print(f"📊 CAD 정보:")
    print(f"  - Sketches: {len(pred_cad.sketch_seq)}")
    print(f"  - Extrudes: {len(pred_cad.extrude_seq)}")
    
    # Mesh 생성
    print("🎨 Mesh 생성 중...")
    try:
        pred_cad.create_mesh()
        pred_cad.mesh.export(output_path)
        print(f"✅ STL 파일 생성: {output_path}")
        print(f"  - Vertices: {len(pred_cad.mesh.vertices)}")
        print(f"  - Faces: {len(pred_cad.mesh.faces)}")
        return True, output_path
    except Exception as e:
        print(f"⚠️  Mesh 생성 실패: {e}")
        # STEP 파일로 시도
        try:
            step_path = output_path.replace(".stl", ".step")
            output_dir = os.path.dirname(step_path) or "."
            filename = os.path.basename(step_path).replace(".step", "")
            pred_cad.save_stp(filename=filename, output_dir=output_dir, type="step")
            print(f"✅ STEP 파일 생성: {step_path}")
            return True, step_path
        except Exception as e2:
            print(f"❌ STEP 파일도 실패: {e2}")
            return False, None


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("Text2CAD 사전 학습 모델 테스트")
    print("="*60 + "\n")
    
    # 설정
    config_path = TEXT2CAD_DIR / "Cad_VLM" / "config" / "inference_user_input.yaml"
    output_dir = PROJECT_ROOT / "outputs" / "text2cad"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Device 설정
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Device: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print()
    
    # 모델 로드
    try:
        model = load_model(str(config_path), device)
    except FileNotFoundError as e:
        print(f"\n❌ 오류: {e}")
        return
    except Exception as e:
        print(f"\n❌ 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 테스트 프롬프트들
    prompts = [
        ("simple_ring", "A simple ring."),
        ("rectangular_prism", "A rectangular prism."),
        ("cylinder_with_hole", "A cylindrical object with a hole through the center."),
        ("block_with_holes", "A rectangular prism with a circular hole in the middle."),
        ("metal_plate", "The CAD model features a rectangular metal plate with four holes along its length."),
    ]
    
    # 생성
    results = []
    for i, (name, prompt) in enumerate(prompts, 1):
        print(f"\n{'#'*60}")
        print(f"테스트 {i}/{len(prompts)}: {name}")
        print(f"{'#'*60}")
        
        output_path = output_dir / f"{name}.stl"
        success, path = generate_cad(model, prompt, device, str(output_path))
        results.append((name, prompt, success, path))
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("✅ 모든 테스트 완료!")
    print(f"{'='*60}\n")
    
    print("📊 결과 요약:")
    successful = sum(1 for _, _, success, _ in results if success)
    print(f"  - 성공: {successful}/{len(results)}")
    print(f"  - 실패: {len(results) - successful}/{len(results)}")
    print()
    
    print("📁 생성된 파일:")
    for name, prompt, success, path in results:
        if success and path:
            status = "✅"
            print(f"  {status} {name}: {path}")
        else:
            status = "❌"
            print(f"  {status} {name}: 실패")
    
    print(f"\n출력 디렉토리: {output_dir}")
    print(f"\n{'='*60}\n")
    
    # 뷰어 안내
    print("🔍 생성된 모델 확인:")
    print("  - macOS: open output.stl")
    print("  - Linux: meshlab output.stl")
    print("  - Online: https://3dviewer.net/")
    print()


if __name__ == "__main__":
    main()

