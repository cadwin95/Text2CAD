#!/usr/bin/env python3
"""
복잡한 객체 생성 테스트 (의자, 사다리 등)
위치 파라미터를 사용하여 복잡한 구조를 만듭니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent import ToolCallingAgent

print("="*60)
print("복잡한 객체 생성 테스트")
print("="*60)
print()

# Agent 초기화
agent = ToolCallingAgent(verbose=True, model="groq/openai/gpt-oss-20b")

# 테스트 1: 의자 만들기
print("\n" + "="*60)
print("테스트 1: 의자 만들기")
print("="*60)

chair_prompt = """
의자를 만들어주세요. 다음과 같은 구조로 만들어주세요:
1. 좌판: 40x40x5 크기의 박스를 위치 (0, 0, 45)에 만들기
2. 다리1: 5x5x45 크기의 박스를 위치 (0, 0, 0)에 만들기
3. 다리2: 5x5x45 크기의 박스를 위치 (35, 0, 0)에 만들기  
4. 다리3: 5x5x45 크기의 박스를 위치 (0, 35, 0)에 만들기
5. 다리4: 5x5x45 크기의 박스를 위치 (35, 35, 0)에 만들기
6. 등받이: 40x5x50 크기의 박스를 위치 (0, 35, 45)에 만들기
7. 완료되면 finish 호출

각 부품의 이름은 Seat, Leg1, Leg2, Leg3, Leg4, Back으로 해주세요.
"""

result = agent.run(chair_prompt)  # max_iterations=16 (기본값)

print("\n결과:")
print(f"  - 성공: {result['success']}")
print(f"  - 반복: {result['iterations']}회")
print(f"  - 도구 호출: {result.get('tool_calls_count', 0)}개")
print(f"  - 완료: {result.get('finished', False)}")
print(f"  - 메시지: {result['message']}")

# 히스토리 초기화
agent.reset()

# 테스트 2: 사다리 만들기
print("\n" + "="*60)
print("테스트 2: 사다리 만들기")
print("="*60)

ladder_prompt = """
사다리를 만들어주세요. 다음과 같은 구조로 만들어주세요:
1. 왼쪽 기둥: 5x5x200 크기의 박스를 위치 (0, 0, 0)에 만들기
2. 오른쪽 기둥: 5x5x200 크기의 박스를 위치 (35, 0, 0)에 만들기
3. 발판1: 40x5x5 크기의 박스를 위치 (0, 0, 40)에 만들기
4. 발판2: 40x5x5 크기의 박스를 위치 (0, 0, 80)에 만들기
5. 발판3: 40x5x5 크기의 박스를 위치 (0, 0, 120)에 만들기
6. 발판4: 40x5x5 크기의 박스를 위치 (0, 0, 160)에 만들기
7. 완료되면 finish 호출

각 부품의 이름은 LeftPole, RightPole, Step1, Step2, Step3, Step4로 해주세요.
"""

result = agent.run(ladder_prompt)  # max_iterations=16 (기본값)

print("\n결과:")
print(f"  - 성공: {result['success']}")
print(f"  - 반복: {result['iterations']}회")
print(f"  - 도구 호출: {result.get('tool_calls_count', 0)}개")
print(f"  - 완료: {result.get('finished', False)}")
print(f"  - 메시지: {result['message']}")

# 히스토리 초기화
agent.reset()

# 테스트 3: 간단한 테이블
print("\n" + "="*60)
print("테스트 3: 간단한 테이블")
print("="*60)

table_prompt = """
간단한 테이블을 만들어주세요:
1. 상판: 80x60x5 크기의 박스를 위치 (0, 0, 70)에 만들기
2. 다리1: 5x5x70 크기의 박스를 위치 (0, 0, 0)에 만들기
3. 다리2: 5x5x70 크기의 박스를 위치 (75, 0, 0)에 만들기
4. 다리3: 5x5x70 크기의 박스를 위치 (0, 55, 0)에 만들기
5. 다리4: 5x5x70 크기의 박스를 위치 (75, 55, 0)에 만들기
6. 완료되면 finish 호출

각 부품의 이름은 Top, TLeg1, TLeg2, TLeg3, TLeg4로 해주세요.
"""

result = agent.run(table_prompt)  # max_iterations=16 (기본값)

print("\n결과:")
print(f"  - 성공: {result['success']}")
print(f"  - 반복: {result['iterations']}회")
print(f"  - 도구 호출: {result.get('tool_calls_count', 0)}개")
print(f"  - 완료: {result.get('finished', False)}")
print(f"  - 메시지: {result['message']}")

print("\n" + "="*60)
print("모든 테스트 완료!")
print("="*60)
print()
print("주요 개선사항:")
print("  ✅ 위치 파라미터 (x, y, z) 추가")
print("  ✅ 회전 파라미터 (rotation) 추가")
print("  ✅ 복잡한 구조 생성 가능")
print("  ✅ 의자, 사다리, 테이블 등 제작 가능")
print()
print("생성된 객체는 FreeCAD에서 확인할 수 있습니다:")
print("  1. Agent로 문서 저장: agent.run('현재 문서를 furniture.FCStd로 저장해줘')")
print("  2. FreeCAD에서 열기: open -a FreeCAD furniture.FCStd")
print()

