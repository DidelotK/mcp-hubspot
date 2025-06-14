#!/bin/bash
# MCP HubSpot Server Wrapper Script
# This script properly configures the environment and launches the MCP server

set -euo pipefail

# Ensure HOME is set (Claude Desktop might not provide it)
if [ -z "${HOME:-}" ]; then
    export HOME="$(getent passwd "$(whoami)" | cut -d: -f6)"
fi

# Dynamic path detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Find uv in common locations
if command -v uv >/dev/null 2>&1; then
    UV_PATH="$(command -v uv)"
elif [ -f "$HOME/.local/bin/uv" ]; then
    UV_PATH="$HOME/.local/bin/uv"
elif [ -f "$HOME/.cargo/bin/uv" ]; then
    UV_PATH="$HOME/.cargo/bin/uv"
else
    echo "Error: uv not found in PATH or common locations" >&2
    exit 1
fi

# Dynamic PATH configuration (handle potential missing HOME gracefully)
USER_LOCAL_BIN="${HOME}/.local/bin"
USER_CARGO_BIN="${HOME}/.cargo/bin"
NODE_BIN="${HOME}/.nvm/versions/node/v20.19.2/bin"

export PATH="$USER_LOCAL_BIN:$USER_CARGO_BIN:$NODE_BIN:$PATH"

# Change to project directory
cd "$PROJECT_DIR"

# Validate that we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found in $PROJECT_DIR" >&2
    exit 1
fi

# Launch the MCP server (API key should be provided via environment)
exec "$UV_PATH" run python main.py "$@" 