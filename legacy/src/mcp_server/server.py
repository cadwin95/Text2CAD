"""
FreeCAD MCP 서버 구현
FastMCP를 사용하여 FreeCAD 도구를 MCP 프로토콜로 제공합니다.
"""

import sys
import json
from typing import Optional

try:
    from fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: fastmcp가 설치되지 않았습니다. 'uv add fastmcp'로 설치하세요.")

from ..freecad_tools import (
    create_box,
    create_cylinder,
    create_sphere,
    create_cone,
    new_document,
    save_document,
    get_active_document,
    export_image
)


# MCP 서버 초기화
if MCP_AVAILABLE:
    mcp = FastMCP("freecad-server")
else:
    mcp = None


if MCP_AVAILABLE:
    @mcp.tool()
    def freecad_create_box(
        length: float,
        width: float,
        height: float,
        name: str = "Box"
    ) -> str:
        """
        FreeCAD에서 박스를 생성합니다.
        
        Args:
            length: 박스의 길이 (X축, mm)
            width: 박스의 너비 (Y축, mm)
            height: 박스의 높이 (Z축, mm)
            name: 객체 이름 (기본값: "Box")
        
        Returns:
            생성 결과 메시지
        """
        result = create_box(length, width, height, name)
        if result["success"]:
            return f"✓ 박스 '{result['object_name']}'를 생성했습니다. 크기: {length}×{width}×{height}mm"
        else:
            return f"✗ 박스 생성 실패: {result.get('message', '알 수 없는 오류')}"


    @mcp.tool()
    def freecad_create_cylinder(
        radius: float,
        height: float,
        name: str = "Cylinder"
    ) -> str:
        """
        FreeCAD에서 실린더를 생성합니다.
        
        Args:
            radius: 실린더의 반지름 (mm)
            height: 실린더의 높이 (mm)
            name: 객체 이름 (기본값: "Cylinder")
        
        Returns:
            생성 결과 메시지
        """
        result = create_cylinder(radius, height, name)
        if result["success"]:
            return f"✓ 실린더 '{result['object_name']}'를 생성했습니다. 반지름: {radius}mm, 높이: {height}mm"
        else:
            return f"✗ 실린더 생성 실패: {result.get('message', '알 수 없는 오류')}"


    @mcp.tool()
    def freecad_create_sphere(
        radius: float,
        name: str = "Sphere"
    ) -> str:
        """
        FreeCAD에서 구를 생성합니다.
        
        Args:
            radius: 구의 반지름 (mm)
            name: 객체 이름 (기본값: "Sphere")
        
        Returns:
            생성 결과 메시지
        """
        result = create_sphere(radius, name)
        if result["success"]:
            return f"✓ 구 '{result['object_name']}'를 생성했습니다. 반지름: {radius}mm"
        else:
            return f"✗ 구 생성 실패: {result.get('message', '알 수 없는 오류')}"


    @mcp.tool()
    def freecad_create_cone(
        radius1: float,
        radius2: float,
        height: float,
        name: str = "Cone"
    ) -> str:
        """
        FreeCAD에서 원뿔을 생성합니다.
        
        Args:
            radius1: 밑면 반지름 (mm)
            radius2: 윗면 반지름 (mm)
            height: 원뿔의 높이 (mm)
            name: 객체 이름 (기본값: "Cone")
        
        Returns:
            생성 결과 메시지
        """
        result = create_cone(radius1, radius2, height, name)
        if result["success"]:
            return f"✓ 원뿔 '{result['object_name']}'를 생성했습니다. 밑면: {radius1}mm, 윗면: {radius2}mm, 높이: {height}mm"
        else:
            return f"✗ 원뿔 생성 실패: {result.get('message', '알 수 없는 오류')}"


    @mcp.tool()
    def freecad_new_document(name: str = "Unnamed") -> str:
        """
        새 FreeCAD 문서를 생성합니다.
        
        Args:
            name: 문서 이름 (기본값: "Unnamed")
        
        Returns:
            생성 결과 메시지
        """
        result = new_document(name)
        if result["success"]:
            return f"✓ 문서 '{result['document_name']}'를 생성했습니다."
        else:
            return f"✗ 문서 생성 실패: {result.get('message', '알 수 없는 오류')}"


    @mcp.tool()
    def freecad_save_document(filepath: str, document_name: Optional[str] = None) -> str:
        """
        FreeCAD 문서를 파일로 저장합니다.
        
        Args:
            filepath: 저장할 파일 경로 (.FCStd)
            document_name: 저장할 문서 이름 (None이면 활성 문서)
        
        Returns:
            저장 결과 메시지
        """
        result = save_document(filepath, document_name)
        if result["success"]:
            return f"✓ 문서를 '{result['filepath']}'에 저장했습니다. (객체 {result.get('objects_count', 0)}개)"
        else:
            return f"✗ 문서 저장 실패: {result.get('message', '알 수 없는 오류')}"


    @mcp.tool()
    def freecad_get_document_info() -> str:
        """
        현재 활성 문서의 정보를 가져옵니다.
        
        Returns:
            문서 정보 메시지
        """
        result = get_active_document()
        if result["success"]:
            objects_list = ", ".join(result.get("objects", []))
            return f"✓ 문서: {result['document_name']}, 객체 수: {result['objects_count']}, 객체: [{objects_list}]"
        else:
            return f"✗ 활성 문서가 없습니다."


    @mcp.tool()
    def freecad_export_image(
        filepath: str,
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        FreeCAD 뷰포트를 이미지로 내보냅니다.
        
        Args:
            filepath: 저장할 이미지 경로 (.png, .jpg 등)
            width: 이미지 너비 (픽셀, 기본값: 800)
            height: 이미지 높이 (픽셀, 기본값: 600)
        
        Returns:
            내보내기 결과 메시지
        """
        result = export_image(filepath, width, height)
        if result["success"]:
            return f"✓ 이미지를 '{result['filepath']}'에 저장했습니다. ({width}×{height}px)"
        else:
            return f"✗ 이미지 내보내기 실패: {result.get('message', '알 수 없는 오류')}"


def get_tools_for_openai() -> list:
    """
    OpenAI function calling 포맷으로 도구 정의를 반환합니다.
    
    Returns:
        OpenAI tools 포맷 리스트
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "freecad_create_box",
                "description": "FreeCAD에서 박스를 생성합니다. 위치(x,y,z)와 회전을 지정할 수 있습니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "length": {"type": "number", "description": "박스의 길이 (X축, mm)"},
                        "width": {"type": "number", "description": "박스의 너비 (Y축, mm)"},
                        "height": {"type": "number", "description": "박스의 높이 (Z축, mm)"},
                        "x": {"type": "number", "description": "X 좌표 (mm, 기본값: 0)", "default": 0},
                        "y": {"type": "number", "description": "Y 좌표 (mm, 기본값: 0)", "default": 0},
                        "z": {"type": "number", "description": "Z 좌표 (mm, 기본값: 0)", "default": 0},
                        "rotation": {"type": "number", "description": "Z축 기준 회전 각도 (도, 기본값: 0)", "default": 0},
                        "name": {"type": "string", "description": "객체 이름", "default": "Box"}
                    },
                    "required": ["length", "width", "height"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "freecad_create_cylinder",
                "description": "FreeCAD에서 실린더를 생성합니다. 위치(x,y,z)와 회전을 지정할 수 있습니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "radius": {"type": "number", "description": "실린더의 반지름 (mm)"},
                        "height": {"type": "number", "description": "실린더의 높이 (mm)"},
                        "x": {"type": "number", "description": "X 좌표 (mm, 기본값: 0)", "default": 0},
                        "y": {"type": "number", "description": "Y 좌표 (mm, 기본값: 0)", "default": 0},
                        "z": {"type": "number", "description": "Z 좌표 (mm, 기본값: 0)", "default": 0},
                        "rotation": {"type": "number", "description": "Z축 기준 회전 각도 (도, 기본값: 0)", "default": 0},
                        "name": {"type": "string", "description": "객체 이름", "default": "Cylinder"}
                    },
                    "required": ["radius", "height"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "freecad_create_sphere",
                "description": "FreeCAD에서 구를 생성합니다. 위치(x,y,z)를 지정할 수 있습니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "radius": {"type": "number", "description": "구의 반지름 (mm)"},
                        "x": {"type": "number", "description": "X 좌표 (mm, 기본값: 0)", "default": 0},
                        "y": {"type": "number", "description": "Y 좌표 (mm, 기본값: 0)", "default": 0},
                        "z": {"type": "number", "description": "Z 좌표 (mm, 기본값: 0)", "default": 0},
                        "name": {"type": "string", "description": "객체 이름", "default": "Sphere"}
                    },
                    "required": ["radius"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "freecad_create_cone",
                "description": "FreeCAD에서 원뿔을 생성합니다. 위치(x,y,z)와 회전을 지정할 수 있습니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "radius1": {"type": "number", "description": "밑면 반지름 (mm)"},
                        "radius2": {"type": "number", "description": "윗면 반지름 (mm)"},
                        "height": {"type": "number", "description": "원뿔의 높이 (mm)"},
                        "x": {"type": "number", "description": "X 좌표 (mm, 기본값: 0)", "default": 0},
                        "y": {"type": "number", "description": "Y 좌표 (mm, 기본값: 0)", "default": 0},
                        "z": {"type": "number", "description": "Z 좌표 (mm, 기본값: 0)", "default": 0},
                        "rotation": {"type": "number", "description": "Z축 기준 회전 각도 (도, 기본값: 0)", "default": 0},
                        "name": {"type": "string", "description": "객체 이름", "default": "Cone"}
                    },
                    "required": ["radius1", "radius2", "height"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "freecad_new_document",
                "description": "새 FreeCAD 문서를 생성합니다",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "문서 이름", "default": "Unnamed"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "freecad_save_document",
                "description": "FreeCAD 문서를 파일로 저장합니다",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "저장할 파일 경로 (.FCStd)"},
                        "document_name": {"type": "string", "description": "저장할 문서 이름 (None이면 활성 문서)"}
                    },
                    "required": ["filepath"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "freecad_get_document_info",
                "description": "현재 활성 문서의 정보를 가져옵니다",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "freecad_export_image",
                "description": "FreeCAD 뷰포트를 이미지로 내보냅니다",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "저장할 이미지 경로"},
                        "width": {"type": "number", "description": "이미지 너비 (픽셀)", "default": 800},
                        "height": {"type": "number", "description": "이미지 높이 (픽셀)", "default": 600}
                    },
                    "required": ["filepath"]
                }
            }
        }
    ]
    return tools


def run_server():
    """MCP 서버 실행"""
    if not MCP_AVAILABLE:
        print("Error: fastmcp가 설치되지 않았습니다.")
        print("다음 명령으로 설치하세요: uv add fastmcp")
        sys.exit(1)
    
    print("FreeCAD MCP 서버를 시작합니다...")
    mcp.run()


if __name__ == "__main__":
    run_server()

