"""
Lightweight OCX XML validator for automated self-checks.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Dict, List


class XMLValidator:
    def validate(self, xml_content: str) -> Dict[str, object]:
        issues: List[str] = []
        stats = {"panels": 0, "stiffeners": 0, "holes": 0}

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as exc:
            return {"ok": False, "issues": [f"XML parse error: {exc}"], "stats": stats}

        if root.tag != "OCX":
            issues.append("Root tag must be <OCX>")
        version = root.get("version")
        if not version:
            issues.append("Missing OCX version attribute")

        structure = root.find(".//Structure")
        if structure is None:
            issues.append("Missing <Structure> node")
            return {"ok": False, "issues": issues, "stats": stats}

        for panel in structure.findall("Panel"):
            stats["panels"] += 1
            geom = panel.find("Geometry")
            points = geom.findall("Point") if geom is not None else []
            if len(points) < 4:
                issues.append(f"Panel {panel.get('name','<unnamed>')} has fewer than 4 points")
            material = panel.find("Material")
            if material is None:
                issues.append(f"Panel {panel.get('name','<unnamed>')} missing <Material>")
            for stiffener in panel.findall("Stiffener"):
                stats["stiffeners"] += 1
                location = stiffener.find("Location")
                if location is None:
                    issues.append(f"Stiffener {stiffener.get('name','<unnamed>')} missing <Location>")
            for hole in panel.findall("Hole"):
                stats["holes"] += 1
                params = hole.find("Parameters")
                position = hole.find("Position")
                if params is None or position is None:
                    issues.append(f"Hole {hole.get('name','<unnamed>')} missing Parameters or Position")

        if stats["panels"] == 0:
            issues.append("No panels defined in Structure")

        return {"ok": len(issues) == 0, "issues": issues, "stats": stats}
