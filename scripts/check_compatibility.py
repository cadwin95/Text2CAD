#!/usr/bin/env python3
"""
호환성 및 버전 체크 스크립트
Python 버전, 필수 패키지, FreeCAD API 등을 검증합니다.
"""

import sys
import platform
from importlib.metadata import version, PackageNotFoundError
from typing import Dict, List, Tuple

# 색상 코드
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check_python_version() -> Tuple[bool, str]:
    """Python 버전 확인 (3.13 필요)"""
    required_version = (3, 13)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        return True, f"Python {current_version[0]}.{current_version[1]}"
    else:
        return False, f"Python {current_version[0]}.{current_version[1]} (3.13+ 필요)"


def check_package_version(package_name: str, min_version: str = None) -> Tuple[bool, str]:
    """패키지 설치 및 버전 확인"""
    try:
        installed_version = version(package_name)
        if min_version:
            # 간단한 버전 비교 (major.minor 기준)
            installed_parts = installed_version.split('.')
            required_parts = min_version.split('.')
            
            for i in range(min(len(installed_parts), len(required_parts))):
                try:
                    if int(installed_parts[i]) < int(required_parts[i]):
                        return False, f"{installed_version} (>= {min_version} 필요)"
                    elif int(installed_parts[i]) > int(required_parts[i]):
                        break
                except ValueError:
                    # 버전 파싱 실패시 설치된 것으로 간주
                    break
        
        return True, installed_version
    except PackageNotFoundError:
        return False, "미설치"


def check_freecad_availability() -> Tuple[bool, str]:
    """FreeCAD 설치 확인 (optional)"""
    try:
        import FreeCAD
        return True, f"FreeCAD {FreeCAD.Version()[0]}.{FreeCAD.Version()[1]}"
    except ImportError:
        # FreeCAD가 없어도 개발은 가능 (stubs 사용)
        return None, "미설치 (선택사항)"


def main():
    """메인 체크 함수"""
    print(f"\n{BOLD}=== FreeCAD Tool Calling Agent 호환성 체크 ==={RESET}\n")
    
    # 시스템 정보
    print(f"{BOLD}시스템 정보:{RESET}")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  아키텍처: {platform.machine()}")
    print()
    
    # Python 버전 체크
    print(f"{BOLD}Python 버전:{RESET}")
    py_ok, py_msg = check_python_version()
    status = f"{GREEN}✓{RESET}" if py_ok else f"{RED}✗{RESET}"
    print(f"  {status} {py_msg}")
    print()
    
    # 필수 패키지 체크
    print(f"{BOLD}필수 패키지:{RESET}")
    packages = {
        "openai": "1.44.0",
        "python-dotenv": "1.0.0",
        "pydantic": "2.7.0",
        "httpx": "0.25.0",
    }
    
    all_packages_ok = True
    for pkg, min_ver in packages.items():
        pkg_ok, pkg_msg = check_package_version(pkg, min_ver)
        status = f"{GREEN}✓{RESET}" if pkg_ok else f"{RED}✗{RESET}"
        print(f"  {status} {pkg}: {pkg_msg}")
        if not pkg_ok:
            all_packages_ok = False
    print()
    
    # 선택적 패키지 체크
    print(f"{BOLD}AI/ML 패키지 (학습용):{RESET}")
    ml_packages = {
        "unsloth": "2024.11",
        "torch": "2.0.0",
        "transformers": "4.40.0",
    }
    
    for pkg, min_ver in ml_packages.items():
        pkg_ok, pkg_msg = check_package_version(pkg, min_ver)
        if pkg_ok:
            status = f"{GREEN}✓{RESET}"
        elif pkg_msg == "미설치":
            status = f"{YELLOW}○{RESET}"
        else:
            status = f"{RED}✗{RESET}"
        print(f"  {status} {pkg}: {pkg_msg}")
    print()
    
    # MCP 및 데이터 수집 패키지
    print(f"{BOLD}MCP 및 데이터 수집:{RESET}")
    mcp_packages = {
        "fastmcp": "0.2.0",
        "openpipe": "4.0.0",
    }
    
    for pkg, min_ver in mcp_packages.items():
        pkg_ok, pkg_msg = check_package_version(pkg, min_ver)
        if pkg_ok:
            status = f"{GREEN}✓{RESET}"
        elif pkg_msg == "미설치":
            status = f"{YELLOW}○{RESET}"
        else:
            status = f"{RED}✗{RESET}"
        print(f"  {status} {pkg}: {pkg_msg}")
    print()
    
    # VL 모델용 패키지
    print(f"{BOLD}VL 모델용 패키지:{RESET}")
    vl_packages = {
        "pillow": "10.0.0",
    }
    
    for pkg, min_ver in vl_packages.items():
        pkg_ok, pkg_msg = check_package_version(pkg, min_ver)
        if pkg_ok:
            status = f"{GREEN}✓{RESET}"
        elif pkg_msg == "미설치":
            status = f"{YELLOW}○{RESET}"
        else:
            status = f"{RED}✗{RESET}"
        print(f"  {status} {pkg}: {pkg_msg}")
    print()
    
    # FreeCAD 체크
    print(f"{BOLD}FreeCAD:{RESET}")
    freecad_ok, freecad_msg = check_freecad_availability()
    if freecad_ok:
        status = f"{GREEN}✓{RESET}"
    elif freecad_ok is None:
        status = f"{YELLOW}○{RESET}"
    else:
        status = f"{RED}✗{RESET}"
    print(f"  {status} FreeCAD: {freecad_msg}")
    
    # FreeCAD stubs 체크
    stubs_ok, stubs_msg = check_package_version("freecad-stubs", "0.21.0")
    status = f"{GREEN}✓{RESET}" if stubs_ok else f"{YELLOW}○{RESET}"
    print(f"  {status} freecad-stubs: {stubs_msg}")
    print()
    
    # 최종 결과
    print(f"{BOLD}{'='*60}{RESET}")
    if py_ok and all_packages_ok:
        print(f"{GREEN}✓ 핵심 의존성이 모두 충족되었습니다!{RESET}")
        print(f"\n다음 단계: {BOLD}uv sync{RESET}로 나머지 패키지를 설치하세요.")
    else:
        print(f"{RED}✗ 일부 필수 패키지가 누락되었습니다.{RESET}")
        print(f"\n다음 명령으로 설치하세요: {BOLD}uv sync{RESET}")
    
    print(f"\n{YELLOW}참고:{RESET} ○ 표시된 패키지는 선택사항입니다.")
    print()


if __name__ == "__main__":
    main()

