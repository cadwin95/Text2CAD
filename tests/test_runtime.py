from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.agent import runtime as agent_runtime
from app.agent.runtime import AgentRuntime
from app.config import LiteLLMConfig, ModelEntry, ModelParams, RouterConfig, RouterSection


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_runtime_single_turn(monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]) -> None:
    fake_choice = SimpleNamespace(message=SimpleNamespace(content='{"tool": "freecad.create_box", "arguments": {"length": 1, "width": 2, "height": 3}}'))
    fake_response = SimpleNamespace(choices=[fake_choice])
    captured_kwargs: dict[str, object] = {}
    tool_calls: list[dict[str, object]] = []

    async def fake_create(**kwargs):
        captured_kwargs.update(kwargs)
        return fake_response

    class DummyClient:
        def __init__(self) -> None:
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=fake_create))

    monkeypatch.setattr(agent_runtime, "get_async_client", lambda: DummyClient())

    config = LiteLLMConfig(
        model_list=[
            ModelEntry(
                model_name="test-model",
                litellm_params=ModelParams(model="gpt-test"),
            )
        ],
        router=RouterSection(config=RouterConfig(default_model="test-model")),
    )

    monkeypatch.setattr(agent_runtime, "load_litellm_config", lambda: config)

    class DummyTool:
        name = "freecad.create_box"

        async def invoke(self, **kwargs):
            tool_calls.append(kwargs)
            return {"created": True}

    runtime = AgentRuntime(
        model="test-model",
        system_prompt="system message",
        user_prompt="user message",
        request_timeout=12.5,
    )
    runtime.tool_registry = {"freecad.create_box": DummyTool()}

    await runtime.run()

    assert captured_kwargs["model"] == "test-model"
    messages = captured_kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "system message"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "user message"
    assert captured_kwargs["timeout"] == 12.5

    assert tool_calls == [{"length": 1, "width": 2, "height": 3}]

    captured = capfd.readouterr()
    assert "[assistant]" in captured.out
    assert "freecad.create_box" in captured.out
    assert '"status": "ok"' in captured.out
