from __future__ import annotations

from app.schemas import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    ChatMessage,
    SingleTurnRequest,
)


def test_single_turn_request_defaults() -> None:
    request = SingleTurnRequest()
    messages = request.to_messages()
    assert messages[0] == ChatMessage(role="system", content=DEFAULT_SYSTEM_PROMPT)
    assert messages[1] == ChatMessage(role="user", content=DEFAULT_USER_PROMPT)


def test_single_turn_request_override() -> None:
    request = SingleTurnRequest(system_prompt="sys", user_prompt="user")
    messages = request.to_messages()
    assert messages[0].content == "sys"
    assert messages[1].content == "user"
