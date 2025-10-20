from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ..utils.env import load_env
from . import CADTool, register


@dataclass(slots=True)
class FreeCADStatusTool(CADTool):
    """Reports whether the FreeCAD command-line binary is available."""

    name: str = "freecad.status"

    async def invoke(self, **kwargs) -> dict[str, object]:
        load_env()
        override = kwargs.get("command")
        raw_value = (override or os.getenv("FREECAD_CMD", "")).strip()
        if not raw_value:
            return {
                "command": "",
                "ready": False,
                "hint": "Set FREECAD_CMD to the FreeCADCmd binary",
            }
        command = Path(raw_value).expanduser()
        exists = command.is_file()
        return {
            "command": str(command),
            "ready": exists,
            "hint": "" if exists else "Verify the path points to FreeCADCmd",
        }


STATUS_TOOL = FreeCADStatusTool()
register(STATUS_TOOL)

__all__ = ["STATUS_TOOL", "FreeCADStatusTool"]
