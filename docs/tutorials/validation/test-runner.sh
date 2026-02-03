#!/bin/bash
# Tutorial Validation Test Runner
# Executes all tutorial E2E tests and generates validation report

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
REPORT_FILE="$PROJECT_ROOT/docs/tutorials/VALIDATION-REPORT.md"
HTML_REPORT="$PROJECT_ROOT/docs/tutorials/VALIDATION-REPORT.html"
LOG_FILE="/tmp/tutorial-validation-$(date +%Y%m%d-%H%M%S).log"

# Test configuration
PYTEST_OPTS="-v --tb=short --maxfail=5"
TEST_DIR="$PROJECT_ROOT/tests/e2e/tutorial"

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log_error "ERROR: $1"
    exit 1
}

# Cleanup function
cleanup() {
    local exit_code=$?
    log "Cleaning up test environment..."
    
    # Stop Docker services
    cd "$PROJECT_ROOT"
    docker compose down 2>/dev/null || true
    
    # Clean test projects
    if [ -d "$PROJECT_ROOT/projectDocs" ]; then
        find "$PROJECT_ROOT/projectDocs" -maxdepth 1 -name "TEST-*" -type d -exec rm -rf {} \; 2>/dev/null || true
    fi
    
    log "Cleanup complete"
    exit $exit_code
}

trap cleanup EXIT INT TERM

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check for required commands
    for cmd in docker pytest python3 jq; do
        if ! command -v $cmd &> /dev/null; then
            error_exit "Required command not found: $cmd"
        fi
    done
    
    # Check for Python venv
    if [ ! -d "$PROJECT_ROOT/.venv" ]; then
        log_warning "Virtual environment not found. Run ./setup.sh first"
    fi
    
    # Check Docker is running
    if ! docker info &> /dev/null; then
        error_exit "Docker is not running. Please start Docker and try again"
    fi
    
    log_success "Prerequisites check passed"
}

# Clean environment
clean_environment() {
    log "Cleaning test environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing services
    log "Stopping Docker services..."
    docker compose down -v 2>&1 | tee -a "$LOG_FILE" || true
    
    # Clean project docs
    log "Cleaning test project directories..."
    if [ -d "$PROJECT_ROOT/projectDocs" ]; then
        mkdir -p "$PROJECT_ROOT/projectDocs"  # Ensure it exists
        find "$PROJECT_ROOT/projectDocs" -maxdepth 1 -name "TEST-*" -type d -exec rm -rf {} \; 2>/dev/null || true
    fi
    
    log_success "Environment cleaned"
}

# Start services
start_services() {
    log "Starting Docker services..."
    
    cd "$PROJECT_ROOT"
    
    # Start services
    docker compose up -d 2>&1 | tee -a "$LOG_FILE" || error_exit "Failed to start Docker services"
    
    log "Waiting for services to be ready..."
    sleep 10
    
    # Wait for API health
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -sf http://localhost:8000/health &> /dev/null; then
            log_success "API is healthy"
            return 0
        fi
        log "Waiting for API... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error_exit "API failed to become healthy after $max_attempts attempts"
}

# Run tutorial tests
run_tests() {
    log "Running tutorial validation tests..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment if exists
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    # Create temp file for pytest output
    local pytest_output="/tmp/pytest-output-$$.txt"
    local pytest_json="/tmp/pytest-result-$$.json"
    
    # Run pytest with JSON report
    log "Executing pytest..."
    if pytest "$TEST_DIR" $PYTEST_OPTS \
        --json-report --json-report-file="$pytest_json" \
        --html="$HTML_REPORT" --self-contained-html \
        2>&1 | tee "$pytest_output" "$LOG_FILE"; then
        log_success "All tests passed"
        local test_result=0
    else
        log_error "Some tests failed"
        local test_result=1
    fi
    
    # Parse results
    local total_tests=$(grep -c "PASSED\|FAILED\|SKIPPED\|ERROR" "$pytest_output" || echo "0")
    local passed_tests=$(grep -c "PASSED" "$pytest_output" || echo "0")
    local failed_tests=$(grep -c "FAILED" "$pytest_output" || echo "0")
    local skipped_tests=$(grep -c "SKIPPED" "$pytest_output" || echo "0")
    
    log "Test Results: $passed_tests passed, $failed_tests failed, $skipped_tests skipped (total: $total_tests)"
    
    # Generate markdown report
    generate_report "$test_result" "$total_tests" "$passed_tests" "$failed_tests" "$skipped_tests" "$pytest_output"
    
    # Cleanup
    rm -f "$pytest_output" "$pytest_json"
    
    return $test_result
}

