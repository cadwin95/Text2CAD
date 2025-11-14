"""
Unsloth Fine-tuning 파이프라인
OpenPipe에서 수집한 데이터로 Qwen 모델을 fine-tuning합니다.
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

try:
    from unsloth import FastLanguageModel
    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False
    print("Warning: unsloth 패키지가 설치되지 않았습니다.")

try:
    from trl import SFTTrainer
    from transformers import TrainingArguments
    TRL_AVAILABLE = True
except ImportError:
    TRL_AVAILABLE = False
    print("Warning: trl, transformers 패키지가 설치되지 않았습니다.")

try:
    from datasets import Dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    print("Warning: datasets 패키지가 설치되지 않았습니다.")


class FreeCADFineTuner:
    """FreeCAD tool calling을 위한 fine-tuner"""
    
    def __init__(
        self,
        model_name: str = "unsloth/Qwen2.5-3B-Instruct",
        max_seq_length: int = 8192,
        load_in_4bit: bool = True,
        output_dir: str = "./models/finetuned"
    ):
        """
        Fine-tuner 초기화
        
        Args:
            model_name: 베이스 모델 이름
            max_seq_length: 최대 시퀀스 길이
            load_in_4bit: 4bit 양자화 로드 여부
            output_dir: 출력 디렉토리
        """
        if not UNSLOTH_AVAILABLE:
            raise ImportError("unsloth 패키지가 필요합니다: uv add unsloth")
        
        if not TRL_AVAILABLE:
            raise ImportError("trl 패키지가 필요합니다: uv add trl")
        
        if not DATASETS_AVAILABLE:
            raise ImportError("datasets 패키지가 필요합니다: uv add datasets")
        
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.load_in_4bit = load_in_4bit
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.tokenizer = None
    
    def load_model(self):
        """모델과 토크나이저 로드"""
        print(f"모델 로드 중: {self.model_name}")
        
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.model_name,
            max_seq_length=self.max_seq_length,
            load_in_4bit=self.load_in_4bit,
            dtype=None,  # 자동 감지
            device_map="auto"
        )
        
        print("모델 로드 완료!")
    
    def setup_lora(
        self,
        r: int = 16,
        lora_alpha: int = 16,
        lora_dropout: float = 0.05,
        target_modules: Optional[List[str]] = None
    ):
        """LoRA 설정"""
        if self.model is None:
            self.load_model()
        
        if target_modules is None:
            target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
        
        print(f"LoRA 설정 중 (r={r}, alpha={lora_alpha})...")
        
        self.model = FastLanguageModel.get_peft_model(
            self.model,
            r=r,
            target_modules=target_modules,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=42,
        )
        
        print("LoRA 설정 완료!")
    
    def load_openpipe_data(self, data_path: str) -> List[Dict]:
        """
        OpenPipe 데이터 로드
        
        Args:
            data_path: OpenPipe 데이터 파일 경로 또는 디렉토리
        
        Returns:
            대화 데이터 리스트
        """
        path = Path(data_path)
        conversations = []
        
        if path.is_file():
            # 단일 파일
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    conversations.extend(data)
                elif "messages" in data:
                    conversations.append(data)
        elif path.is_dir():
            # 디렉토리의 모든 JSON 파일
            for file_path in path.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        conversations.extend(data)
                    elif "messages" in data or "response" in data:
                        conversations.append(data)
        
        print(f"데이터 로드 완료: {len(conversations)}개 대화")
        return conversations
    
    def convert_to_training_format(self, conversations: List[Dict]) -> List[Dict]:
        """
        대화 데이터를 학습 포맷으로 변환
        
        Args:
            conversations: OpenPipe 또는 합성 데이터
        
        Returns:
            학습용 데이터
        """
        training_data = []
        
        for conv in conversations:
            # OpenPipe 로그 포맷
            if "response" in conv:
                user_msg = conv.get("user_message", "")
                response = conv["response"]
                
                # 응답에서 메시지 추출
                if "choices" in response:
                    assistant_msg = response["choices"][0].get("message", {}).get("content", "")
                    
                    training_data.append({
                        "text": self._format_conversation([
                            {"role": "user", "content": user_msg},
                            {"role": "assistant", "content": assistant_msg}
                        ])
                    })
            
            # 직접 메시지 포맷
            elif "messages" in conv:
                training_data.append({
                    "text": self._format_conversation(conv["messages"])
                })
            
            # 명령어 리스트 (합성 데이터)
            elif "commands" in conv:
                for cmd in conv["commands"]:
                    training_data.append({
                        "text": self._format_conversation([
                            {"role": "user", "content": cmd},
                            {"role": "assistant", "content": "명령을 실행하겠습니다."}
                        ])
                    })
        
        print(f"학습 데이터 변환 완료: {len(training_data)}개")
        return training_data
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """대화를 ChatML 포맷으로 변환"""
        formatted = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        return formatted
    
    def train(
        self,
        train_data: List[Dict],
        per_device_train_batch_size: int = 2,
        gradient_accumulation_steps: int = 4,
        warmup_steps: int = 10,
        max_steps: int = 100,
        learning_rate: float = 2e-4,
        logging_steps: int = 10,
        save_steps: int = 50
    ):
        """
        모델 학습
        
        Args:
            train_data: 학습 데이터
            per_device_train_batch_size: 배치 크기
            gradient_accumulation_steps: 그래디언트 누적 스텝
            warmup_steps: 워밍업 스텝
            max_steps: 최대 학습 스텝
            learning_rate: 학습률
            logging_steps: 로깅 간격
            save_steps: 저장 간격
        """
        if self.model is None:
            self.setup_lora()
        
        # Dataset 생성
        dataset = Dataset.from_list(train_data)
        
        # 학습 인자 설정
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"checkpoint_{timestamp}"
        
        training_args = TrainingArguments(
            output_dir=str(output_path),
            per_device_train_batch_size=per_device_train_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            warmup_steps=warmup_steps,
            max_steps=max_steps,
            learning_rate=learning_rate,
            logging_steps=logging_steps,
            save_steps=save_steps,
            save_total_limit=3,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=42,
            fp16=True,
        )
        
        # Trainer 초기화
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=dataset,
            max_seq_length=self.max_seq_length,
            args=training_args,
            dataset_text_field="text",
        )
        
        print(f"\n{'='*60}")
        print("학습 시작...")
        print(f"  - 데이터: {len(train_data)}개")
        print(f"  - 최대 스텝: {max_steps}")
        print(f"  - 학습률: {learning_rate}")
        print(f"  - 출력 경로: {output_path}")
        print(f"{'='*60}\n")
        
        # 학습 실행
        trainer.train()
        
        print(f"\n{'='*60}")
        print("학습 완료!")
        print(f"{'='*60}\n")
        
        return output_path
    
    def save_model(self, output_path: str, save_method: str = "merged_16bit"):
        """
        모델 저장
        
        Args:
            output_path: 저장 경로
            save_method: 저장 방법 (merged_16bit, lora, gguf 등)
        """
        if self.model is None:
            raise ValueError("저장할 모델이 없습니다. 먼저 학습을 진행하세요.")
        
        save_path = Path(output_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        print(f"모델 저장 중: {save_path}")
        
        if save_method == "merged_16bit":
            self.model.save_pretrained_merged(
                str(save_path),
                self.tokenizer,
                save_method="merged_16bit"
            )
        elif save_method == "lora":
            self.model.save_pretrained(str(save_path))
            self.tokenizer.save_pretrained(str(save_path))
        elif save_method == "gguf":
            # GGUF 포맷으로 저장 (llama.cpp 호환)
            self.model.save_pretrained_gguf(
                str(save_path),
                self.tokenizer,
                quantization_method="q4_k_m"
            )
        
        print(f"저장 완료: {save_path}")


def main():
    """메인 함수 - Fine-tuning 실행"""
    print("FreeCAD Fine-tuning 파이프라인 시작...\n")
    
    # Fine-tuner 초기화
    finetuner = FreeCADFineTuner(
        model_name="unsloth/Qwen2.5-3B-Instruct",
        max_seq_length=8192
    )
    
    # 데이터 로드
    print("1. 데이터 로드")
    data_path = "./data/logs"  # OpenPipe 로그 또는 합성 데이터
    conversations = finetuner.load_openpipe_data(data_path)
    
    if len(conversations) == 0:
        print("학습 데이터가 없습니다!")
        print("먼저 다음을 실행하세요:")
        print("  - python -m src.training.synthetic_data")
        print("  - python -m src.training.data_collector")
        return
    
    # 학습 데이터 변환
    print("\n2. 데이터 변환")
    train_data = finetuner.convert_to_training_format(conversations)
    
    # 모델 로드 및 LoRA 설정
    print("\n3. 모델 로드")
    finetuner.load_model()
    finetuner.setup_lora(r=16, lora_alpha=16)
    
    # 학습
    print("\n4. 학습 시작")
    checkpoint_path = finetuner.train(
        train_data,
        max_steps=100,
        learning_rate=2e-4
    )
    
    # 모델 저장
    print("\n5. 모델 저장")
    final_path = "./models/finetuned/freecad-qwen-final"
    finetuner.save_model(final_path, save_method="merged_16bit")
    
    # GGUF 포맷으로도 저장 (llama.cpp용)
    gguf_path = "./models/finetuned/freecad-qwen-gguf"
    finetuner.save_model(gguf_path, save_method="gguf")
    
    print(f"\n{'='*60}")
    print("Fine-tuning 완료!")
    print(f"  - 체크포인트: {checkpoint_path}")
    print(f"  - 최종 모델: {final_path}")
    print(f"  - GGUF 모델: {gguf_path}")
    print(f"{'='*60}\n")
    
    print("다음 단계:")
    print("1. GGUF 모델을 llama.cpp로 로드")
    print("2. docker-compose.yml에서 모델 경로 변경")
    print("3. Agent로 테스트")


if __name__ == "__main__":
    main()

