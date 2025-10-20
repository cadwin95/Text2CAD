from __future__ import annotations

import asyncio
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import subprocess

from ..schemas import CreateBoxParams, CreateBoxResult
from ..utils.env import load_env
from . import CADTool, register


def _render_box_script(params: CreateBoxParams, saved_path: Optional[Path]) -> str:
    doc_name = params.doc_name.replace("\"", "_")
    save_stmt = ""
    if saved_path:
        save_stmt = f"doc.saveAs(r\"{saved_path.as_posix()}\")"
    lines = [
        "import FreeCAD",
        "import Part",
        f'doc = FreeCAD.newDocument("{doc_name}")',
        'box = doc.addObject("Part::Box", "Box")',
        f"box.Length = {params.length}",
        f"box.Width = {params.width}",
        f"box.Height = {params.height}",
        "doc.recompute()",
    ]
    if save_stmt:
        lines.append(save_stmt)
    lines.append("FreeCAD.closeDocument(doc.Name)")
    return "\n".join(lines) + "\n"


async def _run_freecad(command: Path, script: str) -> tuple[int, str, str]:
    loop = asyncio.get_running_loop()
    temp_dir = Path(tempfile.mkdtemp())
    script_path = temp_dir / "create_box.py"
    script_path.write_text(script, encoding="utf-8")

    def _run() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(command), str(script_path)],
            check=False,
            capture_output=True,
            text=True,
        )

    result: subprocess.CompletedProcess[str] = await loop.run_in_executor(None, _run)
    return result.returncode, result.stdout or "", result.stderr or ""


def _resolve_command(override: Optional[str]) -> Optional[Path]:
    load_env()
    raw = (override or os.getenv("FREECAD_CMD", "")).strip()
    if not raw:
        return None
    command = Path(raw).expanduser()
    if command.is_file():
        return command
    return None


@dataclass(slots=True)
class FreeCADCreateBoxTool(CADTool):
    name: str = "freecad.create_box"

    async def invoke(self, **kwargs) -> dict[str, object]:
        command_override = kwargs.pop("command", None)
        params = CreateBoxParams(**kwargs)
        saved_path = Path(params.output_path).expanduser() if params.output_path else None
        script = _render_box_script(params, saved_path)
        command_path = _resolve_command(command_override)

        executed = False
        returncode: int | None = None
        stdout = ""
        stderr = ""

        if command_path:
            returncode, stdout, stderr = await _run_freecad(command_path, script)
            executed = True

        result = CreateBoxResult(
            command=str(command_path or ""),
            script=script,
            executed=executed,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            saved_path=str(saved_path) if saved_path else None,
        )
        return result.model_dump()


BOX_TOOL = FreeCADCreateBoxTool()
register(BOX_TOOL)

__all__ = ["BOX_TOOL", "FreeCADCreateBoxTool"]
