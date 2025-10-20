from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.tools.freecad_box import FreeCADCreateBoxTool


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
@pytest.mark.integration
async def test_freecad_create_box_integration(tmp_path: Path) -> None:
    command = os.getenv("FREECAD_CMD")
    if not command or not Path(command).is_file():
        pytest.skip("FREECAD_CMD is not configured or missing")

    output_path = tmp_path / "integration_box.FCStd"
    tool = FreeCADCreateBoxTool()
    result = await tool.invoke(
        length=10.0,
        width=5.0,
        height=3.0,
        doc_name="IntegrationBox",
        output_path=str(output_path),
    )

    assert result["executed"] is True
    assert result["returncode"] == 0
    saved = result["saved_path"]
    assert saved
    assert Path(saved).is_file()
    assert Path(result["command"]).is_file()
