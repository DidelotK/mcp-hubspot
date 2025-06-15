#!/bin/bash
# Script to test MCP HubSpot configuration
# Author: Auto-generated for MCP HubSpot project

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing MCP HubSpot Configuration${NC}\n"

# 1. Check if Claude Desktop config exists
echo -e "${BLUE}📁 Checking Claude Desktop configuration...${NC}"
CONFIG_FILE="$HOME/.config/Claude/claude_desktop_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Claude Desktop config file not found: $CONFIG_FILE${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Config file exists: $CONFIG_FILE${NC}"
fi

# 2. Validate JSON syntax
echo -e "\n${BLUE}📄 Validating JSON syntax...${NC}"
if python3 -m json.tool "$CONFIG_FILE" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ JSON syntax is valid${NC}"
else
    echo -e "${RED}❌ Invalid JSON syntax in config file${NC}"
    exit 1
fi

# 3. Check if uv command exists
echo -e "\n${BLUE}🔍 Checking uv installation...${NC}"
# Dynamic uv detection
if command -v uv >/dev/null 2>&1; then
    UV_PATH="$(command -v uv)"
elif [ -f "$HOME/.local/bin/uv" ]; then
    UV_PATH="$HOME/.local/bin/uv"
elif [ -f "$HOME/.cargo/bin/uv" ]; then
    UV_PATH="$HOME/.cargo/bin/uv"
else
    echo -e "${RED}❌ uv not found in PATH or common locations${NC}"
    exit 1
fi

echo -e "${GREEN}✅ uv found at: $UV_PATH${NC}"
echo -e "${GREEN}   Version: $($UV_PATH --version)${NC}"

# 4. Check if project directory exists
echo -e "\n${BLUE}📂 Checking project directory...${NC}"
# Dynamic project directory detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${GREEN}✅ Project directory exists: $PROJECT_DIR${NC}"
else
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

# 5. Check if main module exists
echo -e "\n${BLUE}🐍 Checking main module...${NC}"
MAIN_MODULE="$PROJECT_DIR/src/hubspot_mcp/__main__.py"
if [ -f "$MAIN_MODULE" ]; then
    echo -e "${GREEN}✅ Main module found: $MAIN_MODULE${NC}"
else
    echo -e "${RED}❌ Main module not found: $MAIN_MODULE${NC}"
    exit 1
fi

# 6. Check HubSpot API key (now in Claude Desktop config)
echo -e "\n${BLUE}🔑 Checking HubSpot API key...${NC}"
if grep -q "HUBSPOT_API_KEY" "$CONFIG_FILE"; then
    echo -e "${GREEN}✅ HubSpot API key found in Claude Desktop config${NC}"
else
    echo -e "${YELLOW}⚠️  HubSpot API key not found in Claude Desktop config${NC}"
    echo -e "${YELLOW}💡 Run 'just setup-claude' to configure it properly${NC}"
fi

# 7. Test MCP server startup using wrapper script
echo -e "\n${BLUE}🚀 Testing MCP server startup...${NC}"

WRAPPER_SCRIPT="$PROJECT_DIR/scripts/mcp/run_mcp_hubspot.sh"
echo -e "${BLUE}   Running: $WRAPPER_SCRIPT --help${NC}"

# Extract API key from Claude config for testing
if grep -q "HUBSPOT_API_KEY" "$CONFIG_FILE"; then
    API_KEY=$(grep -o '"HUBSPOT_API_KEY":[^,}]*' "$CONFIG_FILE" | cut -d'"' -f4)
    export HUBSPOT_API_KEY="$API_KEY"
fi

# Run the wrapper script help command
HUBSPOT_API_KEY="$API_KEY" "$WRAPPER_SCRIPT" --help > /tmp/mcp_test.log 2>&1
help_exit_code=$?

# Check if we got the expected output (regardless of exit code)
if grep -q "HubSpot MCP Server" /tmp/mcp_test.log; then
    echo -e "${GREEN}✅ MCP server can start successfully${NC}"
    echo -e "${GREEN}✅ Server responds with correct identification${NC}"
else
    echo -e "${RED}❌ MCP server failed to start or doesn't respond correctly${NC}"
    echo -e "${YELLOW}Output (exit code: $help_exit_code):${NC}"
    cat /tmp/mcp_test.log
    exit 1
fi

# 8. Check Claude Desktop logs (if they exist)
echo -e "\n${BLUE}📋 Checking recent Claude Desktop logs...${NC}"
LOG_DIR="$HOME/.config/Claude/logs"
if [ -d "$LOG_DIR" ]; then
    LATEST_MCP_LOG=$(find "$LOG_DIR" -name "mcp*.log" -type f -exec ls -t {} + 2>/dev/null | head -1)
    if [ -n "$LATEST_MCP_LOG" ]; then
        echo -e "${BLUE}   Latest MCP log: $LATEST_MCP_LOG${NC}"
        if grep -q "ENOENT" "$LATEST_MCP_LOG" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Found ENOENT errors in logs (command not found)${NC}"
        elif grep -q "Initializing server" "$LATEST_MCP_LOG" 2>/dev/null; then
            echo -e "${GREEN}✅ Server initialization found in logs${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No MCP logs found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Claude logs directory not found${NC}"
fi

# Cleanup
rm -f /tmp/mcp_test.log

echo -e "\n${GREEN}🎉 MCP Configuration Test Complete!${NC}"
echo -e "\n${BLUE}💡 Next steps:${NC}"
echo -e "   1. Start Claude Desktop: ${GREEN}claude-desktop${NC}"
echo -e "   2. Test MCP integration: ${GREEN}\"List my HubSpot contacts\"${NC}"
echo -e "   3. Check logs if issues: ${GREEN}cat ~/.config/Claude/logs/mcp*.log${NC}"
