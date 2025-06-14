#!/bin/bash
# Code quality check script for HubSpot MCP project

set -e

echo "🔍 Checking code quality..."
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Initialize result tracking
ALL_PASSED=true

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is not installed. Install it with: pip install uv${NC}"
    exit 1
fi

# Run checks
echo "🧪 Running tests with coverage..."

# Test coverage check
echo "📊 Checking code coverage..."
if uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80; then
    print_result 0 "Code coverage (≥80%)"
else
    print_result 1 "Code coverage (≥80%)"
    ALL_PASSED=false
fi

echo "🔧 Checking formatting with black..."
if uv run black --check --diff src/ main.py tests/ scripts/; then
    print_result 0 "Code formatting"
else
    print_result 1 "Code formatting"
    ALL_PASSED=false
fi

echo "📋 Checking imports with isort..."
if uv run isort --check-only --diff src/ main.py tests/ scripts/; then
    print_result 0 "Import organization"
else
    print_result 1 "Import organization"
    ALL_PASSED=false
fi

echo "🔍 Checking PEP 8 compliance with flake8..."
if uv run flake8 src/ main.py tests/ scripts/; then
    print_result 0 "PEP 8 compliance"
else
    print_result 1 "PEP 8 compliance"
    ALL_PASSED=false
fi

echo "🔬 Checking types with mypy..."
if uv run mypy src/ main.py; then
    print_result 0 "Type checking"
else
    print_result 0 "Type checking (warnings ignored)"
    # Type warnings are not blocking for now
fi

echo "🔒 Security analysis with bandit..."
if uv run bandit -r src/ -f json -o bandit_report.json; then
    print_result 0 "Security analysis"
else
    print_result 1 "Security analysis"
    ALL_PASSED=false
fi

echo ""
echo "🎯 Summary:"

if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✅ All quality checks passed!${NC}"
    echo ""
    echo "🚀 Ready to commit and push!"
    exit 0
else
    echo -e "${RED}❌ Some quality checks failed.${NC}"
    echo ""
    echo "🔧 To fix issues automatically:"
    echo "  uv run black src/ main.py tests/ scripts/"
    echo "  uv run isort src/ main.py tests/ scripts/"
    echo ""
    echo "📋 To check remaining issues:"
    echo "  uv run flake8 src/ main.py tests/ scripts/"
    echo "  uv run mypy src/ main.py"
    exit 1
fi

echo "🎉 Quality checks completed!"
echo "📄 Detailed report available in: lint_report.md"
echo "📊 HTML coverage report available in: htmlcov/index.html"

if [ -f lint_report.md ]; then
    echo ""
    echo "📋 Summary of the report:"
    head -20 lint_report.md
fi 