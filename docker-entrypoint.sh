#!/bin/bash
set -e

# Default values
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8080"
DEFAULT_MODE="sse"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check required environment variables
if [ -z "$HUBSPOT_API_KEY" ]; then
    log "ERROR: HUBSPOT_API_KEY environment variable is required"
    exit 1
fi

# Set defaults if not provided
HOST=${HOST:-$DEFAULT_HOST}
PORT=${PORT:-$DEFAULT_PORT}
MODE=${MODE:-$DEFAULT_MODE}

# Authentication configuration
MCP_AUTH_KEY=${MCP_AUTH_KEY:-}
MCP_AUTH_HEADER=${MCP_AUTH_HEADER:-X-API-Key}

# Override with command line arguments if provided
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        *)
            # Keep unknown arguments
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Validate mode
if [[ "$MODE" != "sse" && "$MODE" != "stdio" ]]; then
    log "ERROR: Invalid mode '$MODE'. Must be 'sse' or 'stdio'"
    exit 1
fi

# For production, we force SSE mode
if [ "$MODE" = "stdio" ]; then
    log "WARNING: stdio mode is not suitable for production deployment. Switching to SSE mode."
    MODE="sse"
fi

# Log startup information
log "Starting HubSpot MCP Server"
log "Mode: $MODE"
log "Host: $HOST"
log "Port: $PORT"
log "Python version: $(python --version)"

# Log authentication status
if [ -n "$MCP_AUTH_KEY" ]; then
    log "Authentication: ENABLED"
    log "Auth Header: $MCP_AUTH_HEADER"
else
    log "Authentication: DISABLED (MCP_AUTH_KEY not set)"
fi

# Health check for readiness
log "Performing pre-flight checks..."

# Check if we can import the main module
python -c "from hubspot_mcp.__main__ import main; print('Module import successful')" || {
    log "ERROR: Failed to import main module"
    exit 1
}

log "Pre-flight checks completed successfully"

# Start the server
log "Starting server..."
exec hubspot-mcp-server --mode "$MODE" --host "$HOST" --port "$PORT" "${ARGS[@]}" 