#!/bin/bash

echo "==================================="
echo "AI Tutor System - 테스트 실행"
echo "==================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 카테고리
declare -A test_categories
test_categories["인증 시스템"]="test_auth.py"
test_categories["콘텐츠 관리"]="test_content.py"
test_categories["리포트 생성"]="test_reports.py"
test_categories["WebSocket/실시간"]="test_websocket.py"
test_categories["RAG 문서 관리"]="test_rag.py"
test_categories["통합 시나리오"]="test_integration.py"

# 전체 테스트 실행 함수
run_all_tests() {
    echo "전체 테스트를 실행합니다..."
    echo ""
    
    total_tests=0
    passed_tests=0
    failed_tests=0
    
    for category in "${!test_categories[@]}"; do
        echo -e "${YELLOW}[$category 테스트]${NC}"
        
        if python -m pytest tests/${test_categories[$category]} -v --tb=short; then
            echo -e "${GREEN}✓ $category 테스트 통과${NC}"
            ((passed_tests++))
        else
            echo -e "${RED}✗ $category 테스트 실패${NC}"
            ((failed_tests++))
        fi
        
        echo ""
        ((total_tests++))
    done
    
    echo "==================================="
    echo "테스트 결과 요약"
    echo "==================================="
    echo "전체: $total_tests"
    echo -e "${GREEN}통과: $passed_tests${NC}"
    echo -e "${RED}실패: $failed_tests${NC}"
    echo ""
}

# 개별 테스트 실행 함수
run_single_test() {
    category=$1
    if [[ -n "${test_categories[$category]}" ]]; then
        echo -e "${YELLOW}[$category 테스트 실행]${NC}"
        python -m pytest tests/${test_categories[$category]} -v --tb=short
    else
        echo -e "${RED}알 수 없는 테스트 카테고리: $category${NC}"
        echo "사용 가능한 카테고리:"
        for key in "${!test_categories[@]}"; do
            echo "  - $key"
        done
    fi
}

# 메인 실행 로직
if [ $# -eq 0 ]; then
    run_all_tests
else
    run_single_test "$1"
fi