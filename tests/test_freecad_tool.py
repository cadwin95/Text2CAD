from __future__ import annotations

from pathlib import Path

import pytest

from app.tools import freecad_box
from app.tools.freecad_box import FreeCADCreateBoxTool


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_freecad_box_without_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(freecad_box, "load_env", lambda: None)
    monkeypatch.delenv("FREECAD_CMD", raising=False)
    tool = FreeCADCreateBoxTool()
    result = await tool.invoke(length=10.0, width=5.0, height=3.0, doc_name=" Demo ")

    assert result["executed"] is False
    assert result["command"] == ""
    assert "import FreeCAD" in result["script"]
    assert result["saved_path"] is None


@pytest.mark.anyio
async def test_freecad_box_with_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake_cmd = tmp_path / "FreeCADCmd"
    fake_cmd.write_text("#!/bin/sh\n")

    async def fake_run(command: Path, script: str) -> tuple[int, str, str]:
        assert command == fake_cmd
        assert "box.Length = 1.0" in script
        return 0, "ok", ""

    monkeypatch.setattr(freecad_box, "load_env", lambda: None)
    monkeypatch.setattr(freecad_box, "_run_freecad", fake_run)

    tool = freecad_box.BOX_TOOL
    result = await tool.invoke(
        command=str(fake_cmd),
        length=1.0,
        width=2.0,
        height=3.0,
        output_path=str(tmp_path / "box.FCStd"),
    )

    assert result["executed"] is True
    assert result["returncode"] == 0
    assert result["stdout"] == "ok"
    assert result["command"] == str(fake_cmd)
    assert result["saved_path"].endswith("box.FCStd")
