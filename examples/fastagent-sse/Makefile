# HubSpot FastAgent SSE Example Makefile
#
# This Makefile provides convenient commands for running the FastAgent SSE example.

# Variables
PYTHON_VERSION := 3.12
UV := uv
PROJECT_ROOT := ../..

# Default target
.PHONY: help
help:
	@echo "🎯 HubSpot FastAgent SSE Example"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@echo "  setup      - Initial setup (copy secrets template)"
	@echo "  test       - Test configuration and connections"
	@echo "  run        - Run FastAgent directly"
	@echo "  launch     - Launch with automatic MCP server startup"
	@echo "  server     - Start only the MCP server in SSE mode"
	@echo "  clean      - Clean up temporary files"
	@echo "  install    - Install dependencies"
	@echo ""
	@echo "Example workflow:"
	@echo "  1. make setup      # Copy secrets template"
	@echo "  2. Edit fastagent.secrets.yaml with your keys"
	@echo "  3. make test       # Validate configuration"
	@echo "  4. make launch     # Run everything"

# Initial setup
.PHONY: setup
setup:
	@echo "🔧 Setting up FastAgent SSE example..."
	@if [ ! -f fastagent.secrets.yaml ]; then \
		cp fastagent.secrets.example.yaml fastagent.secrets.yaml; \
		echo "✅ Created fastagent.secrets.yaml"; \
		echo "📝 Please edit it with your actual API keys"; \
	else \
		echo "ℹ️ fastagent.secrets.yaml already exists"; \
	fi
	@echo "✅ Setup complete"

# Test configuration
.PHONY: test
test:
	@echo "🧪 Testing configuration and connectivity..."
	@$(UV) run test-setup.py

# Install dependencies
.PHONY: install
install:
	@echo "📦 Installing dependencies..."
	@cd $(PROJECT_ROOT) && $(UV) sync
	@echo "✅ Dependencies installed"

# Run FastAgent directly (requires MCP server to be running)
.PHONY: run
run:
	@echo "🤖 Starting FastAgent..."
	@$(UV) run agent.py

# Launch with automatic MCP server startup
.PHONY: launch
launch:
	@echo "🚀 Launching FastAgent with MCP server..."
	@$(UV) run launch.py

# Start only the MCP server
.PHONY: server
server:
	@echo "🌐 Starting MCP server in SSE mode..."
	@if [ ! -f fastagent.secrets.yaml ]; then \
		echo "❌ fastagent.secrets.yaml not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@export $$(grep -v '^#' fastagent.secrets.yaml | sed '/^$$/d' | xargs) && \
	 cd $(PROJECT_ROOT) && \
	 $(UV) run hubspot-mcp-server --mode sse --port 8080 --auth-header

# Clean up
.PHONY: clean
clean:
	@echo "🧹 Cleaning up..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -f *.log
	@echo "✅ Cleanup complete"

# Development helpers
.PHONY: check-secrets
check-secrets:
	@if [ ! -f fastagent.secrets.yaml ]; then \
		echo "❌ fastagent.secrets.yaml not found"; \
		echo "📝 Run 'make setup' to create it"; \
		exit 1; \
	fi
	@echo "✅ Secrets file exists"

.PHONY: validate-config
validate-config:
	@echo "🔍 Validating configuration files..."
	@python -c "import yaml; yaml.safe_load(open('fastagent.config.yaml'))" && echo "✅ Config is valid YAML"
	@python -c "import yaml; yaml.safe_load(open('fastagent.secrets.yaml'))" && echo "✅ Secrets is valid YAML"

# Quick status check
.PHONY: status
status:
	@echo "📊 FastAgent SSE Example Status"
	@echo "=============================="
	@echo -n "Config file: "
	@if [ -f fastagent.config.yaml ]; then echo "✅ Present"; else echo "❌ Missing"; fi
	@echo -n "Secrets file: "
	@if [ -f fastagent.secrets.yaml ]; then echo "✅ Present"; else echo "❌ Missing"; fi
	@echo -n "MCP Server: "
	@curl -s -f -m 2 http://localhost:8080/health >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running"
	@echo ""

# Show logs (if running in background)
.PHONY: logs
logs:
	@echo "📄 Recent logs..."
	@if [ -f server.log ]; then tail -n 20 server.log; else echo "No logs found"; fi

# Development mode (auto-restart on changes)
.PHONY: dev
dev:
	@echo "🔧 Development mode - auto-restart on changes"
	@echo "Press Ctrl+C to stop"
	@$(UV) run watchdog agent.py

.PHONY: all
all: setup install test launch
