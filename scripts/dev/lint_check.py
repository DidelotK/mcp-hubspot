#!/usr/bin/env python3
"""
Comprehensive code quality check script for the HubSpot MCP Server.
Runs formatting, import organization, linting, type checking, security analysis, and tests.
"""

import subprocess
import sys
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def run_command(command: str, description: str) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"{Colors.BLUE}🔍 {description}...{Colors.NC}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ {description} passed{Colors.NC}")
            return True, result.stdout
        else:
            print(f"{Colors.RED}❌ {description} failed{Colors.NC}")
            if result.stderr:
                print(f"{Colors.YELLOW}Error details:{Colors.NC}")
                print(result.stderr)
            return False, result.stderr
            
    except Exception as e:
        print(f"{Colors.RED}❌ {description} failed with exception: {e}{Colors.NC}")
        return False, str(e)

def main():
    """Main entry point for quality checks."""
    print(f"{Colors.BLUE}🚀 Starting comprehensive code quality checks...{Colors.NC}\n")
    
    project_root = Path(__file__).parent.parent.parent
    
    # Change to project directory
    import os
    os.chdir(project_root)
    
    checks = [
        ("uv run black --check --diff src/ tests/ scripts/", "Code formatting (black)"),
        ("uv run isort --check-only --diff src/ tests/ scripts/", "Import organization (isort)"),
        ("uv run flake8 src/ tests/ scripts/", "Code linting (flake8)"),
        ("uv run mypy src/", "Type checking (mypy)"),
        ("uv run bandit -r src/ -f json", "Security analysis (bandit)"),
        ("uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90", "Unit tests with coverage"),
    ]
    
    results = []
    for command, description in checks:
        success, output = run_command(command, description)
        results.append((success, description, output))
    
    # Summary
    print(f"\n{Colors.BLUE}📊 Quality Check Summary{Colors.NC}")
    print(f"{Colors.BLUE}{'='*40}{Colors.NC}")
    
    passed = sum(1 for success, _, _ in results if success)
    total = len(results)
    
    for success, description, _ in results:
        status = f"{Colors.GREEN}✅" if success else f"{Colors.RED}❌"
        print(f"{status} {description}{Colors.NC}")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} checks passed{Colors.NC}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All quality checks passed! ✨{Colors.NC}")
        return 0
    else:
        print(f"{Colors.RED}❌ Some quality checks failed{Colors.NC}")
        print(f"\n{Colors.YELLOW}🔧 To fix formatting and import issues, run:{Colors.NC}")
        print("uv run black src/ tests/ scripts/")
        print("uv run isort src/ tests/ scripts/")
        print(f"\n{Colors.YELLOW}🔧 To fix linting issues, run:{Colors.NC}")
        print("uv run flake8 src/ tests/ scripts/")
        print("uv run mypy src/")
        return 1

if __name__ == "__main__":
    sys.exit(main())
