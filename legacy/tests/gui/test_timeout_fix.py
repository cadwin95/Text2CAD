#!/usr/bin/env python3
"""
타임아웃 수정 테스트
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import ToolCallingAgent

print("="*70)
print("🧪 타임아웃 수정 테스트")
print("="*70)
print()

# Agent 초기화
agent = ToolCallingAgent(model='groq/openai/gpt-oss-20b', verbose=False)

# 많은 객체를 만드는 테스트
test_prompt = """
간단한 사다리를 만들어줘:
1. 왼쪽 기둥: 5x5x100 at (0, 0, 0)
2. 오른쪽 기둥: 5x5x100 at (30, 0, 0)
3. 발판1: 30x5x3 at (0, 0, 20)
4. 발판2: 30x5x3 at (0, 0, 40)
5. 발판3: 30x5x3 at (0, 0, 60)
6. 발판4: 30x5x3 at (0, 0, 80)
7. finish 호출
"""

print("테스트 시작: 6개 객체 생성")
print("-"*70)

try:
    result = agent.run(test_prompt, max_iterations=16)
    
    if result['success']:
        print()
        print("="*70)
        print("✅ 테스트 성공!")
        print("="*70)
        print(f"  - 반복: {result['iterations']}회")
        print(f"  - 완료: {result.get('finished', False)}")
        print(f"  - 메시지: {result.get('message', 'N/A')}")
    else:
        print()
        print("="*70)
        print("❌ 테스트 실패")
        print("="*70)
        print(f"  - 메시지: {result.get('message', 'Unknown error')}")

except Exception as e:
    print()
    print("="*70)
    print("❌ 오류 발생")
    print("="*70)
    print(f"  {e}")

print()
print("💡 이제 interactive_freecad.py를 실행해보세요:")
print("   python3 interactive_freecad.py")
print()

