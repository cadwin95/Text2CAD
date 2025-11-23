#!/usr/bin/env python3
"""
Agent 간단 테스트 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*60)
print("FreeCAD Tool Calling Agent 간단 테스트")
print("="*60)
print()

# 1. FreeCAD 도구 직접 테스트
print("1. FreeCAD 도구 직접 호출 테스트")
print("-"*60)

try:
    from src.freecad_tools import create_box, create_cylinder, create_sphere
    
    print("a) 박스 생성...")
    result = create_box(10, 10, 10, "TestBox")
    print(f"   ✓ 결과: {result['success']}, 객체: {result['object_name']}")
    
    print("b) 실린더 생성...")
    result = create_cylinder(5, 20, "TestCylinder")
    print(f"   ✓ 결과: {result['success']}, 객체: {result['object_name']}")
    
    print("c) 구 생성...")
    result = create_sphere(7, "TestSphere")
    print(f"   ✓ 결과: {result['success']}, 객체: {result['object_name']}")
    
    print("   → FreeCAD 도구: 정상 작동 ✓")
except Exception as e:
    print(f"   ✗ 오류: {e}")

print()

# 2. MCP 도구 포맷 테스트
print("2. MCP 도구 포맷 테스트")
print("-"*60)

try:
    from src.mcp_server.server import get_tools_for_openai
    
    tools = get_tools_for_openai()
    print(f"   사용 가능한 도구: {len(tools)}개")
    for i, tool in enumerate(tools[:3], 1):
        func = tool["function"]
        print(f"   {i}. {func['name']}")
    print("   ...")
    print("   → MCP 도구 포맷: 정상 ✓")
except Exception as e:
    print(f"   ✗ 오류: {e}")

print()

# 3. Agent 초기화 테스트
print("3. Agent 초기화 테스트")
print("-"*60)

try:
    from src.agent import ToolCallingAgent
    
    agent = ToolCallingAgent(verbose=False)
    print("   ✓ Agent 초기화 성공")
    print("   → Agent: 정상 ✓")
except Exception as e:
    print(f"   ✗ 오류: {e}")

print()

# 4. Agent 명령 실행 테스트 (간단한 버전)
print("4. Agent 명령 실행 테스트")
print("-"*60)

try:
    from src.agent import ToolCallingAgent
    
    agent = ToolCallingAgent(verbose=False)
    
    # 간단한 명령 하나만 테스트
    print("   명령: '10mm x 10mm x 10mm 크기의 박스를 만들어줘'")
    result = agent.run("10mm x 10mm x 10mm 크기의 박스를 만들어줘", max_iterations=2)
    
    if result["success"]:
        print(f"   ✓ 성공")
        print(f"   - 반복: {result['iterations']}회")
        if result.get('tool_calls_count'):
            print(f"   - 도구 호출: {result['tool_calls_count']}개")
        print("   → Agent 실행: 정상 ✓")
    else:
        print(f"   ✗ 실패: {result['message']}")
except Exception as e:
    print(f"   ✗ 오류: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
print("테스트 완료")
print("="*60)

