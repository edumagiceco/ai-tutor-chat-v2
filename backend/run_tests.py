#!/usr/bin/env python3
"""
AI Tutor System - 테스트 실행기
"""
import subprocess
import sys
from typing import Dict, List

# 색상 코드
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color


# 테스트 카테고리
test_categories = {
    "인증 시스템": "test_auth.py",
    "콘텐츠 관리": "test_content.py",
    "리포트 생성": "test_reports.py",
    "WebSocket/실시간": "test_websocket.py",
    "RAG 문서 관리": "test_rag.py",
    "통합 시나리오": "test_integration.py"
}


def run_single_test(category: str, test_file: str) -> bool:
    """단일 테스트 실행"""
    print(f"\n{YELLOW}[{category} 테스트]{NC}")
    
    cmd = [sys.executable, "-m", "pytest", f"tests/{test_file}", "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"{GREEN}✓ {category} 테스트 통과{NC}")
        return True
    else:
        print(f"{RED}✗ {category} 테스트 실패{NC}")
        return False


def run_all_tests():
    """전체 테스트 실행"""
    print("===================================")
    print("AI Tutor System - 테스트 실행")
    print("===================================")
    print("\n전체 테스트를 실행합니다...")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for category, test_file in test_categories.items():
        if run_single_test(category, test_file):
            passed_tests += 1
        else:
            failed_tests += 1
        total_tests += 1
    
    print("\n===================================")
    print("테스트 결과 요약")
    print("===================================")
    print(f"전체: {total_tests}")
    print(f"{GREEN}통과: {passed_tests}{NC}")
    print(f"{RED}실패: {failed_tests}{NC}")
    print()


def run_category_test(category: str):
    """특정 카테고리 테스트 실행"""
    if category in test_categories:
        print(f"\n{YELLOW}[{category} 테스트 실행]{NC}")
        test_file = test_categories[category]
        cmd = [sys.executable, "-m", "pytest", f"tests/{test_file}", "-v", "--tb=short"]
        subprocess.run(cmd)
    else:
        print(f"{RED}알 수 없는 테스트 카테고리: {category}{NC}")
        print("사용 가능한 카테고리:")
        for key in test_categories:
            print(f"  - {key}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_all_tests()
    else:
        run_category_test(sys.argv[1])