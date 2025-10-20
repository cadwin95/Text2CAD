from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from ..config import load_litellm_config
from ..llm import get_async_client
from ..schemas import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    ChatMessage,
    SingleTurnRequest,
    ToolCall,
)
from .transcript import Transcript

if TYPE_CHECKING:  # pragma: no cover - 타입 체크용
    from ..tools import CADTool


@dataclass(slots=True)
class AgentRuntime:
    """Coordinates the lifecycle of a single CAD conversation."""

    model: str
    transcript_path: Optional[str] = None
    request_timeout: float = 30.0
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    user_prompt: str = DEFAULT_USER_PROMPT
    tool_registry: dict[str, "CADTool"] | None = None

    async def run(self) -> None:
        """Kick off the agent loop."""

        registry = self._initialize_tools()
        config = load_litellm_config()
        model_entry = config.get_model(self.model)
        transcript = Transcript()
        request = SingleTurnRequest(
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
        )
        bootstrap = request.to_messages()
        transcript.extend(bootstrap)

        client = get_async_client()
        response = await client.chat.completions.create(
            model=model_entry.model_name,
            messages=[msg.model_dump() for msg in bootstrap],
            timeout=self.request_timeout,
            extra_body=model_entry.litellm_params.to_litellm_kwargs(),
        )
        content = response.choices[0].message.content or ""
        assistant_message = ChatMessage(role="assistant", content=content)
        transcript.add(assistant_message)

        tool_call = self._parse_tool_call(content)
        if tool_call:
            tool_message = await self._execute_tool(tool_call, registry)
            transcript.add(tool_message)

        await self._emit_transcript(transcript)

    def _initialize_tools(self) -> dict[str, "CADTool"]:
        if self.tool_registry is not None:
            return self.tool_registry
        from .. import tools

        self.tool_registry = tools.REGISTRY
        return self.tool_registry

    async def _emit_transcript(self, transcript: Transcript) -> None:
        if self.transcript_path:
            target = Path(self.transcript_path)
            transcript.write(target)
        else:
            for entry in transcript.messages:
                print(f"[{entry.role}] {entry.content}")
        await asyncio.sleep(0)

    def _parse_tool_call(self, content: str) -> ToolCall | None:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return None

        if not isinstance(payload, dict):
            return None

        tool_name = payload.get("tool") or payload.get("name")
        arguments = payload.get("arguments") or payload.get("args")
        if not tool_name or not isinstance(arguments, dict):
            return None

        return ToolCall(name=str(tool_name), arguments=arguments)

    async def _execute_tool(
        self,
        call: ToolCall,
        registry: dict[str, "CADTool"],
    ) -> ChatMessage:
        tool = registry.get(call.name)
        if tool is None:
            return ChatMessage(
                role="tool",
                content=json.dumps(
                    {
                        "tool": call.name,
                        "status": "error",
                        "message": "Tool not found",
                    },
                    ensure_ascii=False,
                ),
            )

        result = await tool.invoke(**call.arguments)
        return ChatMessage(
            role="tool",
            content=json.dumps(
                {
                    "tool": call.name,
                    "status": "ok",
                    "result": result,
                },
                ensure_ascii=False,
            ),
        )
