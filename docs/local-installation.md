# Local Installation Guide

## Overview

This guide explains how to build and install the HubSpot MCP Server locally using uv for development, testing, or system-wide deployment.

## Prerequisites

- **Python 3.12+**: Required runtime environment
- **uv Package Manager**: Latest version installed
- **Git**: For cloning the repository
- **HubSpot API Key**: Valid private app API key

## Installation Methods

### 1. Development Installation (Recommended for Contributors)

Install the package in development mode, allowing you to make changes and see them immediately.

#### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/mcp-hubspot.git
cd mcp-hubspot

# Install development dependencies
uv sync --dev
```

#### Install in Development Mode

```bash
# Install in editable mode
uv pip install -e .

# Or using uv's development install
uv sync --dev
```

**Benefits:**
- ✅ Changes to source code are immediately reflected
- ✅ Perfect for development and testing
- ✅ Includes all development tools
- ✅ Can run tests and quality checks

#### Verify Development Installation

```bash
# Check if installed correctly
uv run python -c "import hubspot_mcp; print('✅ Package installed successfully')"

# Test the server
uv run hubspot-mcp-server --help
```

### 2. Local Package Installation

Build and install the package locally as a regular Python package.

#### Build the Package

```bash
# Ensure you're in the project directory
cd mcp-hubspot

# Build the distribution packages
uv build
```

This creates:
- `dist/hubspot_mcp-x.x.x.tar.gz` (source distribution)
- `dist/hubspot_mcp-x.x.x-py3-none-any.whl` (wheel distribution)

#### Install from Local Build

```bash
# Install the wheel package
uv pip install dist/hubspot_mcp-*.whl

# Or install the source distribution
uv pip install dist/hubspot_mcp-*.tar.gz
```

#### Verify Installation

```bash
# Check installation
uv run python -c "import hubspot_mcp; print(hubspot_mcp.__version__)"

# Test the CLI command
uv run hubspot-mcp-server --help

# Or test as Python module
uv run python -m hubspot_mcp --help
```

### 3. Direct Installation from Source

Install directly from the current directory without building separate packages.

```bash
# Install from current directory
uv pip install .

# Or with development dependencies
uv pip install ".[dev]"
```

## Configuration After Installation

### 1. Environment Setup

```bash
# Set your HubSpot API key
export HUBSPOT_API_KEY="pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Optional: Set logging level
export LOG_LEVEL="INFO"
```

### 2. Verify Installation Works

```bash
# Test the server in stdio mode
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uv run python -m hubspot_mcp.main --mode stdio

# Or start in SSE mode
uv run python -m hubspot_mcp.main --mode sse --port 8080
```

## Using the Locally Installed Package

### 1. With Claude Desktop

Update your Claude Desktop configuration to use the installed package:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "hubspot_mcp.main",
        "--mode",
        "stdio"
      ],
      "env": {
        "HUBSPOT_API_KEY": "your_hubspot_api_key"
      }
    }
  }
}
```

### 2. As a Python Module

```python
# Import and use in your Python code
from hubspot_mcp.client import HubSpotClient
from hubspot_mcp.tools import ContactsTool

# Create client
client = HubSpotClient()

# Use tools
contacts_tool = ContactsTool(client)
```

### 3. Command Line Usage

You can use the installed package in multiple ways:

```bash
# Using the binary entry point
uv run hubspot-mcp-server --mode sse --port 8080

# Or as Python module
uv run python -m hubspot_mcp --mode stdio

# If installed globally, direct binary usage
hubspot-mcp-server --mode sse --port 8080
```

## Advanced Installation Options

### 1. Virtual Environment Management

```bash
# Create a dedicated virtual environment
uv venv mcp-hubspot-env

# Activate the environment
source mcp-hubspot-env/bin/activate  # Linux/macOS
# or
mcp-hubspot-env\Scripts\activate.bat  # Windows

# Install in the virtual environment
uv pip install .
```

### 2. System-Wide Installation

```bash
# Install globally (requires appropriate permissions)
uv pip install . --system

# Or using pip directly
pip install .
```

