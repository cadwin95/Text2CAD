#!/usr/bin/env python3
"""
Agent 테스트 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import ToolCallingAgent


def test_agent():
    """Agent 기본 테스트"""
    print("="*60)
    print("FreeCAD Tool Calling Agent 테스트")
    print("="*60)
    print()
    
    # Agent 초기화
    print("1. Agent 초기화...")
    try:
        agent = ToolCallingAgent(verbose=False)
        print("   ✓ Agent 초기화 성공\n")
    except Exception as e:
        print(f"   ✗ Agent 초기화 실패: {e}\n")
        return
    
    # 테스트 케이스
    test_cases = [
        {
            "name": "박스 생성 (한국어)",
            "command": "10mm x 10mm x 10mm 크기의 박스를 만들어줘",
        },
        {
            "name": "실린더 생성 (한국어)",
            "command": "반지름 5mm, 높이 20mm인 실린더를 생성해",
        },
        {
            "name": "구 생성 (한국어)",
            "command": "반지름 7mm인 구를 만들어",
        },
        {
            "name": "박스 생성 (영어)",
            "command": "Create a box with dimensions 15mm x 15mm x 15mm",
        },
        {
            "name": "복합 명령",
            "command": "반지름 5mm인 구와 10x10x10 박스를 만들어줘",
        },
    ]
    
    results = []
    
    # 각 테스트 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   명령: {test_case['command']}")
        
        try:
            result = agent.run(test_case['command'], max_iterations=3)
            
            if result["success"]:
                print(f"   ✓ 성공")
                print(f"   - 반복: {result['iterations']}회")
                print(f"   - 메시지: {result['message'][:100]}...")
                results.append({
                    "test": test_case['name'],
                    "status": "성공",
                    "result": result
                })
            else:
                print(f"   ✗ 실패: {result['message']}")
                results.append({
                    "test": test_case['name'],
                    "status": "실패",
                    "result": result
                })
        except Exception as e:
            print(f"   ✗ 오류: {e}")
            results.append({
                "test": test_case['name'],
                "status": "오류",
                "error": str(e)
            })
        
        print()
        
        # 히스토리 초기화
        agent.reset()
    
    # 결과 요약
    print("="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    success_count = sum(1 for r in results if r["status"] == "성공")
    total_count = len(results)
    
    print(f"전체: {total_count}개")
    print(f"성공: {success_count}개")
    print(f"실패: {total_count - success_count}개")
    print(f"성공률: {success_count/total_count*100:.1f}%")
    print()
    
    return results


if __name__ == "__main__":
    results = test_agent()

