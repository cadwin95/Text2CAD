"""
OpenPipe 데이터 수집기
LiteLLM proxy를 통해 도구 호출 데이터를 자동으로 수집합니다.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai 패키지가 설치되지 않았습니다.")

from ..mcp_server.server import get_tools_for_openai


class DataCollector:
    """OpenPipe 데이터 수집기"""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        log_dir: str = "./data/logs"
    ):
        """
        데이터 수집기 초기화
        
        Args:
            base_url: LiteLLM proxy URL (기본값: 환경변수 LITELLM_BASE_URL)
            api_key: API 키 (기본값: 환경변수 LITELLM_API_KEY)
            log_dir: 로그 저장 디렉토리
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 패키지가 필요합니다: uv add openai")
        
        self.base_url = base_url or os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        self.api_key = api_key or os.getenv("LITELLM_API_KEY", "sk-1234")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenAI 클라이언트 초기화
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # FreeCAD 도구 로드
        self.tools = get_tools_for_openai()
    
    def collect_interaction(
        self,
        user_message: str,
        model: str = "groq/llama-3.1-8b-instruct",
        max_tokens: int = 500,
        save_log: bool = True
    ) -> Dict:
        """
        사용자 메시지에 대한 상호작용을 수집합니다.
        
        Args:
            user_message: 사용자 메시지
            model: 사용할 모델 이름
            max_tokens: 최대 토큰 수
            save_log: 로그 저장 여부
        
        Returns:
            응답 데이터
        """
        messages = [{"role": "user", "content": user_message}]
        
        # OpenPipe는 LiteLLM을 통해 자동으로 로깅됨
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=self.tools,
            max_tokens=max_tokens
        )
        
        # 로컬 로그 저장
        if save_log:
            self._save_log(user_message, response)
        
        return {
            "user_message": user_message,
            "model": model,
            "response": response.model_dump() if hasattr(response, 'model_dump') else dict(response),
            "has_tool_calls": bool(response.choices[0].message.tool_calls)
        }
    
    def _save_log(self, user_message: str, response):
        """로그를 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"interaction_{timestamp}.json"
        
        log_data = {
            "timestamp": timestamp,
            "user_message": user_message,
            "response": response.model_dump() if hasattr(response, 'model_dump') else dict(response)
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def batch_collect(self, messages: List[str], model: str = "groq/llama-3.1-8b-instruct") -> List[Dict]:
        """
        여러 메시지를 배치로 수집합니다.
        
        Args:
            messages: 사용자 메시지 리스트
            model: 사용할 모델 이름
        
        Returns:
            응답 데이터 리스트
        """
        results = []
        for i, msg in enumerate(messages, 1):
            print(f"[{i}/{len(messages)}] 수집 중: {msg[:50]}...")
            try:
                result = self.collect_interaction(msg, model)
                results.append(result)
            except Exception as e:
                print(f"오류 발생: {e}")
                results.append({
                    "user_message": msg,
                    "error": str(e)
                })
        
        return results


def create_test_scenarios() -> List[str]:
    """테스트 시나리오 생성"""
    scenarios = [
        # 한국어 명령
        "10mm x 10mm x 10mm 크기의 박스를 만들어줘",
        "반지름 5mm, 높이 20mm인 실린더를 생성해",
        "반지름 7mm인 구를 만들어",
        "밑면 반지름 10mm, 윗면 반지름 5mm, 높이 15mm인 원뿔을 생성해줘",
        "새 문서를 만들고 20x20x20 박스를 추가해",
        
        # 영어 명령
        "Create a box with dimensions 15mm x 15mm x 15mm",
        "Make a cylinder with radius 8mm and height 25mm",
        "Generate a sphere with radius 10mm",
        "Create a new document",
        "Save the current document as test.FCStd",
        
        # 복잡한 명령
        "반지름 5mm인 구와 10x10x10 박스를 만들어줘",
        "실린더를 만들고 이미지로 저장해줘",
    ]
    return scenarios


def main():
    """메인 함수 - 테스트 시나리오 수집"""
    print("OpenPipe 데이터 수집기 시작...\n")
    
    # 데이터 수집기 초기화
    collector = DataCollector()
    
    # 테스트 시나리오 생성
    scenarios = create_test_scenarios()
    
    print(f"총 {len(scenarios)}개 시나리오를 수집합니다.\n")
    
    # 배치 수집
    results = collector.batch_collect(scenarios)
    
    # 결과 요약
    successful = sum(1 for r in results if "error" not in r)
    with_tool_calls = sum(1 for r in results if r.get("has_tool_calls", False))
    
    print(f"\n{'='*60}")
    print(f"수집 완료!")
    print(f"  - 성공: {successful}/{len(scenarios)}")
    print(f"  - Tool calls 포함: {with_tool_calls}/{successful}")
    print(f"  - 로그 저장 위치: {collector.log_dir}")
    print(f"{'='*60}\n")
    
    # OpenPipe 대시보드 안내
    print("다음 단계:")
    print("1. OpenPipe 대시보드에서 수집된 데이터 확인")
    print("2. 데이터 품질 검토 및 필터링")
    print("3. Fine-tuning 데이터셋 준비")


if __name__ == "__main__":
    main()

