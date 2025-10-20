"""Tool registry for CAD actions."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CADTool(Protocol):
    """Protocol for FreeCAD-backed tool implementations."""

    name: str

    async def invoke(self, **kwargs) -> dict:  # pragma: no cover - interface only
        """Execute the tool with keyword arguments."""
        raise NotImplementedError


REGISTRY: dict[str, CADTool] = {}


def register(tool: CADTool) -> None:
    """Register a CAD tool implementation by name."""

    REGISTRY[tool.name] = tool


# Ensure default tools register on import
try:
    from . import freecad_stub  # noqa: F401
except ImportError:  # pragma: no cover
    pass

try:
    from . import freecad_box  # noqa: F401
except ImportError:  # pragma: no cover
    pass