# Generate validation report
generate_report() {
    local test_result=$1
    local total=$2
    local passed=$3
    local failed=$4
    local skipped=$5
    local pytest_output=$6
    
    log "Generating validation report..."
    
    cat > "$REPORT_FILE" << EOF
# Tutorial Validation Report

**Generated:** $(date +'%Y-%m-%d %H:%M:%S')  
**Status:** $([ $test_result -eq 0 ] && echo "✅ ALL PASSED" || echo "❌ SOME FAILED")

## Summary

- **Total Tests:** $total
- **Passed:** $passed ✅
- **Failed:** $failed ❌
- **Skipped:** $skipped ⊙

**Pass Rate:** $(awk "BEGIN {printf \"%.1f\", ($passed/$total)*100}")%

## Test Results by Module

EOF
    
    # Extract test results from pytest output
    log "Parsing test results..."
    
    # TUI Basics Tests
    cat >> "$REPORT_FILE" << EOF
### TUI Basics Tutorials

| Test | Status | Duration |
|------|--------|----------|
EOF
    
    grep "test_tui_basics" "$pytest_output" | while read -r line; do
        if echo "$line" | grep -q "PASSED"; then
            status="✅ PASS"
        elif echo "$line" | grep -q "FAILED"; then
            status="❌ FAIL"
        elif echo "$line" | grep -q "SKIPPED"; then
            status="⊙ SKIP"
        else
            status="❓ UNKNOWN"
        fi
        
        test_name=$(echo "$line" | sed 's/.*::\(test_[^ ]*\).*/\1/')
        duration=$(echo "$line" | grep -oP '\d+\.\d+s' || echo "N/A")
        
        echo "| $test_name | $status | $duration |" >> "$REPORT_FILE"
    done
    
    # GUI Basics Tests
    cat >> "$REPORT_FILE" << EOF

### GUI Basics Tutorials

| Test | Status | Duration |
|------|--------|----------|
EOF
    
    grep "test_gui_basics" "$pytest_output" | while read -r line; do
        if echo "$line" | grep -q "PASSED"; then
            status="✅ PASS"
        elif echo "$line" | grep -q "FAILED"; then
            status="❌ FAIL"
        else
            status="⊙ SKIP"
        fi
        
        test_name=$(echo "$line" | sed 's/.*::\(test_[^ ]*\).*/\1/')
        duration=$(echo "$line" | grep -oP '\d+\.\d+s' || echo "N/A")
        
        echo "| $test_name | $status | $duration |" >> "$REPORT_FILE"
    done
    
    # Advanced Workflows Tests
    cat >> "$REPORT_FILE" << EOF

### Advanced Workflows Tutorials

| Test | Status | Duration |
|------|--------|----------|
EOF
    
    grep "test_advanced_workflows" "$pytest_output" | while read -r line; do
        if echo "$line" | grep -q "PASSED"; then
            status="✅ PASS"
        elif echo "$line" | grep -q "FAILED"; then
            status="❌ FAIL"
        else
            status="⊙ SKIP"
        fi
        
        test_name=$(echo "$line" | sed 's/.*::\(test_[^ ]*\).*/\1/')
        duration=$(echo "$line" | grep -oP '\d+\.\d+s' || echo "N/A")
        
        echo "| $test_name | $status | $duration |" >> "$REPORT_FILE"
    done
    
    # Failure details
    if [ $failed -gt 0 ]; then
        cat >> "$REPORT_FILE" << EOF

## Failure Details

EOF
        
        grep -A 10 "FAILED" "$pytest_output" | head -50 >> "$REPORT_FILE" || true
    fi
    
    # Footer
    cat >> "$REPORT_FILE" << EOF

## How to Use This Report

1. **Pass Rate < 90%:** Investigate failed tests immediately
2. **Failed Tests:** Check error details above and fix issues
3. **Skipped Tests:** Review if tests should be enabled
4. **HTML Report:** Open [VALIDATION-REPORT.html](VALIDATION-REPORT.html) for detailed view

## Re-running Validation

\`\`\`bash
cd docs/tutorials/validation
./test-runner.sh
\`\`\`

## Manual Tutorial Validation

For manual validation of tutorial content:
1. Follow each tutorial step-by-step
2. Compare actual output with expected output in \`expected-outputs/\`
3. Document discrepancies in GitHub issues
4. Update tutorials or expected outputs as needed

---

*Report generated by: \`docs/tutorials/validation/test-runner.sh\`*  
*Log file: \`$LOG_FILE\`*
EOF
    
    log_success "Validation report generated: $REPORT_FILE"
    
    if [ -f "$HTML_REPORT" ]; then
        log_success "HTML report generated: $HTML_REPORT"
    fi
}

# Print summary
print_summary() {
    local test_result=$1
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  TUTORIAL VALIDATION COMPLETE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "  Report:    $REPORT_FILE"
    if [ -f "$HTML_REPORT" ]; then
        echo "  HTML:      $HTML_REPORT"
    fi
    echo "  Log:       $LOG_FILE"
    echo ""
    
    if [ $test_result -eq 0 ]; then
        echo -e "  Status:    ${GREEN}✓ ALL TESTS PASSED${NC}"
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        return 0
    else
        echo -e "  Status:    ${RED}✗ SOME TESTS FAILED${NC}"
        echo ""
        echo "  Review the report for details and fix failing tests."
        echo "═══════════════════════════════════════════════════════════════"
        return 1
    fi
}

# Main execution
main() {
    echo "═══════════════════════════════════════════════════════════════"
    echo "  TUTORIAL VALIDATION SUITE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    check_prerequisites
    clean_environment
    start_services
    
    local test_result=0
    run_tests || test_result=$?
    
    print_summary $test_result
    
    return $test_result
}

# Run main
main "$@"
