import os
from typing import Any, Dict, List, Optional

from src.agent.code_executor import OcxCodeExecutor
from src.agent.ocx_code_agent import OCXCodeAgent
from src.agent.xml_validator import XMLValidator


class GenerativeDesignCoordinator:
    """
    Instruction -> Code -> Execution -> Validation pipeline.
    """

    def __init__(self, model: str = None, max_attempts: int = 2):
        # 환경 변수에서 코드 생성 모델 지정 가능 (기본값: gpt-4o)
        code_model = model or os.getenv("CODE_GENERATION_MODEL", "gpt-4o")
        self.codegen = OCXCodeAgent(model=code_model)
        self.executor = OcxCodeExecutor()
        self.validator = XMLValidator()
        self.max_attempts = max_attempts

    def run(
        self,
        user_prompt: str,
        history: Optional[List[Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        feedback: Optional[str] = None
        attempts: List[Dict[str, Any]] = []

        for attempt in range(self.max_attempts):
            code = self.codegen.generate_code(
                user_prompt=user_prompt,
                history=self._normalize_history(history),
                context=context,
                feedback=feedback,
            )

            exec_result = self.executor.run(code)
            attempt_record: Dict[str, Any] = {"code": code, "execution": exec_result}

            if not exec_result.get("success"):
                feedback = f"Execution failed: {exec_result.get('error')}"
                attempts.append(attempt_record)
                continue

            xml_content = exec_result.get("xml_content", "")
            validation = self.validator.validate(xml_content)
            attempt_record["validation"] = validation

            if validation.get("ok"):
                attempts.append(attempt_record)
                return {
                    "success": True,
                    "xml_content": xml_content,
                    "code": code,
                    "attempts": attempts,
                    "xml_validation": validation,
                }

            feedback = "XML validation issues: " + "; ".join(validation.get("issues", []))
            attempts.append(attempt_record)

        return {
            "success": False,
            "error": feedback or "Unknown failure in generative design pipeline",
            "attempts": attempts,
        }

    def _normalize_history(self, history: Optional[List[Any]]) -> Optional[List[Dict[str, str]]]:
        if not history:
            return None
        normalized: List[Dict[str, str]] = []
        for msg in history:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
            else:
                role = getattr(msg, "role", None)
                content = getattr(msg, "content", None)
            if role in {"user", "assistant"} and content:
                normalized.append({"role": role, "content": content})
        return normalized or None
