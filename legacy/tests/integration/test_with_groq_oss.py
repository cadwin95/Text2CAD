#!/usr/bin/env python3
"""
Groq OSS 모델을 사용한 Agent 테스트
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

print("="*60)
print("Groq OSS 모델 테스트")
print("="*60)
print()

# 1. Groq OSS 모델 직접 호출 테스트
print("1. Groq OSS 모델 직접 호출")
print("-"*60)

try:
    from openai import OpenAI
    
    client = OpenAI(
        base_url=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        api_key=os.getenv("LITELLM_API_KEY", "sk-1234")
    )
    
    print("모델: groq/openai/gpt-oss-20b")
    response = client.chat.completions.create(
        model="groq/openai/gpt-oss-20b",
        messages=[{"role": "user", "content": "안녕하세요. 간단히 인사해주세요."}],
        max_tokens=100
    )
    
    print(f"   ✓ 응답: {response.choices[0].message.content}")
    print("   → Groq OSS 연결: 정상 ✓")
except Exception as e:
    print(f"   ✗ 오류: {e}")

print()

# 2. Function Calling 테스트
print("2. Groq OSS Function Calling 테스트")
print("-"*60)

try:
    from openai import OpenAI
    from src.mcp_server.server import get_tools_for_openai
    
    client = OpenAI(
        base_url=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        api_key=os.getenv("LITELLM_API_KEY", "sk-1234")
    )
    
    tools = get_tools_for_openai()
    
    print("   명령: '10mm x 10mm x 10mm 박스를 만들어줘'")
    response = client.chat.completions.create(
        model="groq/openai/gpt-oss-20b",
        messages=[{"role": "user", "content": "10mm x 10mm x 10mm 박스를 만들어줘"}],
        tools=tools[:4],  # 기본 도형 도구만
        max_tokens=200
    )
    
    if response.choices[0].message.tool_calls:
        print(f"   ✓ Tool calls: {len(response.choices[0].message.tool_calls)}개")
        for tc in response.choices[0].message.tool_calls:
            print(f"      - {tc.function.name}: {tc.function.arguments[:50]}...")
        print("   → Function calling: 지원 ✓")
    else:
        print(f"   ○ Tool calls 없음")
        print(f"   응답: {response.choices[0].message.content}")
        print("   → Function calling: 미지원 (fine-tuning 필요)")
except Exception as e:
    print(f"   ✗ 오류: {e}")

print()

# 3. Agent로 실행 테스트
print("3. Agent + Groq OSS 통합 테스트")
print("-"*60)

try:
    from src.agent import ToolCallingAgent
    
    # Groq OSS 모델로 Agent 초기화
    agent = ToolCallingAgent(
        model="groq/openai/gpt-oss-20b",
        verbose=False
    )
    
    print("   명령: '10mm x 10mm x 10mm 크기의 박스를 만들어줘'")
    result = agent.run("10mm x 10mm x 10mm 크기의 박스를 만들어줘", max_iterations=2)
    
    if result["success"]:
        print(f"   ✓ 성공")
        print(f"   - 반복: {result['iterations']}회")
        if result.get('tool_calls_count'):
            print(f"   - 도구 호출: {result['tool_calls_count']}개")
        print("   → Agent 실행: 정상 ✓")
    else:
        print(f"   ○ 완료: {result['message'][:100]}")
except Exception as e:
    print(f"   ✗ 오류: {e}")

print()

# 4. 합성 데이터 생성 테스트
print("4. Groq OSS로 합성 데이터 생성 테스트")
print("-"*60)

try:
    from openai import OpenAI
    
    client = OpenAI(
        base_url=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        api_key=os.getenv("LITELLM_API_KEY", "sk-1234")
    )
    
    print("   프롬프트: FreeCAD 명령 3개 생성")
    response = client.chat.completions.create(
        model="groq/openai/gpt-oss-20b",
        messages=[{
            "role": "user",
            "content": """FreeCAD에서 박스를 생성하는 자연스러운 한국어 명령어 3개를 생성해주세요.
각 명령어는 길이, 너비, 높이를 포함해야 합니다.
한 줄에 하나씩만 작성하세요."""
        }],
        temperature=0.8,
        max_tokens=200
    )
    
    print(f"   ✓ 생성된 명령어:")
    for line in response.choices[0].message.content.strip().split('\n'):
        if line.strip():
            print(f"      - {line.strip()}")
    print("   → 합성 데이터 생성: 가능 ✓")
except Exception as e:
    print(f"   ✗ 오류: {e}")

print()

# 결과 요약
print("="*60)
print("Groq OSS 모델 테스트 완료")
print("="*60)
print()
print("요약:")
print("  - Groq OSS (openai/gpt-oss-20b)는 Groq의 오픈소스 모델")
print("  - Function calling 지원 여부 확인 완료")
print("  - 합성 데이터 생성에 활용 가능")
print()
print("다음 단계:")
print("  1. 합성 데이터 생성: python -m src.training.synthetic_data")
print("  2. Fine-tuning: python -m src.training.finetune")