### 3. Installation with Specific Extras

```bash
# Install with development dependencies
uv pip install ".[dev]"

# Install with embedding support
uv pip install ".[embeddings]"

# Install with all extras
uv pip install ".[dev,embeddings,docs]"
```

## Updating Local Installation

### Development Installation

```bash
# Pull latest changes
git pull origin main

# Sync dependencies (for development mode)
uv sync --dev
```

### Package Installation

```bash
# Rebuild and reinstall
uv build
uv pip install --upgrade dist/hubspot_mcp-*.whl
```

## Uninstalling

### Remove the Package

```bash
# Uninstall the package
uv pip uninstall hubspot-mcp

# Clean up build artifacts
rm -rf dist/ build/ *.egg-info/
```

### Clean Development Environment

```bash
# Remove virtual environment
rm -rf .venv/

# Remove cache
rm -rf .mypy_cache/ .pytest_cache/ __pycache__/
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Ensure package is properly installed
uv pip list | grep hubspot

# Reinstall if needed
uv pip uninstall hubspot-mcp
uv pip install .
```

#### 2. Missing Dependencies

```bash
# Reinstall with all dependencies
uv sync --dev --all-extras

# Or rebuild and install
uv build
uv pip install dist/hubspot_mcp-*.whl --force-reinstall
```

#### 3. Permission Issues

```bash
# Install in user directory
uv pip install . --user

# Or use virtual environment
uv venv
source .venv/bin/activate
uv pip install .
```

#### 4. Build Failures

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Update build tools
uv pip install --upgrade build wheel

# Try building again
uv build
```

### Verification Steps

```bash
# 1. Check Python can import the package
python -c "import hubspot_mcp; print('✅ Import successful')"

# 2. Check version
python -c "import hubspot_mcp; print(f'Version: {hubspot_mcp.__version__}')"

# 3. Test binary functionality
uv run hubspot-mcp-server --help

# 4. Test module functionality
uv run python -m hubspot_mcp --help

# 5. Test basic server functionality (requires HUBSPOT_API_KEY)
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uv run python -m hubspot_mcp --mode stdio

# 6. Check dependencies
uv pip check
```

## Integration with Development Workflow

### 1. Development Cycle

```bash
# 1. Make changes to source code
vim src/hubspot_mcp/tools/new_tool.py

# 2. Run tests
uv run pytest

# 3. Test locally installed version
python -m hubspot_mcp.main --mode stdio

# 4. Build and test package
uv build
uv pip install dist/hubspot_mcp-*.whl --force-reinstall
```

### 2. Testing Different Versions

```bash
# Install specific version
uv pip install hubspot-mcp==1.0.0

# Install from specific git commit
uv pip install git+https://github.com/your-org/mcp-hubspot.git@commit-hash

# Install from local branch
git checkout feature-branch
uv pip install .
```

## Best Practices

### 1. Development Setup

- ✅ Use development installation (`uv sync --dev`) for active development
- ✅ Keep virtual environments separate for different projects
- ✅ Regularly sync dependencies (`uv sync`)
- ✅ Test both development and package installations

### 2. Production Setup

- ✅ Use wheel installation for production deployments
- ✅ Pin specific versions in requirements
- ✅ Test package installation in clean environments
- ✅ Document installation procedures for your team

### 3. Maintenance

- ✅ Regularly update dependencies
- ✅ Test installation on different Python versions
- ✅ Keep build artifacts clean
- ✅ Verify installations work in fresh environments

## Next Steps

After successful local installation:

1. **Configure Integration**: See [Integration Guide](integration.md)
2. **Test Functionality**: Follow [Integration Testing Guide](integration-testing.md)
3. **Development**: Check [Developer Guide](developer.md)
4. **Troubleshooting**: Refer to [Troubleshooting Guide](troubleshooting.md)

## Related Documentation

- [Installation Guide](installation.md) - Standard installation methods
- [Developer Guide](developer.md) - Development setup and workflow
- [Integration Guide](integration.md) - Client configuration
- [Contributing Guide](contributing.md) - Contribution guidelines 