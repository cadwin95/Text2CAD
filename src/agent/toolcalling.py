"""
FreeCAD Tool Calling Agent
OpenAI SDK를 사용하여 LiteLLM proxy를 통해 도구를 호출합니다.
"""

import os
import json
from typing import List, Dict, Optional, Callable
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
from ..freecad_tools import (
    create_box,
    create_cylinder,
    create_sphere,
    create_cone,
    new_document,
    save_document,
    get_active_document,
    export_image
)


class ToolCallingAgent:
    """FreeCAD Tool Calling Agent"""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        model: str = "llama.cpp",
        verbose: bool = True
    ):
        """
        Agent 초기화
        
        Args:
            base_url: LiteLLM proxy URL
            api_key: API 키
            model: 사용할 모델 이름
            verbose: 상세 출력 여부
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 패키지가 필요합니다: uv add openai")
        
        self.base_url = base_url or os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        self.api_key = api_key or os.getenv("LITELLM_API_KEY", "sk-1234")
        self.model = model
        self.verbose = verbose
        
        # OpenAI 클라이언트 초기화
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # FreeCAD 도구 로드
        self.tools = get_tools_for_openai()
        
        # finish 도구 추가
        self._add_finish_tool()
        
        # 도구 함수 매핑
        self.tool_functions = {
            "freecad_create_box": create_box,
            "freecad_create_cylinder": create_cylinder,
            "freecad_create_sphere": create_sphere,
            "freecad_create_cone": create_cone,
            "freecad_new_document": new_document,
            "freecad_save_document": save_document,
            "freecad_get_document_info": get_active_document,
            "freecad_export_image": export_image,
            "finish": self._finish_task,
        }
        
        # 대화 히스토리
        self.messages = []
        
        # 초기화 정보 출력
        if self.verbose:
            print("="*60)
            print("🤖 FreeCAD Tool Calling Agent 초기화")
            print("="*60)
            print(f"  📡 LiteLLM Proxy: {self.base_url}")
            print(f"  🧠 모델: {self.model}")
            print(f"  🔧 도구 개수: {len(self.tools)}개")
            print("="*60)
            print()
    
    def _add_finish_tool(self):
        """finish 도구를 도구 목록에 추가"""
        finish_tool = {
            "type": "function",
            "function": {
                "name": "finish",
                "description": "작업이 완료되었을 때 호출합니다. 최종 결과나 요약을 제공합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "완료된 작업의 요약 또는 최종 답변"
                        }
                    },
                    "required": ["summary"]
                }
            }
        }
        self.tools.append(finish_tool)
    
    def _finish_task(self, summary: str) -> Dict:
        """작업 완료 처리"""
        return {
            "success": True,
            "finished": True,
            "summary": summary
        }
    
    def run(
        self,
        user_message: str,
        max_iterations: int = 16,
        image_context: Optional[str] = None
    ) -> Dict:
        """
        사용자 메시지를 처리하고 도구를 호출합니다.
        
        Args:
            user_message: 사용자 메시지
            max_iterations: 최대 반복 횟수 (기본값: 16)
            image_context: 이미지 분석 결과 (vision 모듈에서 제공)
        
        Returns:
            실행 결과
        """
        # 이미지 컨텍스트 추가
        if image_context:
            user_message = f"{user_message}\n\n[이미지 분석 결과]\n{image_context}"
        
        # 메시지 추가
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"사용자: {user_message}")
            print(f"{'='*60}")
            print(f"🧠 사용 모델: {self.model}")
            print(f"{'='*60}\n")
        
        # 반복적으로 도구 호출
        for iteration in range(max_iterations):
            if self.verbose:
                print(f"[반복 {iteration + 1}/{max_iterations}] 🧠 모델: {self.model}")
            
            # LLM 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                temperature=0.1
            )
            
            assistant_message = response.choices[0].message
            
            # 어시스턴트 메시지 추가
            self.messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (assistant_message.tool_calls or [])
                ]
            })
            
            # Tool calls 확인
            if not assistant_message.tool_calls:
                # 도구 호출이 없으면 경고 (모델이 finish를 호출해야 함)
                if self.verbose:
                    print(f"  ⚠ 경고: 도구 호출 없이 응답함")
                    print(f"  어시스턴트: {assistant_message.content}")
                
                return {
                    "success": True,
                    "message": assistant_message.content or "작업 완료 (도구 호출 없음)",
                    "iterations": iteration + 1,
                    "tool_calls_count": 0,
                    "warning": "모델이 finish 도구를 호출하지 않았습니다"
                }
            
            # 도구 호출 실행
            tool_results = []
            task_finished = False
            final_summary = None
            
            for tool_call in assistant_message.tool_calls:
                result = self._execute_tool_call(tool_call)
                tool_results.append(result)
                
                # finish 도구가 호출되었는지 확인
                if tool_call.function.name == "finish":
                    task_finished = True
                    final_summary = result.get("summary", "작업 완료")
                
                # 도구 결과를 메시지에 추가
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # finish 도구가 호출되면 종료
            if task_finished:
                if self.verbose:
                    print(f"  ✓ 작업 완료: {final_summary}")
                
                return {
                    "success": True,
                    "message": final_summary,
                    "iterations": iteration + 1,
                    "tool_calls_count": len(tool_results),
                    "tool_results": tool_results,
                    "finished": True
                }
            
            # 마지막 반복이면 결과 반환
            if iteration == max_iterations - 1:
                return {
                    "success": True,
                    "message": "최대 반복 횟수에 도달했습니다.",
                    "iterations": max_iterations,
                    "tool_calls_count": len(tool_results),
                    "tool_results": tool_results,
                    "warning": "최대 반복 횟수 도달 - finish 도구가 호출되지 않음"
                }
        
        return {
            "success": False,
            "message": "예상치 못한 종료"
        }
    
    def _execute_tool_call(self, tool_call) -> Dict:
        """
        도구 호출 실행
        
        Args:
            tool_call: OpenAI tool call 객체
        
        Returns:
            도구 실행 결과
        """
        func_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        if self.verbose:
            print(f"  → 도구 호출: {func_name}")
            print(f"    파라미터: {arguments}")
        
        # 도구 함수 실행
        if func_name in self.tool_functions:
            func = self.tool_functions[func_name]
            try:
                result = func(**arguments)
                if self.verbose:
                    print(f"    결과: {result}")
                return result
            except Exception as e:
                error_result = {"success": False, "error": str(e)}
                if self.verbose:
                    print(f"    오류: {e}")
                return error_result
        else:
            error_result = {"success": False, "error": f"알 수 없는 도구: {func_name}"}
            if self.verbose:
                print(f"    오류: 알 수 없는 도구")
            return error_result
    
    def reset(self):
        """대화 히스토리 초기화"""
        self.messages = []
        if self.verbose:
            print("대화 히스토리가 초기화되었습니다.")


def main():
    """메인 함수 - Agent 테스트"""
    print("FreeCAD Tool Calling Agent 시작...\n")
    
    # Agent 초기화
    agent = ToolCallingAgent(verbose=True)
    
    # 테스트 명령
    test_commands = [
        "10mm x 10mm x 10mm 크기의 박스를 만들어줘",
        "반지름 5mm, 높이 20mm인 실린더를 생성해",
        "현재 문서 정보를 알려줘",
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{'#'*60}")
        print(f"테스트 {i}/{len(test_commands)}")
        print(f"{'#'*60}")
        
        result = agent.run(cmd)
        
        print(f"\n결과:")
        print(f"  - 성공: {result['success']}")
        print(f"  - 반복: {result['iterations']}")
        print(f"  - 메시지: {result['message']}")
        
        # 다음 테스트를 위해 히스토리 초기화
        agent.reset()
    
    print(f"\n{'='*60}")
    print("모든 테스트 완료!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

