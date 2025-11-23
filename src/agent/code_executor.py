"""
Executes LLM-generated Python snippets that build OCX XML via OCXBuilder.

Execution happens in a constrained globals namespace to prevent dangerous imports
while still letting the model use math and common builtins.
"""

from __future__ import annotations

import contextlib
import io
import math
import sys
import traceback
from pathlib import Path
from typing import Dict, Optional

from src.ocx_sdk import OCXBuilder


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    allowed = {"math", "random", "ocx_sdk"}
    root = name.split(".")[0]
    if root not in allowed:
        raise ImportError(f"Import of '{name}' is not allowed")
    return __import__(name, globals, locals, fromlist, level)


class OcxCodeExecutor:
    def __init__(self):
        self.safe_builtins = {
            "abs": abs,
            "enumerate": enumerate,
            "float": float,
            "int": int,
            "len": len,
            "max": max,
            "min": min,
            "print": print,
            "range": range,
            "round": round,
            "sum": sum,
            "__import__": _safe_import,
        }

    def run(self, code: str) -> Dict[str, object]:
        """
        Execute Python code that uses OCXBuilder and return XML + logs.
        """
        buffer = io.StringIO()
        # Ensure repo root and src are on path so `import ocx_sdk` works even when launched from backend/
        repo_root = Path(__file__).resolve().parents[2]
        src_dir = repo_root / "src"
        for p in [src_dir, repo_root]:
            p_str = str(p)
            if p_str not in sys.path:
                sys.path.insert(0, p_str)

        env = {
            "OCXBuilder": OCXBuilder,
            "builder": OCXBuilder(),
            "math": math,
        }

        try:
            with contextlib.redirect_stdout(buffer):
                exec(code, {"__builtins__": self.safe_builtins}, env)
        except Exception as exc:
            return {
                "success": False,
                "error": f"{exc}",
                "traceback": traceback.format_exc(),
                "stdout": buffer.getvalue(),
                "code": code,
            }

        xml_output: Optional[str] = None
        if isinstance(env.get("xml_output"), str):
            xml_output = env["xml_output"]  # type: ignore[index]
        elif isinstance(env.get("ocx_xml"), str):
            xml_output = env["ocx_xml"]  # type: ignore[index]
        elif isinstance(env.get("builder"), OCXBuilder):
            xml_output = env["builder"].to_xml_string()  # type: ignore[index]

        if not xml_output:
            return {
                "success": False,
                "error": "Execution completed but no XML was produced. Ensure you set xml_output = builder.to_xml_string().",
                "stdout": buffer.getvalue(),
                "code": code,
            }

        return {
            "success": True,
            "xml_content": xml_output,
            "stdout": buffer.getvalue(),
            "code": code,
        }
