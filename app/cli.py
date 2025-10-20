from __future__ import annotations

import asyncio
from typing import Optional

import typer

from .agent.runtime import AgentRuntime
from .schemas import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT

app = typer.Typer(add_completion=False)


TOOL_DEMO_SYSTEM_PROMPT = (
    "당신은 FreeCAD 자동화 에이전트다. 항상 하나의 JSON 객체만 반환하고, "
    "필드는 tool (문자열)과 arguments (객체)만 포함해야 한다."
)
TOOL_DEMO_USER_PROMPT = (
    "길이 10, 폭 5, 높이 3인 박스를 위해 freecad.create_box 툴을 호출할 JSON을 생성해줘."
)
DEFAULT_MODEL = "openai/gpt-4o-mini"
LOCAL_MODEL = "openai/llama.cpp"


@app.command()
def run(
    model: str = typer.Option(
        DEFAULT_MODEL,
        help="LiteLLM 프록시에 등록된 모델 식별자",
    ),
    prompt: str = typer.Option(
        DEFAULT_USER_PROMPT,
        "--prompt",
        "-p",
        help="단일 턴 사용자 프롬프트",
    ),
    system_prompt: str = typer.Option(
        DEFAULT_SYSTEM_PROMPT,
        "--system-prompt",
        "-s",
        help="LLM에 전달할 시스템 지침",
    ),
    transcript_path: Optional[str] = typer.Option(
        None,
        help="대화 로그를 저장할 경로",
    ),
    timeout: float = typer.Option(
        30.0,
        help="LiteLLM 요청 타임아웃(초)",
    ),
    demo_tool: bool = typer.Option(
        False,
        "--demo-freecad",
        help="FreeCAD 박스 생성 툴 호출용 데모 프롬프트 사용",
    ),
    use_local: bool = typer.Option(
        False,
        "--local",
        help="로컬 llama.cpp 모델(openai/llama.cpp)을 사용",
    ),
) -> None:
    """LiteLLM Proxy를 거쳐 단일 턴 Chat Completion을 실행."""

    if demo_tool:
        system_prompt = TOOL_DEMO_SYSTEM_PROMPT
        prompt = TOOL_DEMO_USER_PROMPT

    selected_model = LOCAL_MODEL if use_local else model

    runtime = AgentRuntime(
        model=selected_model,
        transcript_path=transcript_path,
        request_timeout=timeout,
        system_prompt=system_prompt,
        user_prompt=prompt,
    )
    asyncio.run(runtime.run())


if __name__ == "__main__":  # pragma: no cover
    app()
