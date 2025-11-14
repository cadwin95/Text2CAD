"""
Vision 분석 모듈
VL 모델을 사용하여 CAD 이미지를 분석합니다.
"""

import os
import base64
from typing import Dict, Optional
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

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: pillow 패키지가 설치되지 않았습니다.")


class VisionAnalyzer:
    """CAD 이미지 분석기"""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        model: str = "llava",
        verbose: bool = True
    ):
        """
        Vision 분석기 초기화
        
        Args:
            base_url: LiteLLM proxy URL
            api_key: API 키
            model: 사용할 VL 모델 이름 (llava)
            verbose: 상세 출력 여부
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 패키지가 필요합니다: uv add openai")
        
        if not PIL_AVAILABLE:
            raise ImportError("pillow 패키지가 필요합니다: uv add pillow")
        
        self.base_url = base_url or os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        self.api_key = api_key or os.getenv("LITELLM_API_KEY", "sk-1234")
        self.model = model
        self.verbose = verbose
        
        # OpenAI 클라이언트 초기화
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def analyze_image(
        self,
        image_path: str,
        prompt: Optional[str] = None
    ) -> Dict:
        """
        이미지를 분석합니다.
        
        Args:
            image_path: 이미지 파일 경로
            prompt: 분석 프롬프트 (기본값: CAD 모델 설명)
        
        Returns:
            분석 결과
        """
        # 이미지 파일 확인
        path = Path(image_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"이미지 파일을 찾을 수 없습니다: {image_path}"
            }
        
        # 이미지를 base64로 인코딩
        try:
            image_b64 = self._encode_image(image_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"이미지 인코딩 실패: {str(e)}"
            }
        
        # 기본 프롬프트
        if prompt is None:
            prompt = """이 CAD 모델을 자세히 설명해주세요. 다음 사항을 포함해주세요:
1. 어떤 형태의 객체들이 보이는지
2. 대략적인 크기와 비율
3. 객체들의 배치와 관계
4. 특이사항이나 주목할 만한 특징"""
        
        if self.verbose:
            print(f"이미지 분석 중: {image_path}")
        
        # VL 모델 호출
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            
            if self.verbose:
                print(f"분석 완료: {analysis[:100]}...")
            
            return {
                "success": True,
                "image_path": image_path,
                "analysis": analysis,
                "model": self.model
            }
        
        except Exception as e:
            error_msg = f"Vision 모델 호출 실패: {str(e)}"
            if self.verbose:
                print(f"오류: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg
            }
    
    def _encode_image(self, image_path: str) -> str:
        """
        이미지를 base64로 인코딩합니다.
        
        Args:
            image_path: 이미지 파일 경로
        
        Returns:
            base64 인코딩된 문자열
        """
        # PIL로 이미지 열기 (포맷 확인)
        img = Image.open(image_path)
        
        # PNG로 변환 (필요시)
        if img.format != 'PNG':
            if self.verbose:
                print(f"이미지를 PNG로 변환 중...")
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
        
        # 직접 인코딩
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def analyze_multiple_images(
        self,
        image_paths: list[str],
        prompt: Optional[str] = None
    ) -> list[Dict]:
        """
        여러 이미지를 분석합니다.
        
        Args:
            image_paths: 이미지 파일 경로 리스트
            prompt: 분석 프롬프트
        
        Returns:
            분석 결과 리스트
        """
        results = []
        
        for i, path in enumerate(image_paths, 1):
            if self.verbose:
                print(f"\n[{i}/{len(image_paths)}] 분석 중...")
            
            result = self.analyze_image(path, prompt)
            results.append(result)
        
        return results


def main():
    """메인 함수 - Vision 분석기 테스트"""
    print("Vision 분석기 테스트...\n")
    
    # 분석기 초기화
    analyzer = VisionAnalyzer(verbose=True)
    
    # 테스트 이미지 경로
    test_image = "./data/captures/test_model.png"
    
    # 이미지가 없으면 안내
    if not Path(test_image).exists():
        print(f"테스트 이미지가 없습니다: {test_image}")
        print("FreeCAD에서 모델을 만들고 이미지를 내보낸 후 다시 시도하세요.")
        return
    
    # 이미지 분석
    result = analyzer.analyze_image(test_image)
    
    if result["success"]:
        print(f"\n{'='*60}")
        print("분석 결과:")
        print(f"{'='*60}")
        print(result["analysis"])
        print(f"{'='*60}\n")
    else:
        print(f"\n분석 실패: {result['error']}\n")


if __name__ == "__main__":
    main()

