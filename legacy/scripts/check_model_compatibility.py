#!/usr/bin/env python3
"""
모델 호환성 체크 스크립트
LiteLLM proxy와 Qwen3-4B의 function calling 지원 여부를 확인합니다.
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 색상 코드
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def test_litellm_connection() -> tuple[bool, str]:
    """LiteLLM proxy 연결 테스트"""
    try:
        from openai import OpenAI
        
        base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        api_key = os.getenv("LITELLM_API_KEY", "sk-1234")
        
        client = OpenAI(base_url=base_url, api_key=api_key)
        
        # 간단한 완성 요청
        response = client.chat.completions.create(
            model="groq/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        return True, f"연결 성공 (모델: groq/llama-3.1-8b-instruct)"
    except ImportError:
        return False, "openai 패키지가 설치되지 않았습니다"
    except Exception as e:
        return False, f"연결 실패: {str(e)}"


def test_function_calling() -> tuple[bool, str]:
    """Function calling 지원 테스트"""
    try:
        from openai import OpenAI
        
        base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        api_key = os.getenv("LITELLM_API_KEY", "sk-1234")
        
        client = OpenAI(base_url=base_url, api_key=api_key)
        
        # 간단한 도구 정의
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city name"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        # Function calling 테스트
        response = client.chat.completions.create(
            model="groq/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
            tools=tools,
            max_tokens=100
        )
        
        # Tool calls가 있는지 확인
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            return True, f"Function calling 지원 (도구 호출: {len(response.choices[0].message.tool_calls)}개)"
        else:
            return False, "Function calling을 지원하지 않습니다 (fine-tuning 필요)"
    
    except Exception as e:
        return False, f"테스트 실패: {str(e)}"


def test_alternative_models() -> Dict[str, tuple[bool, str]]:
    """대체 모델 사용 가능 여부 테스트"""
    results = {}
    
    try:
        from openai import OpenAI
        
        base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        api_key = os.getenv("LITELLM_API_KEY", "sk-1234")
        
        client = OpenAI(base_url=base_url, api_key=api_key)
        
        # OpenAI 모델 테스트 (합성 데이터 생성용)
        models_to_test = [
            ("openai/gpt-4o", "GPT-4o (합성 데이터용)"),
            ("groq/llama-3.3-70b-versatile", "Groq Llama-3.3 (합성 데이터용)"),
        ]
        
        for model_name, description in models_to_test:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                results[model_name] = (True, f"{description} - 사용 가능")
            except Exception as e:
                results[model_name] = (False, f"{description} - 실패: {str(e)[:50]}")
    
    except ImportError:
        results["error"] = (False, "openai 패키지가 설치되지 않았습니다")
    
    return results


def main():
    """메인 체크 함수"""
    print(f"\n{BOLD}=== 모델 호환성 체크 ==={RESET}\n")
    
    # 환경 변수 확인
    print(f"{BOLD}환경 설정:{RESET}")
    base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
    api_key = os.getenv("LITELLM_API_KEY", "sk-1234")
    print(f"  LiteLLM Base URL: {base_url}")
    print(f"  API Key: {'설정됨' if api_key else '미설정'}")
    print()
    
    # LiteLLM 연결 테스트
    print(f"{BOLD}1. LiteLLM Proxy 연결 테스트:{RESET}")
    conn_ok, conn_msg = test_litellm_connection()
    status = f"{GREEN}✓{RESET}" if conn_ok else f"{RED}✗{RESET}"
    print(f"  {status} {conn_msg}")
    print()
    
    if not conn_ok:
        print(f"{RED}LiteLLM proxy에 연결할 수 없습니다.{RESET}")
        print(f"Docker Compose 서비스가 실행 중인지 확인하세요:")
        print(f"  {BOLD}docker-compose ps{RESET}")
        print()
        sys.exit(1)
    
    # Function calling 테스트
    print(f"{BOLD}2. Function Calling 지원 테스트:{RESET}")
    fc_ok, fc_msg = test_function_calling()
    status = f"{GREEN}✓{RESET}" if fc_ok else f"{YELLOW}⚠{RESET}"
    print(f"  {status} {fc_msg}")
    print()
    
    if not fc_ok:
        print(f"{YELLOW}권장 사항:{RESET}")
        print(f"  - 현재 모델이 function calling을 지원하지 않을 수 있습니다.")
        print(f"  - groq/llama-3.1-8b-instruct 또는 openai/gpt-4o-mini 등 function calling 지원 모델을 사용하세요.")
        print()
    
    # 대체 모델 테스트
    print(f"{BOLD}3. 합성 데이터 생성용 모델 테스트:{RESET}")
    alt_results = test_alternative_models()
    
    for model_name, (ok, msg) in alt_results.items():
        status = f"{GREEN}✓{RESET}" if ok else f"{YELLOW}○{RESET}"
        print(f"  {status} {msg}")
    print()
    
    # 최종 권장사항
    print(f"{BOLD}{'='*60}{RESET}")
    if conn_ok and fc_ok:
        print(f"{GREEN}✓ 모든 테스트 통과! Function calling을 바로 사용할 수 있습니다.{RESET}")
    elif conn_ok:
        print(f"{YELLOW}⚠ 연결은 성공했지만 function calling이 제한적입니다.{RESET}")
        print(f"\n다음 단계:")
        print(f"  1. groq/llama-3.1-8b-instruct 또는 openai/gpt-4o-mini 등 function calling 지원 모델 사용")
        print(f"  2. 필요시 OpenPipe로 도구 호출 데이터 수집")
    else:
        print(f"{RED}✗ 연결 실패. Docker 서비스를 확인하세요.{RESET}")
    print()


if __name__ == "__main__":
    main()

