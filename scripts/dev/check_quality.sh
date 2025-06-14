#!/bin/bash
# Quality check script for the HubSpot MCP Server
# Performs comprehensive code quality checks: formatting, imports, linting, type checking, and testing

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emoji for better visual feedback
SUCCESS="✅"
FAILURE="❌"
WARNING="⚠️"
INFO="ℹ️"

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ERRORS=0
WARNINGS=0

# Initialize log file
LOG_FILE="$PROJECT_DIR/quality_check.log"
echo "Quality Check Report - $(date)" > "$LOG_FILE"

# Function to log and display messages
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    echo -e "$message"
}

# Function to run a command and capture output
run_check() {
    local check_name="$1"
    local command="$2"
    local show_output="$3"
    
    log_message "INFO" "${BLUE}🔍 Running $check_name...${NC}"
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        log_message "SUCCESS" "${GREEN}$SUCCESS $check_name passed${NC}"
        return 0
    else
        log_message "ERROR" "${RED}$FAILURE $check_name failed${NC}"
        if [ "$show_output" = "true" ]; then
            echo -e "${YELLOW}📄 Error details:${NC}"
            tail -n 20 "$LOG_FILE" | grep -E "(error|Error|ERROR|failed|Failed|FAILED)" || true
        fi
        ((ERRORS++))
        return 1
    fi
}

# Main function
main() {
    log_message "INFO" "${BLUE}🚀 Starting comprehensive quality checks...${NC}"
    
    # Navigate to project directory
    cd "$PROJECT_DIR"
    
    # Check 1: Code formatting with black
    if run_check "Code formatting (black)" "uv run black --check --diff src/ tests/ scripts/" "true"; then
        log_message "SUCCESS" "${GREEN}$SUCCESS Code formatting is correct${NC}"
    else
        log_message "WARNING" "${YELLOW}$WARNING Code formatting issues found${NC}"
        ((WARNINGS++))
    fi
    
    # Check 2: Import organization with isort
    if run_check "Import organization (isort)" "uv run isort --check-only --diff src/ tests/ scripts/" "true"; then
        log_message "SUCCESS" "${GREEN}$SUCCESS Import organization is correct${NC}"
    else
        log_message "WARNING" "${YELLOW}$WARNING Import organization issues found${NC}"
        ((WARNINGS++))
    fi
    
    # Check 3: Code linting with flake8
    if run_check "Code linting (flake8)" "uv run flake8 src/ tests/ scripts/" "true"; then
        log_message "SUCCESS" "${GREEN}$SUCCESS Code linting passed${NC}"
    else
        log_message "ERROR" "${RED}$FAILURE Code linting failed${NC}"
    fi
    
    # Check 4: Type checking with mypy
    if run_check "Type checking (mypy)" "uv run mypy src/" "true"; then
        log_message "SUCCESS" "${GREEN}$SUCCESS Type checking passed${NC}"
    else
        log_message "ERROR" "${RED}$FAILURE Type checking failed${NC}"
    fi
    
    # Check 5: Security scanning with bandit
    if run_check "Security scanning (bandit)" "uv run bandit -r src/ -f json" "false"; then
        log_message "SUCCESS" "${GREEN}$SUCCESS Security scanning passed${NC}"
    else
        log_message "WARNING" "${YELLOW}$WARNING Security issues found${NC}"
        ((WARNINGS++))
    fi
    
    # Check 6: Unit tests with coverage
    if run_check "Unit tests with coverage" "uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90" "true"; then
        log_message "SUCCESS" "${GREEN}$SUCCESS All tests passed with adequate coverage${NC}"
    else
        log_message "ERROR" "${RED}$FAILURE Tests failed or coverage insufficient${NC}"
    fi
    
    # Final report
    echo ""
    log_message "INFO" "${BLUE}📊 Quality Check Summary${NC}"
    log_message "INFO" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        log_message "SUCCESS" "${GREEN}$SUCCESS All quality checks passed! ✨${NC}"
        exit 0
    elif [ $ERRORS -eq 0 ]; then
        log_message "WARNING" "${YELLOW}$WARNING All critical checks passed, but $WARNINGS warnings found${NC}"
        echo -e "${YELLOW}$INFO Consider addressing the warnings for better code quality${NC}"
        exit 0
    else
        log_message "ERROR" "${RED}$FAILURE Quality checks failed with $ERRORS errors and $WARNINGS warnings${NC}"
        echo ""
        echo -e "${RED}🔧 To fix formatting and import issues, run:${NC}"
        echo "  uv run black src/ tests/ scripts/"
        echo "  uv run isort src/ tests/ scripts/"
        echo ""
        echo -e "${RED}🔧 To fix linting issues, run:${NC}"
        echo "  uv run flake8 src/ tests/ scripts/"
        echo "  uv run mypy src/"
        echo ""
        echo -e "${BLUE}📋 Full report available in: $LOG_FILE${NC}"
        exit 1
    fi
}

# Run main function
main "$@" 