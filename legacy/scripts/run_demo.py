#!/usr/bin/env python3
"""
FreeCAD Tool Calling Agent 데모
모든 기능을 시연합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import ToolCallingAgent
from src.freecad_tools import create_box, create_cylinder, create_sphere


def print_header(title: str):
    """헤더 출력"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")


def demo_direct_tools():
    """FreeCAD 도구 직접 호출 데모"""
    print_header("1. FreeCAD 도구 직접 호출")
    
    print("📦 박스 생성...")
    result = create_box(10, 10, 10, "DemoBox")
    print(f"  결과: {result}\n")
    
    print("🔵 실린더 생성...")
    result = create_cylinder(5, 20, "DemoCylinder")
    print(f"  결과: {result}\n")
    
    print("⚪ 구 생성...")
    result = create_sphere(7, "DemoSphere")
    print(f"  결과: {result}\n")


def demo_agent_korean():
    """Agent로 한국어 명령 실행 데모"""
    print_header("2. Agent - 한국어 명령")
    
    agent = ToolCallingAgent(verbose=False)
    
    commands = [
        "10mm x 10mm x 10mm 크기의 박스를 만들어줘",
        "반지름 5mm, 높이 20mm인 실린더를 생성해",
        "반지름 7mm인 구를 만들어",
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n[{i}] 명령: {cmd}")
        result = agent.run(cmd)
        if result["success"]:
            print(f"    ✓ 성공: {result['message']}")
        else:
            print(f"    ✗ 실패: {result['message']}")
        agent.reset()


def demo_agent_english():
    """Agent로 영어 명령 실행 데모"""
    print_header("3. Agent - 영어 명령")
    
    agent = ToolCallingAgent(verbose=False)
    
    commands = [
        "Create a box with dimensions 15mm x 15mm x 15mm",
        "Make a cylinder with radius 8mm and height 25mm",
        "Generate a sphere with radius 10mm",
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n[{i}] Command: {cmd}")
        result = agent.run(cmd)
        if result["success"]:
            print(f"    ✓ Success: {result['message']}")
        else:
            print(f"    ✗ Failed: {result['message']}")
        agent.reset()


def demo_agent_complex():
    """Agent로 복잡한 명령 실행 데모"""
    print_header("4. Agent - 복잡한 명령")
    
    agent = ToolCallingAgent(verbose=True)
    
    print("\n복합 명령: 여러 객체 생성")
    result = agent.run("반지름 5mm인 구와 10x10x10 박스를 만들어줘")
    
    if result["success"]:
        print(f"\n✓ 성공!")
    else:
        print(f"\n✗ 실패: {result['message']}")


def demo_mcp_tools():
    """MCP 도구 포맷 데모"""
    print_header("5. MCP 도구 포맷")
    
    from src.mcp_server.server import get_tools_for_openai
    
    tools = get_tools_for_openai()
    
    print(f"사용 가능한 도구: {len(tools)}개\n")
    
    for i, tool in enumerate(tools, 1):
        func = tool["function"]
        print(f"{i}. {func['name']}")
        print(f"   설명: {func['description']}")
        print(f"   파라미터: {', '.join(func['parameters']['properties'].keys())}")
        print()


def main():
    """메인 함수"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     FreeCAD Tool Calling Agent - 데모                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    demos = [
        ("FreeCAD 도구 직접 호출", demo_direct_tools),
        ("Agent - 한국어 명령", demo_agent_korean),
        ("Agent - 영어 명령", demo_agent_english),
        ("Agent - 복잡한 명령", demo_agent_complex),
        ("MCP 도구 포맷", demo_mcp_tools),
    ]
    
    print("실행할 데모를 선택하세요:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. 모두 실행")
    print()
    
    try:
        choice = input("선택 (0-5): ").strip()
        
        if choice == "0":
            # 모두 실행
            for name, func in demos:
                func()
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            # 선택한 데모 실행
            demos[int(choice) - 1][1]()
        else:
            print("잘못된 선택입니다.")
            return
        
        print_header("데모 완료!")
        print("다음 단계:")
        print("  - 합성 데이터 생성: python -m src.training.synthetic_data")
        print("  - 데이터 수집: python -m src.training.data_collector")
        print("  - Fine-tuning: python -m src.training.finetune")
        print()
    
    except KeyboardInterrupt:
        print("\n\n데모가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

