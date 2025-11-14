#!/usr/bin/env python3
"""
finish 도구 테스트 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import ToolCallingAgent

print("="*60)
print("finish 도구 테스트")
print("="*60)
print()

# 테스트 케이스
test_cases = [
    {
        "name": "간단한 박스 생성",
        "command": "10mm x 10mm x 10mm 크기의 박스를 만들고 완료했다고 알려줘",
        "model": "llama.cpp"
    },
    {
        "name": "여러 객체 생성",
        "command": "반지름 5mm인 구와 10x10x10 박스를 만들고 작업을 완료해줘",
        "model": "llama.cpp"
    },
    {
        "name": "Groq OSS - 박스 생성",
        "command": "Create a 15mm cube and finish the task",
        "model": "groq/openai/gpt-oss-20b"
    },
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{i}. {test_case['name']}")
    print(f"   모델: {test_case['model']}")
    print(f"   명령: {test_case['command']}")
    print("-"*60)
    
    try:
        agent = ToolCallingAgent(
            model=test_case['model'],
            verbose=True
        )
        
        result = agent.run(test_case['command'], max_iterations=5)
        
        print()
        print("결과:")
        print(f"  - 성공: {result['success']}")
        print(f"  - 반복: {result['iterations']}회")
        print(f"  - 도구 호출: {result.get('tool_calls_count', 0)}개")
        print(f"  - 완료: {result.get('finished', False)}")
        print(f"  - 메시지: {result['message'][:100]}...")
        
        if result.get('warning'):
            print(f"  ⚠ 경고: {result['warning']}")
        
        print()
        
    except Exception as e:
        print(f"  ✗ 오류: {e}")
        import traceback
        traceback.print_exc()
    
    print()

print("="*60)
print("테스트 완료")
print("="*60)
print()
print("주요 개선사항:")
print("  1. ✅ finish 도구 추가")
print("  2. ✅ 명시적 작업 완료 처리")
print("  3. ✅ 모델이 finish 호출하도록 유도")
print("  4. ✅ 도구 호출 없는 경우 경고")
print()

