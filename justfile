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
    @echo "  just inspect-stdio  # Inspector with stdio server"
    @echo "  just inspect-sse    # Inspector with SSE server (auth)"
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
    @echo "  just docker-build   # Build & push Docker image (buildx)"
    @echo "  just docker-build-local # Build Docker image locally (no push)"
    @echo "  just clean          # Clean artifacts"
    @echo ""
    @echo "💡 Use 'just help-<category>' for detailed commands in each category"

# Run all tests with coverage reporting
test:
    uv run pytest --cov=src --cov-report=term-missing -v

# Run tests in watch mode (requires pytest-watch)
test-watch:
    uv run ptw -- --cov=src --cov-report=term-missing -v

# Run tests with HTML coverage report
test-html:
    uv run pytest --cov=src --cov-report=html --cov-report=term-missing -v
    @echo "Coverage report generated in htmlcov/index.html"

# Start the server in stdio mode (for Claude Desktop)
server-stdio:
    uv run hubspot-mcp-server --mode stdio

# Start the server in SSE mode on default port (8080)
server-sse:
    uv run hubspot-mcp-server --mode sse

# Start the server in SSE mode on custom host and port
server-sse-custom host="localhost" port="8080":
    uv run hubspot-mcp-server --mode sse --host {{host}} --port {{port}}

# Start MCP Inspector with specific HubSpot server (stdio mode)
inspect-stdio:
    @echo "🔍 Starting MCP Inspector with HubSpot stdio server..."
    npx @modelcontextprotocol/inspector@latest --config mcp.json --server hubspot-stdio

# Start MCP Inspector with SSE server (with authentication)
inspect-sse:
    @echo "🔍 Starting MCP Inspector with HubSpot SSE server (authenticated)..."
    npx @modelcontextprotocol/inspector@latest

# Install dependencies
install:
    uv sync

# Install development dependencies
install-dev:
    uv sync --dev

# Run code quality checks
lint:
    uv run black --check src tests
    uv run isort --check-only src tests
    uv run flake8 src tests

# Run rigorous static type checking over the full codebase
type-check:
    uv run mypy src

# Format code
format:
    uv run black src tests
    uv run isort src tests

# Run security checks
security:
    @mkdir -p reports
    uv run bandit -r src -f json -o reports/bandit_report.json
    uv run bandit -r src

