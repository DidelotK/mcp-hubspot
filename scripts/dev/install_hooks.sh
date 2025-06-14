#!/bin/bash
# Install Git hooks for code quality

set -e

echo "🔧 Installing Git hooks..."

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔍 Checking code quality before commit..."

# Exit on first error
set -e

# Run quick checks
echo "🔧 Checking formatting..."
if ! uv run black --check src/ main.py tests/ scripts/ 2>/dev/null; then
    echo "❌ Code formatting issues found. Run: uv run black src/ main.py tests/ scripts/"
    exit 1
fi

echo "📋 Checking imports..."
if ! uv run isort --check-only src/ main.py tests/ scripts/ 2>/dev/null; then
    echo "❌ Import organization issues found. Run: uv run isort src/ main.py tests/ scripts/"
    exit 1
fi

# flake8 check (non-blocking for pre-commit)
if ! uv run flake8 src/ main.py tests/ scripts/ 2>/dev/null; then
    echo "⚠️ Code style warnings found. Please check and fix if needed."
    echo "Run: uv run flake8 src/ main.py tests/ scripts/"
fi

echo "✅ Quality checks passed!"
EOF

# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "🧪 Running tests before push..."

# Exit on first error
set -e

# Run full test suite
if ! uv run pytest --cov=src --cov-report=term-missing; then
    echo "❌ Tests failed. Please fix before pushing."
    exit 1
fi

echo "✅ All tests passed!"
EOF

# Make hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push

echo "✅ Git hooks installed successfully!"
echo ""
echo "📋 Hooks installed:"
echo "  - pre-commit: Format and style checking"
echo "  - pre-push: Full test suite"
echo ""
echo "💡 To bypass hooks temporarily:"
echo "  git commit --no-verify"
echo "  git push --no-verify" 