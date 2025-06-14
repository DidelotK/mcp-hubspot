# HubSpot MCP Server - Just Commands

# Show organized command menu
default:
    @echo "🚀 HubSpot MCP Server - Available Commands"
    @echo "=========================================="
    @echo ""
    @echo "📋 HELP & SETUP:"
    @echo "  just help-setup     # Show setup commands"
    @echo "  just install        # Install dependencies" 
    @echo "  just install-dev    # Install development dependencies"
    @echo "  just info           # Show project info"
    @echo ""
    @echo "📱 CLAUDE DESKTOP:"
    @echo "  just help-claude    # Show Claude Desktop commands"
    @echo "  just setup-claude   # Setup Claude Desktop configuration"
    @echo "  just start-claude   # Start Claude Desktop"
    @echo "  just kill-claude    # Kill Claude Desktop processes"
    @echo "  just diagnose-mcp   # Quick diagnostic"
    @echo "  just logs-claude    # Show logs"
    @echo ""
    @echo "⚙️ MCP SERVER:"
    @echo "  just help-mcp       # Show MCP server commands"
    @echo "  just server-stdio   # Start server (stdio mode)"
    @echo "  just server-sse     # Start server (SSE mode)"
    @echo "  just test-mcp       # Test MCP configuration"
    @echo ""
    @echo "🛠️ DEVELOPMENT:"
    @echo "  just help-dev       # Show development commands"
    @echo "  just format         # Format code"
    @echo "  just lint           # Run linting"
    @echo "  just type-check     # Type checking"
    @echo "  just check          # All quality checks"
    @echo ""
    @echo "🧪 TESTING:"
    @echo "  just help-test      # Show testing commands"
    @echo "  just test           # Run tests"
    @echo "  just test-watch     # Run tests in watch mode"
    @echo "  just test-html      # Tests with HTML report"
    @echo ""
    @echo "📦 BUILD & DEPLOY:"
    @echo "  just help-build     # Show build commands"
    @echo "  just build          # Build package"
    @echo "  just clean          # Clean artifacts"
    @echo ""
    @echo "💡 Use 'just help-<category>' for detailed commands in each category"

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

# Run the basic MCP client example (requires HUBSPOT_API_KEY env var)
example-basic:
    uv run python examples/basic/test_mcp_client.py

# Kill all Claude Desktop processes
kill-claude:
    @echo "🔍 Terminating all Claude Desktop processes..."
    ./scripts/claude/kill_claude.sh

# Setup Claude Desktop configuration dynamically
setup-claude:
    @echo "🔧 Setting up Claude Desktop configuration..."
    ./scripts/claude/setup_claude_config.sh

# Test MCP HubSpot configuration
test-mcp:
    @echo "🧪 Testing MCP HubSpot configuration..."
    ./scripts/mcp/test_mcp_config.sh

# Start Claude Desktop (after killing existing processes)
start-claude:
    @echo "🚀 Starting Claude Desktop..."
    @./scripts/claude/kill_claude.sh >/dev/null 2>&1 || true
    @sleep 1
    @claude-desktop &
    @echo "✅ Claude Desktop started in background"

# Show Claude Desktop logs (MCP server logs)
logs-claude:
    @echo "📋 Claude Desktop MCP Logs:"
    @echo "=========================="
    @tail -f ~/.config/Claude/logs/mcp*.log

# Quick diagnostic of MCP server status
diagnose-mcp:
    @echo "🔍 Running MCP diagnostic..."
    ./scripts/claude/diagnose_mcp.sh

# =====================================
# HELP MENUS FOR EACH CATEGORY
# =====================================

# Show detailed setup commands
help-setup:
    @echo "📋 SETUP COMMANDS:"
    @echo "  just install        # Install dependencies using uv"
    @echo "  just install-dev    # Install dev dependencies + pre-commit hooks"
    @echo "  just info           # Show project information and status"
    @echo ""
    @echo "📝 First time setup:"
    @echo "  1. just install-dev"
    @echo "  2. Set HUBSPOT_API_KEY environment variable"
    @echo "  3. just setup-claude"

# Show detailed Claude Desktop commands  
help-claude:
    @echo "📱 CLAUDE DESKTOP COMMANDS:"
    @echo "  just setup-claude   # Setup Claude config with HubSpot MCP"
    @echo "  just start-claude   # Kill existing + start Claude Desktop"
    @echo "  just kill-claude    # Kill all Claude Desktop processes"
    @echo "  just diagnose-mcp   # Diagnose MCP server connection"
    @echo "  just logs-claude    # Show Claude Desktop logs"
    @echo ""
    @echo "🔄 Typical workflow:"
    @echo "  1. just setup-claude"
    @echo "  2. just start-claude"
    @echo "  3. just diagnose-mcp (if issues)"

# Show detailed MCP server commands
help-mcp:
    @echo "⚙️ MCP SERVER COMMANDS:"
    @echo "  just server-stdio   # Start in stdio mode (for Claude Desktop)"
    @echo "  just server-sse     # Start in SSE mode on port 8080"
    @echo "  just server-sse-custom HOST PORT  # Custom host/port"
    @echo "  just test-mcp       # Test MCP configuration"
    @echo "  just example-basic  # Run basic example client"
    @echo ""
    @echo "🔧 Environment setup:"
    @echo "  export HUBSPOT_API_KEY='your-key-here'"

# Show detailed development commands
help-dev:
    @echo "🛠️ DEVELOPMENT COMMANDS:"
    @echo "  just format         # Format code with black + isort"
    @echo "  just lint           # Run linting (ruff + custom scripts)"
    @echo "  just type-check     # Static type checking with mypy"
    @echo "  just security       # Security scan with bandit"
    @echo "  just check          # Run ALL quality checks"
    @echo ""
    @echo "⚡ Quick development:"
    @echo "  just check  # Runs format + lint + type-check + test + security"

# Show detailed testing commands
help-test:
    @echo "🧪 TESTING COMMANDS:"
    @echo "  just test           # Run tests with coverage report"
    @echo "  just test-watch     # Run tests in watch mode"
    @echo "  just test-html      # Generate HTML coverage report"
    @echo ""
    @echo "📊 Coverage requirements:"
    @echo "  - Minimum coverage: 90%"
    @echo "  - HTML report saved to htmlcov/"

# Show detailed build commands
help-build:
    @echo "📦 BUILD & DEPLOY COMMANDS:"
    @echo "  just build          # Build Python package"
    @echo "  just clean          # Clean cache and build artifacts"
    @echo ""
    @echo "🗂️ Artifacts:"
    @echo "  - Build output: dist/"
    @echo "  - Package info: *.egg-info/" 