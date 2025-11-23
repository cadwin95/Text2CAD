#!/usr/bin/env python3
"""
서비스 헬스체크 스크립트
Docker Compose 서비스 상태 및 API 엔드포인트를 확인합니다.
"""

import subprocess
import sys
import time
from typing import Dict, Tuple

try:
    import httpx
except ImportError:
    print("httpx 패키지가 필요합니다: uv add httpx")
    sys.exit(1)

# 색상 코드
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check_docker_service(service_name: str) -> Tuple[bool, str]:
    """Docker Compose 서비스 상태 확인"""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "-q", service_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # 컨테이너 ID가 있으면 실행 중
            container_id = result.stdout.strip()
            
            # 상태 확인
            status_result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Status}}", container_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            status = status_result.stdout.strip()
            if status == "running":
                return True, f"실행 중 (ID: {container_id[:12]})"
            else:
                return False, f"상태: {status}"
        else:
            return False, "컨테이너를 찾을 수 없음"
    
    except subprocess.TimeoutExpired:
        return False, "타임아웃"
    except FileNotFoundError:
        return False, "docker-compose를 찾을 수 없음"
    except Exception as e:
        return False, f"오류: {str(e)}"


def check_http_endpoint(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """HTTP 엔드포인트 상태 확인"""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            if response.status_code == 200:
                return True, f"응답 성공 (200 OK)"
            else:
                return False, f"HTTP {response.status_code}"
    except httpx.ConnectError:
        return False, "연결 실패"
    except httpx.TimeoutException:
        return False, "타임아웃"
    except Exception as e:
        return False, f"오류: {str(e)}"


def check_litellm_models() -> Tuple[bool, str]:
    """LiteLLM에서 사용 가능한 모델 목록 확인"""
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get("http://localhost:4000/v1/models")
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    models = [model["id"] for model in data["data"]]
                    return True, f"{len(models)}개 모델: {', '.join(models[:3])}"
                else:
                    return True, "모델 정보 확인 불가"
            else:
                return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"오류: {str(e)}"


def check_postgres_connection() -> Tuple[bool, str]:
    """PostgreSQL 연결 확인"""
    try:
        result = subprocess.run(
            [
                "docker", "exec", "litellm_postgres",
                "pg_isready", "-d", "litellm", "-U", "llmproxy"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return True, "연결 가능"
        else:
            return False, result.stderr.strip() or "연결 실패"
    except Exception as e:
        return False, f"오류: {str(e)}"


def main():
    """메인 헬스체크 함수"""
    print(f"\n{BOLD}=== Docker Compose 서비스 헬스체크 ==={RESET}\n")
    
    # Docker 서비스 상태
    print(f"{BOLD}1. Docker 컨테이너 상태:{RESET}")
    services = [
        ("litellm-proxy", "LiteLLM Proxy"),
        ("postgres", "PostgreSQL"),
        ("prometheus", "Prometheus"),
    ]
    
    all_services_ok = True
    for service_name, description in services:
        ok, msg = check_docker_service(service_name)
        status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
        print(f"  {status} {description} ({service_name}): {msg}")
        if not ok:
            all_services_ok = False
    print()
    
    if not all_services_ok:
        print(f"{RED}일부 서비스가 실행되지 않습니다.{RESET}")
        print(f"다음 명령으로 서비스를 시작하세요:")
        print(f"  {BOLD}docker-compose up -d{RESET}")
        print()
        return
    
    # HTTP 엔드포인트 체크
    print(f"{BOLD}2. API 엔드포인트 상태:{RESET}")
    endpoints = [
        ("http://localhost:4000/health", "LiteLLM Health"),
        ("http://localhost:9090/-/healthy", "Prometheus Health"),
    ]
    
    for url, description in endpoints:
        ok, msg = check_http_endpoint(url)
        status = f"{GREEN}✓{RESET}" if ok else f"{YELLOW}○{RESET}"
        print(f"  {status} {description}: {msg}")
    print()
    
    # LiteLLM 모델 목록
    print(f"{BOLD}3. LiteLLM 사용 가능 모델:{RESET}")
    ok, msg = check_litellm_models()
    status = f"{GREEN}✓{RESET}" if ok else f"{YELLOW}○{RESET}"
    print(f"  {status} {msg}")
    print()
    
    # PostgreSQL 연결
    print(f"{BOLD}4. 데이터베이스 연결:{RESET}")
    ok, msg = check_postgres_connection()
    status = f"{GREEN}✓{RESET}" if ok else f"{YELLOW}○{RESET}"
    print(f"  {status} PostgreSQL: {msg}")
    print()
    
    # 최종 결과
    print(f"{BOLD}{'='*60}{RESET}")
    if all_services_ok:
        print(f"{GREEN}✓ 모든 서비스가 정상적으로 실행 중입니다!{RESET}")
        print(f"\n다음 단계:")
        print(f"  - 모델 호환성 체크: {BOLD}python scripts/check_model_compatibility.py{RESET}")
    else:
        print(f"{RED}✗ 일부 서비스에 문제가 있습니다.{RESET}")
    print()


if __name__ == "__main__":
    main()

