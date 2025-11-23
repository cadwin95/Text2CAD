"""
MCP 서버 도구 테스트
"""

import pytest
from src.mcp_server.server import get_tools_for_openai


def test_tools_format():
    """도구 포맷 테스트"""
    tools = get_tools_for_openai()
    
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # 첫 번째 도구 검증
    tool = tools[0]
    assert "type" in tool
    assert tool["type"] == "function"
    assert "function" in tool
    
    func = tool["function"]
    assert "name" in func
    assert "description" in func
    assert "parameters" in func
    
    params = func["parameters"]
    assert "type" in params
    assert params["type"] == "object"
    assert "properties" in params
    assert "required" in params


def test_all_tools_present():
    """모든 도구가 포함되어 있는지 테스트"""
    tools = get_tools_for_openai()
    tool_names = [t["function"]["name"] for t in tools]
    
    expected_tools = [
        "freecad_create_box",
        "freecad_create_cylinder",
        "freecad_create_sphere",
        "freecad_create_cone",
        "freecad_new_document",
        "freecad_save_document",
        "freecad_get_document_info",
        "freecad_export_image"
    ]
    
    for expected in expected_tools:
        assert expected in tool_names, f"{expected} 도구가 없습니다"


def test_tool_parameters():
    """도구 파라미터 검증"""
    tools = get_tools_for_openai()
    
    # create_box 도구 찾기
    box_tool = next(t for t in tools if t["function"]["name"] == "freecad_create_box")
    params = box_tool["function"]["parameters"]
    
    assert "length" in params["properties"]
    assert "width" in params["properties"]
    assert "height" in params["properties"]
    assert params["properties"]["length"]["type"] == "number"
    assert "length" in params["required"]
    assert "width" in params["required"]
    assert "height" in params["required"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

