"""
FreeCAD 도구 테스트
"""

import pytest
from src.freecad_tools import (
    create_box,
    create_cylinder,
    create_sphere,
    create_cone,
    new_document,
    get_active_document
)


def test_create_box():
    """박스 생성 테스트"""
    result = create_box(10, 10, 10, "TestBox")
    
    assert result["success"] is True
    assert result["object_name"] == "TestBox"
    assert result["type"] == "Box"
    assert result["parameters"]["length"] == 10
    assert result["parameters"]["width"] == 10
    assert result["parameters"]["height"] == 10


def test_create_cylinder():
    """실린더 생성 테스트"""
    result = create_cylinder(5, 20, "TestCylinder")
    
    assert result["success"] is True
    assert result["object_name"] == "TestCylinder"
    assert result["type"] == "Cylinder"
    assert result["parameters"]["radius"] == 5
    assert result["parameters"]["height"] == 20


def test_create_sphere():
    """구 생성 테스트"""
    result = create_sphere(7, "TestSphere")
    
    assert result["success"] is True
    assert result["object_name"] == "TestSphere"
    assert result["type"] == "Sphere"
    assert result["parameters"]["radius"] == 7


def test_create_cone():
    """원뿔 생성 테스트"""
    result = create_cone(10, 5, 15, "TestCone")
    
    assert result["success"] is True
    assert result["object_name"] == "TestCone"
    assert result["type"] == "Cone"
    assert result["parameters"]["radius1"] == 10
    assert result["parameters"]["radius2"] == 5
    assert result["parameters"]["height"] == 15


def test_invalid_parameters():
    """잘못된 파라미터 테스트"""
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        create_box(-10, 10, 10)  # 음수 길이
    
    with pytest.raises(ValidationError):
        create_cylinder(0, 20)  # 0 반지름
    
    with pytest.raises(ValidationError):
        create_sphere(-5)  # 음수 반지름


def test_new_document():
    """새 문서 생성 테스트"""
    result = new_document("TestDocument")
    
    assert result["success"] is True
    assert result["document_name"] == "TestDocument"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

