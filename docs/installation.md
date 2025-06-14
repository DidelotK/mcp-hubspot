# Installation and Configuration

## Prerequisites

- Python 3.12 or higher
- uv (Python package manager)
- Valid HubSpot API key

## Installation

### 1. Install uv (if not already installed)

```bash
# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to your PATH (restart shell or run):
source $HOME/.local/bin/env
```

Verify installation:
```bash
uv --version
```

### 2. Clone the project

```bash
git clone <repo-url>
cd hubspot-mcp-server
```

### 3. Install dependencies

```bash
# Install all dependencies including development tools
uv sync --extra dev
```

### 4. Configure environment variables

Create a `.envrc` file or set environment variables:

```bash
export HUBSPOT_API_KEY="your_hubspot_api_key"
```

## HubSpot Configuration

The server requires a valid HubSpot API key. You can obtain this key from your HubSpot account:

1. Log in to your HubSpot account
2. Go to Settings > Integrations > Private App API Keys
3. Create a new private API key
4. Set the HUBSPOT_API_KEY environment variable

### Required Permissions

Make sure your API key has the following permissions:
- **Contacts**: Read
- **Companies**: Read  
- **Deals**: Read
- **CRM Search**: Read

## Starting the Server

### stdio mode (for Claude Desktop)

```bash
uv run python main.py --mode stdio
```

### SSE mode (for other MCP clients)

```bash
uv run python main.py --mode sse --host 127.0.0.1 --port 8080
```

## Installation Verification

To verify everything is working correctly:

```bash
# Run tests
uv run pytest

# Verify HubSpot connection
uv run python -c "from src.hubspot_mcp.client import HubSpotClient; client = HubSpotClient(); print('✅ HubSpot connection OK')"
``` 