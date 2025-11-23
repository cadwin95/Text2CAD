"""
FreeCAD MCP 서버
FastMCP를 사용한 FreeCAD tool calling 서버
"""

from .server import mcp, run_server

__all__ = ["mcp", "run_server"]

