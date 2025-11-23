import os
import base64
from typing import Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class VLMValidator:
    """
    Vision Language Model validator using OpenAI GPT-4 Vision or LLaVA.
    Validates generated 3D models against user requirements.
    """
    
    def __init__(self, model: str = None):
        # 환경 변수에서 VLM 모델 지정 가능 (기본값: gpt-4o)
        self.model = model or os.getenv("VLM_VALIDATION_MODEL", "gpt-4o")
        
        # LLaVA 등 로컬 모델 사용 시 LiteLLM 프록시 사용
        base_url = os.getenv("LITELLM_BASE_URL")
        api_key = os.getenv("LITELLM_API_KEY")
        
        if self.model == "llava" or (base_url and "localhost" in base_url):
            # 로컬 모델 사용 시
            base_url = base_url or "http://localhost:4000"
            api_key = api_key or "sk-1234"
            self.client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            # OpenAI 모델 사용 시
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def validate(self, user_request: str, image_path: str, xml_content: str) -> Dict:
        """
        Validate the generated 3D model against user request.
        
        Args:
            user_request: Original user's natural language request
            image_path: Path to the rendered PNG image
            xml_content: Generated OCX XML content
            
        Returns:
            Dictionary containing validation results
        """
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": "Image file not found"
            }
        
        base64_image = self._encode_image(image_path)
        
        validation_prompt = f"""You are a CAD validation expert. Analyze this 3D model rendering.

**User Request**: "{user_request}"

**Generated OCX XML Summary**:
- Analyze the structure based on the visual representation

**Validation Tasks**:
1. Does the rendered 3D model match the user's request?
2. Are the dimensions and proportions reasonable?
3. Is the structure type correct (deck, bulkhead, shell, etc.)?
4. Are there any obvious errors or missing elements?

Provide your response in JSON format:
{{
    "matches_request": true/false,
    "confidence_score": 0.0-1.0,
    "issues": ["list of issues found"],
    "suggestions": ["list of improvement suggestions"],
    "summary": "brief validation summary"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": validation_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            validation_text = response.choices[0].message.content
            
            # Try to parse JSON from response
            import json
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in validation_text:
                    json_str = validation_text.split("```json")[1].split("```")[0].strip()
                elif "```" in validation_text:
                    json_str = validation_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = validation_text
                    
                validation_result = json.loads(json_str)
                validation_result["success"] = True
                validation_result["raw_response"] = validation_text
                return validation_result
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw text
                return {
                    "success": True,
                    "matches_request": None,
                    "confidence_score": 0.0,
                    "summary": validation_text,
                    "issues": [],
                    "suggestions": [],
                    "raw_response": validation_text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