# Clean cache and build artifacts
clean:
    @echo "🧹 Cleaning cache and build artifacts..."
    @find src tests -type f -name "*.pyc" -delete 2>/dev/null || true
    @find src tests -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @rm -rf .pytest_cache/ 2>/dev/null || true
    @rm -rf .coverage 2>/dev/null || true
    @rm -rf htmlcov/ 2>/dev/null || true
    @rm -f reports/*.json reports/*.html reports/*.txt 2>/dev/null || true
    @echo "✅ Cleanup completed"

# Run all quality checks (lint, test, security) with visual feedback
check:
    @echo ""
    @echo "\033[1;36m🚀 DÉMARRAGE DES VÉRIFICATIONS DE QUALITÉ\033[0m"
    @echo "\033[1;36m==========================================\033[0m"
    @echo ""
    @echo "\033[1;34m📋 Étape 1/5: Vérification du formatage du code\033[0m"
    @echo "\033[0;34m⏳ Vérification avec Black et isort...\033[0m"
    uv run black --check src tests
    uv run isort --check-only src tests
    @echo "\033[1;32m✅ Formatage vérifié avec succès\033[0m"
    @echo ""
    @echo "\033[1;34m🔍 Étape 2/5: Analyse statique et linting\033[0m"
    @echo "\033[0;34m⏳ Analyse avec flake8...\033[0m"
    uv run flake8 src tests
    @echo "\033[1;32m✅ Linting terminé avec succès\033[0m"
    @echo ""
    @echo "\033[1;34m🎯 Étape 3/5: Vérification des types statiques\033[0m"
    @echo "\033[0;34m⏳ Analyse avec mypy...\033[0m"
    uv run mypy src
    @echo "\033[1;32m✅ Vérification des types réussie\033[0m"
    @echo ""
    @echo "\033[1;34m🔒 Étape 4/5: Analyse de sécurité du code\033[0m"
    @echo "\033[0;34m⏳ Scan de sécurité avec bandit...\033[0m"
    @mkdir -p reports
    uv run bandit -r src -f json -o reports/bandit_report.json
    uv run bandit -r src
    @echo "\033[1;32m✅ Analyse de sécurité terminée\033[0m"
    @echo ""
    @echo "\033[1;34m🧪 Étape 5/5: Exécution des tests unitaires\033[0m"
    @echo "\033[0;34m⏳ Lancement des tests avec coverage...\033[0m"
    uv run pytest --cov=src --cov-report=term-missing -v
    @echo ""
    @echo "\033[1;32m🎉 TOUTES LES VÉRIFICATIONS SONT TERMINÉES AVEC SUCCÈS !\033[0m"
    @echo "\033[1;32m=====================================================\033[0m"
    @echo "\033[1;33m📊 Résumé: Formatage ✅ | Linting ✅ | Types ✅ | Sécurité ✅ | Tests ✅\033[0m"
    @echo ""

# Build the package
build:
    uv build

# Build Docker image using buildx (eliminates warnings)
docker-build:
    @echo "🐳 Building Docker image..."
    @if docker buildx version >/dev/null 2>&1; then \
        echo "✅ Using Docker buildx for warning-free builds..."; \
        if ! docker buildx ls | grep -q "multiarch"; then \
            echo "📋 Initializing buildx builder..."; \
            docker buildx create --name multiarch --use --bootstrap; \
        else \
            echo "📋 Using existing buildx builder..."; \
            docker buildx use multiarch; \
        fi; \
        echo "🔨 Building and pushing image with buildx..."; \
        docker buildx build \
            --platform linux/amd64 \
            --tag ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
            --push \
            .; \
        echo "✅ Docker image built and pushed successfully with buildx!"; \
    else \
        echo "⚠️  Docker buildx not available, using standard docker build..."; \
        echo "💡 Install docker-buildx-plugin for warning-free builds"; \
        echo "🔨 Building and pushing image..."; \
        docker build \
            --tag ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
            .; \
        docker push ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}; \
        echo "✅ Docker image built and pushed successfully!"; \
    fi

# Build Docker image locally (no push)
docker-build-local:
    @echo "🐳 Building Docker image locally..."
    @if docker buildx version >/dev/null 2>&1; then \
        echo "✅ Using Docker buildx for warning-free builds..."; \
        if ! docker buildx ls | grep -q "multiarch"; then \
            echo "📋 Initializing buildx builder..."; \
            docker buildx create --name multiarch --use --bootstrap; \
        else \
            echo "📋 Using existing buildx builder..."; \
            docker buildx use multiarch; \
        fi; \
        echo "🔨 Building image for local use with buildx..."; \
        docker buildx build \
            --platform linux/amd64 \
            --tag ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
            --load \
            .; \
        echo "✅ Docker image built locally with buildx!"; \
    else \
        echo "⚠️  Docker buildx not available, using standard docker build..."; \
        echo "💡 Install docker-buildx-plugin for warning-free builds"; \
        echo "🔨 Building image for local use..."; \
        docker build \
            --tag ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
            .; \
        echo "✅ Docker image built locally!"; \
    fi

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
    @echo ""
    @echo "🔍 Debugging:"
    @echo "  just inspect-stdio  # Direct stdio connection"
    @echo "  just inspect-sse    # Direct SSE connection (auth)"

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
    echo ""
    @echo "📊 Coverage requirements:"
    @echo "  - Minimum coverage: 90%"
    @echo "  - HTML report saved to htmlcov/"

# Show detailed build commands
help-build:
    @echo "📦 BUILD & DEPLOY COMMANDS:"
    @echo "  just build          # Build Python package"
    @echo "  just docker-build   # Build & push Docker image (buildx)"
    @echo "  just docker-build-local # Build Docker image locally (no push)"
    @echo "  just clean          # Clean cache and build artifacts"
    @echo ""
    @echo "🗂️ Artifacts:"
    @echo "  - Build output: dist/"
    @echo "  - Package info: *.egg-info/"
    @echo ""
    @echo "🐳 Docker commands require environment variables:"
    @echo "  - IMAGE_REGISTRY (e.g., rg.fr-par.scw.cloud/keltio-public)"
    @echo "  - IMAGE_NAME (e.g., hubspot-mcp-server)"
    @echo "  - IMAGE_TAG (e.g., 0.1.0)"
    @echo "  - REGISTRY_PASSWORD (for authentication)" 