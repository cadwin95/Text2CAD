"""Pydantic schemas for agent IO."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .freecad import CreateBoxParams, CreateBoxResult

DEFAULT_SYSTEM_PROMPT = (
    "You are the OmniSQL Tools Agent verifying startup. "
    "Respond concisely and confirm readiness."
)
DEFAULT_USER_PROMPT = (
    "Reply with a short acknowledgement that you are ready to perform CAD automation tasks."
)


class ChatMessage(BaseModel):
    """단일 메시지를 표현하는 기본 구조."""

    role: str = Field(..., description="메시지를 보낸 주체 (system/user/assistant 등)")
    content: str = Field(..., description="메시지 내용")


class SingleTurnRequest(BaseModel):
    """단일 턴 대화를 위한 시스템/사용자 프롬프트 설정."""

    system_prompt: str = Field(
        default=DEFAULT_SYSTEM_PROMPT,
        description="LLM에게 부여할 시스템 지침",
    )
    user_prompt: str = Field(
        default=DEFAULT_USER_PROMPT,
        description="사용자 입력 프롬프트",
    )

    def to_messages(self) -> list[ChatMessage]:
        """Chat Completions 포맷에 맞는 메시지 리스트 반환."""

        return [
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=self.user_prompt),
        ]


class ToolCall(BaseModel):
    """Schema describing a tool invocation from the agent."""

    name: str = Field(..., description="Registered tool name")
    arguments: dict = Field(default_factory=dict, description="Tool parameters")


__all__ = [
    "CreateBoxParams",
    "CreateBoxResult",
    "ChatMessage",
    "SingleTurnRequest",
    "ToolCall",
    "DEFAULT_SYSTEM_PROMPT",
    "DEFAULT_USER_PROMPT",
]
