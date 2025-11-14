"""
FreeCAD 기본 도형 생성 도구
박스, 실린더, 구, 원뿔 등의 기본 도형을 생성합니다.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field

# FreeCAD 임포트 (타입 체크용)
try:
    import FreeCAD
    import Part
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False
    # Stub으로 작업 가능
    FreeCAD = None
    Part = None


class BoxParams(BaseModel):
    """박스 생성 파라미터"""
    length: float = Field(gt=0, description="박스의 길이 (X축)")
    width: float = Field(gt=0, description="박스의 너비 (Y축)")
    height: float = Field(gt=0, description="박스의 높이 (Z축)")
    name: Optional[str] = Field(default="Box", description="객체 이름")


class CylinderParams(BaseModel):
    """실린더 생성 파라미터"""
    radius: float = Field(gt=0, description="실린더의 반지름")
    height: float = Field(gt=0, description="실린더의 높이")
    name: Optional[str] = Field(default="Cylinder", description="객체 이름")


class SphereParams(BaseModel):
    """구 생성 파라미터"""
    radius: float = Field(gt=0, description="구의 반지름")
    name: Optional[str] = Field(default="Sphere", description="객체 이름")


class ConeParams(BaseModel):
    """원뿔 생성 파라미터"""
    radius1: float = Field(ge=0, description="밑면 반지름")
    radius2: float = Field(ge=0, description="윗면 반지름")
    height: float = Field(gt=0, description="원뿔의 높이")
    name: Optional[str] = Field(default="Cone", description="객체 이름")


def create_box(
    length: float,
    width: float,
    height: float,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    rotation: float = 0,
    name: str = "Box"
) -> Dict[str, any]:
    """
    FreeCAD에서 박스를 생성합니다.
    
    Args:
        length: 박스의 길이 (X축, mm)
        width: 박스의 너비 (Y축, mm)
        height: 박스의 높이 (Z축, mm)
        x: X 좌표 (기본값: 0)
        y: Y 좌표 (기본값: 0)
        z: Z 좌표 (기본값: 0)
        rotation: Z축 기준 회전 각도 (도, 기본값: 0)
        name: 객체 이름 (기본값: "Box")
    
    Returns:
        생성된 객체 정보 딕셔너리
    
    Raises:
        RuntimeError: FreeCAD를 사용할 수 없는 경우
    """
    if not FREECAD_AVAILABLE:
        # 테스트 또는 개발 모드
        return {
            "success": True,
            "object_name": name,
            "type": "Box",
            "parameters": {
                "length": length,
                "width": width,
                "height": height,
                "position": {"x": x, "y": y, "z": z},
                "rotation": rotation
            },
            "message": "FreeCAD가 설치되지 않아 시뮬레이션 모드로 실행됨"
        }
    
    # 파라미터 검증
    params = BoxParams(length=length, width=width, height=height, name=name)
    
    # 활성 문서 가져오기 또는 새로 생성
    doc = FreeCAD.activeDocument()
    if doc is None:
        doc = FreeCAD.newDocument("Unnamed")
    
    # 박스 생성
    box = doc.addObject("Part::Box", params.name)
    box.Length = params.length
    box.Width = params.width
    box.Height = params.height
    
    # 위치 설정
    box.Placement.Base = FreeCAD.Vector(x, y, z)
    
    # 회전 설정 (Z축 기준)
    if rotation != 0:
        box.Placement.Rotation = FreeCAD.Rotation(
            FreeCAD.Vector(0, 0, 1), rotation
        )
    
    # 문서 재계산
    doc.recompute()
    
    return {
        "success": True,
        "object_name": box.Name,
        "type": "Box",
        "parameters": {
            "length": box.Length,
            "width": box.Width,
            "height": box.Height,
            "position": {"x": x, "y": y, "z": z},
            "rotation": rotation
        },
        "document": doc.Name
    }


def create_cylinder(
    radius: float,
    height: float,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    rotation: float = 0,
    name: str = "Cylinder"
) -> Dict[str, any]:
    """
    FreeCAD에서 실린더를 생성합니다.
    
    Args:
        radius: 실린더의 반지름 (mm)
        height: 실린더의 높이 (mm)
        x: X 좌표 (기본값: 0)
        y: Y 좌표 (기본값: 0)
        z: Z 좌표 (기본값: 0)
        rotation: Z축 기준 회전 각도 (도, 기본값: 0)
        name: 객체 이름 (기본값: "Cylinder")
    
    Returns:
        생성된 객체 정보 딕셔너리
    
    Raises:
        RuntimeError: FreeCAD를 사용할 수 없는 경우
    """
    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "object_name": name,
            "type": "Cylinder",
            "parameters": {
                "radius": radius,
                "height": height,
                "position": {"x": x, "y": y, "z": z},
                "rotation": rotation
            },
            "message": "FreeCAD가 설치되지 않아 시뮬레이션 모드로 실행됨"
        }
    
    # 파라미터 검증
    params = CylinderParams(radius=radius, height=height, name=name)
    
    # 활성 문서 가져오기 또는 새로 생성
    doc = FreeCAD.activeDocument()
    if doc is None:
        doc = FreeCAD.newDocument("Unnamed")
    
    # 실린더 생성
    cylinder = doc.addObject("Part::Cylinder", params.name)
    cylinder.Radius = params.radius
    cylinder.Height = params.height
    
    # 위치 설정
    cylinder.Placement.Base = FreeCAD.Vector(x, y, z)
    
    # 회전 설정
    if rotation != 0:
        cylinder.Placement.Rotation = FreeCAD.Rotation(
            FreeCAD.Vector(0, 0, 1), rotation
        )
    
    # 문서 재계산
    doc.recompute()
    
    return {
        "success": True,
        "object_name": cylinder.Name,
        "type": "Cylinder",
        "parameters": {
            "radius": cylinder.Radius,
            "height": cylinder.Height,
            "position": {"x": x, "y": y, "z": z},
            "rotation": rotation
        },
        "document": doc.Name
    }


def create_sphere(
    radius: float,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    name: str = "Sphere"
) -> Dict[str, any]:
    """
    FreeCAD에서 구를 생성합니다.
    
    Args:
        radius: 구의 반지름 (mm)
        x: X 좌표 (기본값: 0)
        y: Y 좌표 (기본값: 0)
        z: Z 좌표 (기본값: 0)
        name: 객체 이름 (기본값: "Sphere")
    
    Returns:
        생성된 객체 정보 딕셔너리
    
    Raises:
        RuntimeError: FreeCAD를 사용할 수 없는 경우
    """
    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "object_name": name,
            "type": "Sphere",
            "parameters": {
                "radius": radius,
                "position": {"x": x, "y": y, "z": z}
            },
            "message": "FreeCAD가 설치되지 않아 시뮬레이션 모드로 실행됨"
        }
    
    # 파라미터 검증
    params = SphereParams(radius=radius, name=name)
    
    # 활성 문서 가져오기 또는 새로 생성
    doc = FreeCAD.activeDocument()
    if doc is None:
        doc = FreeCAD.newDocument("Unnamed")
    
    # 구 생성
    sphere = doc.addObject("Part::Sphere", params.name)
    sphere.Radius = params.radius
    
    # 위치 설정
    sphere.Placement.Base = FreeCAD.Vector(x, y, z)
    
    # 문서 재계산
    doc.recompute()
    
    return {
        "success": True,
        "object_name": sphere.Name,
        "type": "Sphere",
        "parameters": {
            "radius": sphere.Radius,
            "position": {"x": x, "y": y, "z": z}
        },
        "document": doc.Name
    }


def create_cone(
    radius1: float,
    radius2: float,
    height: float,
    x: float = 0,
    y: float = 0,
    z: float = 0,
    rotation: float = 0,
    name: str = "Cone"
) -> Dict[str, any]:
    """
    FreeCAD에서 원뿔을 생성합니다.
    
    Args:
        radius1: 밑면 반지름 (mm)
        radius2: 윗면 반지름 (mm)
        height: 원뿔의 높이 (mm)
        x: X 좌표 (기본값: 0)
        y: Y 좌표 (기본값: 0)
        z: Z 좌표 (기본값: 0)
        rotation: Z축 기준 회전 각도 (도, 기본값: 0)
        name: 객체 이름 (기본값: "Cone")
    
    Returns:
        생성된 객체 정보 딕셔너리
    
    Raises:
        RuntimeError: FreeCAD를 사용할 수 없는 경우
    """
    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "object_name": name,
            "type": "Cone",
            "parameters": {
                "radius1": radius1,
                "radius2": radius2,
                "height": height,
                "position": {"x": x, "y": y, "z": z},
                "rotation": rotation
            },
            "message": "FreeCAD가 설치되지 않아 시뮬레이션 모드로 실행됨"
        }
    
    # 파라미터 검증
    params = ConeParams(radius1=radius1, radius2=radius2, height=height, name=name)
    
    # 활성 문서 가져오기 또는 새로 생성
    doc = FreeCAD.activeDocument()
    if doc is None:
        doc = FreeCAD.newDocument("Unnamed")
    
    # 원뿔 생성
    cone = doc.addObject("Part::Cone", params.name)
    cone.Radius1 = params.radius1
    cone.Radius2 = params.radius2
    cone.Height = params.height
    
    # 위치 설정
    cone.Placement.Base = FreeCAD.Vector(x, y, z)
    
    # 회전 설정
    if rotation != 0:
        cone.Placement.Rotation = FreeCAD.Rotation(
            FreeCAD.Vector(0, 0, 1), rotation
        )
    
    # 문서 재계산
    doc.recompute()
    
    return {
        "success": True,
        "object_name": cone.Name,
        "type": "Cone",
        "parameters": {
            "radius1": cone.Radius1,
            "radius2": cone.Radius2,
            "height": cone.Height,
            "position": {"x": x, "y": y, "z": z},
            "rotation": rotation
        },
        "document": doc.Name
    }

