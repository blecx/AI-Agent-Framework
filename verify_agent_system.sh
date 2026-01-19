#!/bin/bash
# verify_agent_system.sh - Complete system verification

set -e

echo "🔍 Custom AI Agent System - Complete Verification"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Test 1: Setup tests
echo "📋 Test 1: System Setup"
echo "----------------------"
if python3 tests/agents/test_setup.py; then
    echo -e "${GREEN}✅ Setup tests PASSED${NC}"
else
    echo -e "${RED}❌ Setup tests FAILED${NC}"
    FAILED=1
fi
echo ""

# Test 2: Export format tests
echo "📋 Test 2: Export Format Support"
echo "--------------------------------"
if python3 tests/agents/test_export_formats.py; then
    echo -e "${GREEN}✅ Format tests PASSED${NC}"
else
    echo -e "${RED}❌ Format tests FAILED${NC}"
    FAILED=1
fi
echo ""

# Test 3: Workflow agent dry-run
echo "📋 Test 3: Workflow Agent Dry-Run"
echo "---------------------------------"
if ./scripts/agents/workflow --issue 999 --dry-run > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Workflow agent dry-run PASSED${NC}"
else
    echo -e "${RED}❌ Workflow agent dry-run FAILED${NC}"
    FAILED=1
fi
echo ""

# Test 4: Extraction with real export (if available)
echo "📋 Test 4: Real Export Extraction"
echo "---------------------------------"
if [ -f "docs/chat/2026-01-18-issue25-prmerge-enhancements-complete-workflow.md" ]; then
    if ./scripts/extract_learnings.py --export docs/chat/2026-01-18-issue25-prmerge-enhancements-complete-workflow.md --no-merge > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Real export extraction PASSED${NC}"
    else
        echo -e "${RED}❌ Real export extraction FAILED${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠️  No real export found (skipped)${NC}"
fi
echo ""

# Test 5: Agent analysis
echo "📋 Test 5: Agent Analysis"
echo "-------------------------"
if ./scripts/train_agent.py --analyze-all > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Agent analysis PASSED${NC}"
else
    echo -e "${RED}❌ Agent analysis FAILED${NC}"
    FAILED=1
fi
echo ""

# Summary
echo "=================================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "System is ready for use!"
    echo ""
    echo "Next steps:"
    echo "  1. Train from existing issues:"
    echo "     ./scripts/extract_learnings.py --export docs/chat/*-issue*.md"
    echo "  2. Run on new issue:"
    echo "     ./scripts/agents/workflow --issue 26"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the errors above and fix before proceeding."
    echo ""
    exit 1
fi
