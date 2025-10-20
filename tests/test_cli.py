from __future__ import annotations

import pytest
from typer.testing import CliRunner

from app.cli import LOCAL_MODEL, app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "LiteLLM Proxy를 거쳐 단일 턴 Chat Completion을 실행." in result.output


def test_cli_run_invocation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class DummyRuntime:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        async def run(self) -> None:  # pragma: no cover - 호출만 검증
            return None

    monkeypatch.setattr("app.cli.AgentRuntime", DummyRuntime)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "--model",
            "openai/gpt-4o-mini",
            "--prompt",
            "hello",
            "--system-prompt",
            "sys",
            "--timeout",
            "5.5",
            "--transcript-path",
            "tmp/out.txt",
            "--local",
        ],
    )

    assert result.exit_code == 0
    assert captured["model"] == LOCAL_MODEL
    assert captured["user_prompt"] == "hello"
    assert captured["system_prompt"] == "sys"
    assert captured["request_timeout"] == 5.5
    assert captured["transcript_path"] == "tmp/out.txt"
