# Scripts Directory

This directory contains utility scripts for the HubSpot MCP Server project, organized by functionality.

## 📁 Directory Structure

```
scripts/
├── claude/          # Claude Desktop management
│   ├── kill_claude.sh
│   ├── setup_claude_config.sh
│   └── diagnose_mcp.sh
├── mcp/             # MCP server management
│   ├── run_mcp_hubspot.sh
│   └── test_mcp_config.sh
├── dev/             # Development tools
│   ├── check_quality.sh
│   ├── install_hooks.sh
│   └── lint_check.py
└── README.md        # This file
```

## 🎯 Script Categories

### 📱 Claude Desktop Management (`scripts/claude/`)

Scripts for managing Claude Desktop application and its integration with the MCP server.

#### 🔴 kill_claude.sh

**Purpose:** Terminate all Claude Desktop processes running on the system.

**Usage:**

```bash
# Direct execution
./scripts/claude/kill_claude.sh

# Via justfile (recommended)
just kill-claude
```

**Features:**

- ✅ **Progressive termination**: Tries graceful shutdown first, then force kill
- ✅ **Smart detection**: Finds all Claude-related processes
- ✅ **Safe execution**: Excludes itself from termination list
- ✅ **Colored output**: Clear visual feedback with status indicators
- ✅ **Error handling**: Robust process detection and cleanup

#### 🔧 setup_claude_config.sh

**Purpose:** Dynamically generate Claude Desktop configuration for HubSpot MCP Server.

**Usage:**

```bash
# Direct execution
./scripts/claude/setup_claude_config.sh

# Via justfile (recommended)
just setup-claude
```

**Features:**

- ✅ **Dynamic paths**: Automatically detects project and script locations
- ✅ **API key management**: Retrieves from environment, .envrc, or user input
- ✅ **Secure**: Prompts for API key if not found in environment
- ✅ **Validation**: Checks JSON syntax and file existence
- ✅ **Portable**: Works on any machine without hardcoded paths

#### 🔍 diagnose_mcp.sh

**Purpose:** Quick diagnostic of MCP server status and health checks.

**Usage:**

```bash
# Direct execution
./scripts/claude/diagnose_mcp.sh

# Via justfile (recommended)
just diagnose-mcp
```

**Features:**

- ✅ **Process detection**: Checks if Claude Desktop is running
- ✅ **Log analysis**: Examines recent MCP server activity
- ✅ **Configuration validation**: Tests wrapper script functionality
- ✅ **Summary reporting**: Provides actionable next steps

### ⚙️ MCP Server Management (`scripts/mcp/`)

Scripts for managing the HubSpot MCP server itself.

#### 🚀 run_mcp_hubspot.sh

**Purpose:** Wrapper script to launch the HubSpot MCP Server with proper environment setup.

**Usage:**

```bash
# Direct execution
./scripts/mcp/run_mcp_hubspot.sh --mode stdio

# Used by Claude Desktop (automatic)
```

**Features:**

- ✅ **Dynamic paths**: Auto-detects project directory and uv location
- ✅ **Environment setup**: Configures PATH and working directory
- ✅ **Error handling**: Validates environment before execution
- ✅ **HOME variable safety**: Works even when HOME is not set
- ✅ **Portable**: No hardcoded paths - works anywhere

#### 🧪 test_mcp_config.sh

**Purpose:** Test and validate the MCP HubSpot configuration for Claude Desktop.

**Usage:**

```bash
# Direct execution
./scripts/mcp/test_mcp_config.sh

# Via justfile (recommended)
just test-mcp
```

**Features:**

- ✅ **Configuration validation**: Checks Claude Desktop config file
- ✅ **Dependency verification**: Ensures uv, Python, and project files are available
- ✅ **API key validation**: Confirms HubSpot API key is configured
- ✅ **Server startup test**: Validates MCP server can start successfully
- ✅ **Comprehensive reporting**: Clear status indicators and next steps

### 🛠️ Development Tools (`scripts/dev/`)

Scripts for code quality, testing, and development workflow automation.

#### ✅ check_quality.sh

**Purpose:** Run comprehensive code quality checks including formatting, linting, and security.

**Usage:**

```bash
# Direct execution
./scripts/dev/check_quality.sh

# Via justfile
just check
```

#### 🔗 install_hooks.sh

**Purpose:** Install Git pre-commit hooks for automated quality checks.

**Usage:**

```bash
# Direct execution
./scripts/dev/install_hooks.sh
```

#### 🐍 lint_check.py

**Purpose:** Python script for advanced linting and code analysis.

**Usage:**

```bash
# Direct execution
./scripts/dev/lint_check.py
```

## 🚀 Quick Commands

All scripts can be executed directly or via the convenient `justfile` recipes:

```bash
# Claude Desktop Management
just setup-claude     # Setup Claude Desktop configuration
just kill-claude      # Kill all Claude processes
just start-claude     # Start Claude Desktop
just diagnose-mcp     # Diagnostic MCP server status

# MCP Server Management
just test-mcp         # Test MCP configuration
just server-stdio     # Start MCP server in stdio mode

# Development Tools
just check            # Run all quality checks
just format           # Format code
just lint             # Run linting
```

## 🎯 Common Workflows

### First Time Setup

```bash
# 1. Setup Claude Desktop
just setup-claude

# 2. Test configuration
just test-mcp

# 3. Start Claude Desktop
just start-claude
```

### Daily Development

```bash
# Quick health check
just diagnose-mcp

# Restart Claude cleanly
just kill-claude && just start-claude

# Monitor logs
just logs-claude
```

### Code Quality

```bash
# Before committing
just check

# Fix formatting issues
just format
```

## 🛡️ Safety Features

- **Self-protection**: Scripts never terminate themselves
- **Graceful degradation**: Multiple fallback strategies
- **Status reporting**: Clear feedback with colored output
- **Error recovery**: Handles partial failures gracefully
- **Environment validation**: Checks prerequisites before execution

## 📋 Prerequisites

All scripts require:

- **bash** shell environment
- **uv** package manager installed
- **Python 3.12+** environment
- **HubSpot API key** configured (for MCP scripts)

## 🔧 Adding New Scripts

When adding new scripts:

1. **Choose the right category**:
   - `claude/` for Claude Desktop management
   - `mcp/` for MCP server tools
   - `dev/` for development utilities

2. **Follow naming conventions**:
   - Use `snake_case.sh` for shell scripts
   - Use `snake_case.py` for Python scripts
   - Use descriptive, action-oriented names

3. **Include proper headers**:

   ```bash
   #!/bin/bash
   # Brief description of what the script does

   set -euo pipefail  # Strict mode
   ```

4. **Update documentation**:
   - Add entry to this README.md
   - Add justfile recipe if applicable
   - Include usage examples

5. **Make executable**:

   ```bash
   chmod +x scripts/category/your_script.sh
   ```

## 📝 Best Practices

- **Use colors**: Include colored output for better UX
- **Error handling**: Always include proper error handling
- **Documentation**: Self-document with `--help` options
- **Testing**: Test scripts in clean environments
- **Security**: Never hardcode secrets or API keys
- **Portability**: Use dynamic path detection

## 🔗 Integration

Scripts are integrated with:

- **Justfile**: Convenient command aliases
- **Git hooks**: Automated quality checks (via dev/ scripts)
- **CI/CD**: Quality gates and testing
- **Claude Desktop**: MCP server management
