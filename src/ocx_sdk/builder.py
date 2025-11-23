"""
OCXBuilder: Helper for programmatic OCX XML generation.

This hides low-level XML tag management so LLMs can focus on intent rather
than verbose markup. The builder tracks panels and geometry so higher-level
helpers (e.g., create_stiffeners_on_plate) can do the repetitive math.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET


def _indent(elem: ET.Element, level: int = 0) -> None:
    """
    Pretty-print helper for xml.etree so XML is readable when surfaced in the UI.
    """
    indent_str = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent_str + "  "
        for child in elem:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():  # type: ignore[name-defined]
            child.tail = indent_str  # type: ignore[name-defined]
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = indent_str


@dataclass
class PlateMetadata:
    name: str
    origin: Tuple[float, float, float]
    length: float
    width: float
    thickness: float


class OCXBuilder:
    def __init__(self, vessel_name: str = "DesignVessel", version: str = "3.0"):
        self.root = ET.Element("OCX", {"version": version})
        self.vessel = ET.SubElement(self.root, "Vessel", {"name": vessel_name})
        self.structure = ET.SubElement(self.vessel, "Structure")
        self.plates: Dict[str, PlateMetadata] = {}

    def create_plate(
        self,
        x: float,
        y: float,
        length: float,
        width: float,
        z: float = 0.0,
        thickness: float = 10.0,
        plate_type: str = "Deck",
        material: str = "AH36",
        name: Optional[str] = None,
    ) -> str:
        """
        Create a rectangular plate defined by origin (x, y, z), length (X), and width (Y).
        """
        plate_id = name or f"plt_{uuid.uuid4().hex[:8]}"
        panel_el = ET.SubElement(
            self.structure,
            "Panel",
            {"name": plate_id, "type": plate_type},
        )
        ET.SubElement(
            panel_el,
            "Material",
            {"grade": material, "thickness": str(thickness)},
        )
        geom_el = ET.SubElement(panel_el, "Geometry", {"type": "Plate"})

        points = [
            (x, y, z),
            (x + length, y, z),
            (x + length, y + width, z),
            (x, y + width, z),
        ]
        for px, py, pz in points:
            ET.SubElement(
                geom_el,
                "Point",
                {"x": f"{px:.2f}", "y": f"{py:.2f}", "z": f"{pz:.2f}"},
            )

        self.plates[plate_id] = PlateMetadata(
            name=plate_id, origin=(x, y, z), length=length, width=width, thickness=thickness
        )
        return plate_id

    def create_stiffener(
        self,
        name: Optional[str],
        start: Tuple[float, float, float],
        end: Tuple[float, float, float],
        profile: str = "Tee",
        height: float = 250.0,
        width: float = 12.0,
        web_thickness: float = 12.0,
        flange_thickness: float = 12.0,
        parent_panel: Optional[str] = None,
    ) -> str:
        stiffener_id = name or f"stf_{uuid.uuid4().hex[:8]}"
        parent_el = self._resolve_parent_panel(parent_panel)
        stiffener_el = ET.SubElement(
            parent_el,
            "Stiffener",
            {"name": stiffener_id, "type": profile},
        )
        ET.SubElement(
            stiffener_el,
            "Profile",
            {
                "height": f"{height:.2f}",
                "width": f"{width:.2f}",
                "web_thickness": f"{web_thickness:.2f}",
                "flange_thickness": f"{flange_thickness:.2f}",
            },
        )
        ET.SubElement(
            stiffener_el,
            "Location",
            {
                "start_x": f"{start[0]:.2f}",
                "start_y": f"{start[1]:.2f}",
                "start_z": f"{start[2]:.2f}",
                "end_x": f"{end[0]:.2f}",
                "end_y": f"{end[1]:.2f}",
                "end_z": f"{end[2]:.2f}",
            },
        )
        return stiffener_id

    def create_stiffeners_on_plate(
        self,
        plate_id: str,
        spacing: float,
        count: int,
        profile: str = "Tee",
        orientation: str = "y",
        name_prefix: str = "STF",
        height: float = 250.0,
        width: float = 12.0,
        web_thickness: float = 12.0,
        flange_thickness: float = 12.0,
    ) -> List[str]:
        """
        Populate evenly spaced stiffeners across a plate.

        orientation:
            "y" (default) stiffeners run along +Y (width), stepped along X (length)
            "x" stiffeners run along +X (length), stepped along Y (width)
        """
        if plate_id not in self.plates:
            raise ValueError(f"Plate '{plate_id}' not found for stiffeners")
        if orientation not in {"x", "y"}:
            raise ValueError("orientation must be 'x' or 'y'")

        plate = self.plates[plate_id]
        created: List[str] = []
        x0, y0, z0 = plate.origin

        for idx in range(count):
            if orientation == "y":
                offset = idx * spacing
                start = (x0 + offset, y0, z0)
                end = (x0 + offset, y0 + plate.width, z0)
            else:
                offset = idx * spacing
                start = (x0, y0 + offset, z0)
                end = (x0 + plate.length, y0 + offset, z0)

            stiffener_id = self.create_stiffener(
                name=f"{name_prefix}_{idx + 1}",
                start=start,
                end=end,
                profile=profile,
                height=height,
                width=width,
                web_thickness=web_thickness,
                flange_thickness=flange_thickness,
                parent_panel=plate_id,
            )
            created.append(stiffener_id)
        return created

    def add_opening(
        self,
        plate_id: str,
        center: Tuple[float, float, float],
        width: float,
        height: float,
        name: Optional[str] = None,
        opening_type: str = "Rectangular",
    ) -> str:
        """
        Add a rectangular/circular opening to a plate.
        """
        if plate_id not in self.plates:
            raise ValueError(f"Plate '{plate_id}' not found for opening")
        opening_id = name or f"hole_{uuid.uuid4().hex[:6]}"
        parent_el = self._resolve_parent_panel(plate_id)
        hole_el = ET.SubElement(
            parent_el,
            "Hole",
            {"name": opening_id, "type": opening_type},
        )
        ET.SubElement(
            hole_el,
            "Parameters",
            {"width": f"{width:.2f}", "height": f"{height:.2f}", "diameter": f"{width:.2f}"},
        )
        ET.SubElement(
            hole_el,
            "Position",
            {"x": f"{center[0]:.2f}", "y": f"{center[1]:.2f}", "z": f"{center[2]:.2f}"},
        )
        return opening_id

    def to_xml_string(self, pretty: bool = True) -> str:
        """
        Serialize the current OCX tree.
        """
        if pretty:
            _indent(self.root)
        return ET.tostring(self.root, encoding="unicode")

    def _resolve_parent_panel(self, plate_id: Optional[str]) -> ET.Element:
        if plate_id and plate_id in self.plates:
            for panel in self.structure.findall("Panel"):
                if panel.get("name") == plate_id:
                    return panel
        return self.structure
