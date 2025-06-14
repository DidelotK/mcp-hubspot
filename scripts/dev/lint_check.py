#!/usr/bin/env python3
"""
Script to check code quality and generate a report
for Pull Request comments.
"""

import os
import subprocess
import sys


def run_command(command):
    """Execute a command and return exit code, stdout and stderr."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def check_black():
    """Check formatting with Black."""
    print("🔍 Checking formatting with Black...")
    return_code, stdout, stderr = run_command(
        "uv run black --check --diff src/ main.py tests/ scripts/"
    )

    if return_code == 0:
        print("✅ Black formatting: OK")
        return True, ""
    else:
        print("❌ Black formatting: Issues found")
        return False, f"**Black formatting issues:**\n```\n{stdout}\n{stderr}\n```\n"


def check_isort():
    """Check import organization with isort."""
    print("🔍 Checking imports with isort...")
    return_code, stdout, stderr = run_command(
        "uv run isort --check-only --diff src/ main.py tests/ scripts/"
    )

    if return_code == 0:
        print("✅ isort imports: OK")
        return True, ""
    else:
        print("❌ isort imports: Issues found")
        return False, f"**Import organization issues:**\n```\n{stdout}\n{stderr}\n```\n"


def check_flake8():
    """Check PEP 8 compliance with flake8."""
    print("🔍 Checking PEP 8 with flake8...")
    return_code, stdout, stderr = run_command(
        "uv run flake8 src/ main.py tests/ scripts/"
    )

    if return_code == 0:
        print("✅ flake8 PEP 8: OK")
        return True, ""
    else:
        print("❌ flake8 PEP 8: Issues found")
        return False, f"**PEP 8 issues:**\n```\n{stdout}\n{stderr}\n```\n"


def check_mypy():
    """Check types with mypy."""
    print("🔍 Checking types with mypy...")
    return_code, stdout, stderr = run_command(
        "cd src && uv run mypy hubspot_mcp/ --config-file=../mypy.ini"
    )

    if return_code == 0:
        print("✅ mypy types: OK")
        return True, ""
    else:
        print("❌ mypy types: Issues found")
        return False, f"**Type checking issues:**\n```\n{stdout}\n{stderr}\n```\n"


def main():
    """Main function to execute all checks."""
    print("🚀 Starting code quality checks...\n")

    all_passed = True
    report = "## 📊 Code Quality Report\n\n"

    # Execute all checks
    checks = [
        ("Black Formatting", check_black),
        ("Import Organization (isort)", check_isort),
        ("PEP 8 Compliance (flake8)", check_flake8),
        ("Type Checking (mypy)", check_mypy),
    ]

    issues = []

    for check_name, check_func in checks:
        passed, error_details = check_func()
        if passed:
            report += f"✅ **{check_name}**: OK\n"
        else:
            all_passed = False
            report += f"❌ **{check_name}**: Issues found\n"
            issues.append(error_details)
        print()  # Empty line for readability

    # Generate final report
    if all_passed:
        report += "\nAll code quality checks passed!\n\n"
        print("🎉 All quality checks passed!")
    else:
        report += "\nSome quality checks failed. Please fix the following issues:\n\n"
        for issue in issues:
            report += issue + "\n"

        # Add correction instructions
        report += "### 🔧 How to fix:\n"
        report += "```bash\n"
        report += "# Auto-fix formatting and imports\n"
        report += "uv run black src/ main.py tests/ scripts/\n"
        report += "uv run isort src/ main.py tests/ scripts/\n\n"
        report += "# Check remaining issues\n"
        report += "uv run flake8 src/ main.py tests/ scripts/\n"
        report += "uv run mypy src/ main.py\n"
        report += "```\n"

    # Save report for GitHub
    os.makedirs("reports", exist_ok=True)
    with open("lint_report.md", "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to lint_report.md")

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
