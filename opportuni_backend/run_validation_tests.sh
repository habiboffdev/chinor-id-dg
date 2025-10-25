#!/bin/bash
# 🔴 CRITICAL: Run Application Validation Tests
# Quick test runner for application validation

echo "🧪 Application Validation Test Suite"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Running application validation tests...${NC}"
echo ""

# Run tests with verbose output
python manage.py test apps.applications.tests_validation --verbosity=2

TEST_EXIT_CODE=$?

echo ""
echo "======================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests PASSED!${NC}"
    echo ""
    echo -e "${GREEN}Validation is working correctly:${NC}"
    echo "  ✅ Multi-language support (Cyrillic, Chinese, Arabic, Emoji)"
    echo "  ✅ Transaction integrity (rollback on failure)"
    echo "  ✅ Malformed data handling (SQL injection, XSS, etc.)"
    echo "  ✅ Edge cases (deleted questions, concurrency, etc.)"
    echo "  ✅ Basic validation (required questions, profile requirements)"
    echo ""
    echo -e "${GREEN}🚀 READY FOR DEPLOYMENT${NC}"
else
    echo -e "${RED}❌ Some tests FAILED!${NC}"
    echo ""
    echo -e "${RED}DO NOT DEPLOY until all tests pass${NC}"
    echo ""
    echo "To see detailed failures, run:"
    echo "  python manage.py test apps.applications.tests_validation -v 2"
fi

echo ""

exit $TEST_EXIT_CODE
