#!/bin/bash
# Install pre-commit hooks for code quality

set -e

echo "🔧 Installing pre-commit hooks..."

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for code quality checks

set -e

echo "🔍 Running pre-commit quality checks..."

# Format check
if ! uv run black --check src/ tests/ scripts/ 2>/dev/null; then
    echo "❌ Code formatting issues found. Run: uv run black src/ tests/ scripts/"
    exit 1
fi

# Import check
if ! uv run isort --check-only src/ tests/ scripts/ 2>/dev/null; then
    echo "❌ Import organization issues found. Run: uv run isort src/ tests/ scripts/"
    exit 1
fi

# Linting check
if ! uv run flake8 src/ tests/ scripts/ 2>/dev/null; then
    echo "❌ Linting issues found."
    echo "Run: uv run flake8 src/ tests/ scripts/"
    exit 1
fi

# Type checking
if ! uv run mypy src/ 2>/dev/null; then
    echo "⚠️ Type checking issues found (not blocking)"
fi

# Quick tests
if ! uv run pytest tests/unit/ --tb=short -q 2>/dev/null; then
    echo "❌ Unit tests failed"
    exit 1
fi

echo "✅ Pre-commit checks passed!"
EOF

# Make hook executable
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "📋 The hook will run the following checks:"
echo "  - Code formatting (black)"
echo "  - Import organization (isort)"
echo "  - Code linting (flake8)"
echo "  - Type checking (mypy)"
echo "  - Unit tests"
echo ""
echo "🚀 Your commits are now protected by quality checks!"
