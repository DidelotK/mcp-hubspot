# HubSpot MCP Server - Just Commands

# Default recipe to show available commands
default:
    @just --list

# Run all tests with coverage reporting
test:
    uv run pytest --cov=src --cov=main --cov-report=term-missing -v

# Run tests in watch mode (requires pytest-watch)
test-watch:
    uv run ptw -- --cov=src --cov=main --cov-report=term-missing -v

# Run tests with HTML coverage report
test-html:
    uv run pytest --cov=src --cov=main --cov-report=html --cov-report=term-missing -v
    @echo "Coverage report generated in htmlcov/index.html"

# Start the server in stdio mode (for Claude Desktop)
server-stdio:
    uv run python main.py --mode stdio

# Start the server in SSE mode on default port (8080)
server-sse:
    uv run python main.py --mode sse

# Start the server in SSE mode on custom host and port
server-sse-custom host="localhost" port="8080":
    uv run python main.py --mode sse --host {{host}} --port {{port}}

# Install dependencies
install:
    uv sync

# Install development dependencies
install-dev:
    uv sync --dev

# Run code quality checks
lint:
    uv run black --check src tests main.py
    uv run isort --check-only src tests main.py
    uv run flake8 src tests main.py

# Run rigorous static type checking over the full codebase
type-check:
    uv run mypy src/hubspot_mcp main.py --config-file mypy.ini

# Format code
format:
    uv run black src tests main.py
    uv run isort src tests main.py

# Run security checks
security:
    uv run bandit -r src main.py

# Clean cache and build artifacts
clean:
    rm -rf __pycache__ .pytest_cache .coverage htmlcov reports
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type d -name "__pycache__" -exec rm -rf {} +

# Run all quality checks (lint, test, security)
check: lint type-check test security

# Build the package
build:
    uv build

# Show project info
info:
    @echo "HubSpot MCP Server"
    @echo "=================="
    @echo "Python version: $(python --version)"
    @echo "UV version: $(uv --version)"
    @echo "Project dependencies:"
    @uv tree 