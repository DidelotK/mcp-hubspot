#!/bin/bash
# Setup Claude Desktop Configuration Script
# Generates a dynamic configuration for the HubSpot MCP Server

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up Claude Desktop configuration...${NC}"

# Dynamic path detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WRAPPER_SCRIPT="$PROJECT_DIR/scripts/mcp/run_mcp_hubspot.sh"

# Check if wrapper script exists
if [ ! -f "$WRAPPER_SCRIPT" ]; then
    echo -e "${RED}❌ Wrapper script not found: $WRAPPER_SCRIPT${NC}"
    exit 1
fi

# Get HubSpot API key from user input or environment
if [ -n "${HUBSPOT_API_KEY:-}" ]; then
    echo -e "${GREEN}✅ Using HUBSPOT_API_KEY from environment${NC}"
    API_KEY="$HUBSPOT_API_KEY"
elif [ -f "$PROJECT_DIR/.envrc" ] && grep -q "HUBSPOT_API_KEY" "$PROJECT_DIR/.envrc"; then
    API_KEY=$(grep "HUBSPOT_API_KEY" "$PROJECT_DIR/.envrc" | cut -d'"' -f2)
    echo -e "${GREEN}✅ Using API key from .envrc file${NC}"
else
    echo -e "${YELLOW}⚠️  HubSpot API key not found in environment or .envrc${NC}"
    echo -e "${BLUE}📝 Please enter your HubSpot API key:${NC}"
    read -r -p "API Key: " API_KEY

    if [ -z "$API_KEY" ]; then
        echo -e "${RED}❌ API key cannot be empty${NC}"
        exit 1
    fi
fi

# Create Claude Desktop config directory if it doesn't exist
CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
mkdir -p "$CLAUDE_CONFIG_DIR"

# Generate Claude Desktop configuration
cat > "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" << EOF
{
    "mcpServers": {
        "hubspot": {
            "command": "$WRAPPER_SCRIPT",
            "args": [
                "--mode",
                "stdio"
            ],
            "env": {
                "HUBSPOT_API_KEY": "$API_KEY"
            }
        }
    }
}
EOF

echo -e "${GREEN}✅ Claude Desktop configuration created successfully${NC}"
echo -e "${BLUE}📁 Config file: $CLAUDE_CONFIG_DIR/claude_desktop_config.json${NC}"

# Validate JSON syntax
if python3 -m json.tool "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ JSON syntax is valid${NC}"
else
    echo -e "${RED}❌ Invalid JSON syntax in generated config${NC}"
    exit 1
fi

# Show configuration summary
echo -e "\n${BLUE}📋 Configuration Summary:${NC}"
echo -e "   Project Dir: $PROJECT_DIR"
echo -e "   Wrapper Script: $WRAPPER_SCRIPT"
echo -e "   API Key: ${API_KEY:0:8}***"
echo -e "   Config File: $CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo -e "\n${GREEN}🎉 Setup complete! You can now start Claude Desktop.${NC}"
echo -e "${YELLOW}💡 Tip: Use 'just start-claude' to launch with this configuration${NC}"
