#!/bin/bash
# Quick MCP Diagnostic Script
# Checks the current status of Claude Desktop and MCP server

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 MCP HubSpot Server Diagnostic${NC}\n"

# Check if Claude Desktop is running
echo -e "${BLUE}1. Claude Desktop Process Status:${NC}"
if pgrep -f "claude-desktop" > /dev/null; then
    CLAUDE_PIDS=$(pgrep -f "claude-desktop" | wc -l)
    echo -e "   ${GREEN}✅ Claude Desktop is running ($CLAUDE_PIDS processes)${NC}"
else
    echo -e "   ${RED}❌ Claude Desktop is not running${NC}"
    exit 1
fi

# Check recent MCP server logs
echo -e "\n${BLUE}2. Recent MCP Server Activity:${NC}"
LOG_FILE="$HOME/.config/Claude/logs/mcp-server-hubspot.log"

# Initialize variables
RECENT_SUCCESS=0
RECENT_ERRORS=0
RECENT_DISCONNECTS=0

if [ -f "$LOG_FILE" ]; then
    # Look for recent successful connections (last 5 minutes)
    RECENT_SUCCESS=$(tail -50 "$LOG_FILE" | grep -c "Server started and connected successfully" 2>/dev/null || echo "0")
    RECENT_ERRORS=$(tail -50 "$LOG_FILE" | grep -c "HOME: unbound variable" 2>/dev/null || echo "0")
    RECENT_DISCONNECTS=$(tail -50 "$LOG_FILE" | grep -c "Server disconnected" 2>/dev/null || echo "0")
    
    # Clean up any whitespace/newlines
    RECENT_SUCCESS=${RECENT_SUCCESS//[^0-9]/}
    RECENT_ERRORS=${RECENT_ERRORS//[^0-9]/}
    RECENT_DISCONNECTS=${RECENT_DISCONNECTS//[^0-9]/}
    
    # Set defaults if empty
    RECENT_SUCCESS=${RECENT_SUCCESS:-0}
    RECENT_ERRORS=${RECENT_ERRORS:-0}
    RECENT_DISCONNECTS=${RECENT_DISCONNECTS:-0}
    
    if [ "$RECENT_SUCCESS" -gt 0 ] && [ "$RECENT_ERRORS" -eq 0 ]; then
        echo -e "   ${GREEN}✅ MCP server connected successfully${NC}"
        echo -e "   ${GREEN}   Recent connections: $RECENT_SUCCESS${NC}"
    elif [ "$RECENT_ERRORS" -gt 0 ]; then
        echo -e "   ${RED}❌ HOME variable errors detected: $RECENT_ERRORS${NC}"
        echo -e "   ${YELLOW}   Fix needed in wrapper script${NC}"
    elif [ "$RECENT_DISCONNECTS" -gt 0 ]; then
        echo -e "   ${YELLOW}⚠️  Recent disconnections: $RECENT_DISCONNECTS${NC}"
    else
        echo -e "   ${YELLOW}⚠️  No recent activity found${NC}"
    fi
    
    # Show last few log entries
    echo -e "\n${BLUE}3. Last 3 Log Entries:${NC}"
    tail -3 "$LOG_FILE" | while read line; do
        if echo "$line" | grep -q "successfully"; then
            echo -e "   ${GREEN}$line${NC}"
        elif echo "$line" | grep -q "error\|Error"; then
            echo -e "   ${RED}$line${NC}"
        else
            echo -e "   ${YELLOW}$line${NC}"
        fi
    done
else
    echo -e "   ${RED}❌ MCP log file not found${NC}"
fi

# Test wrapper script
echo -e "\n${BLUE}4. Testing Wrapper Script:${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$SCRIPT_DIR/../mcp/run_mcp_hubspot.sh"

# Test without HOME variable using bash -c to avoid timeout issues
if bash -c "unset HOME; '$WRAPPER_SCRIPT' --help" > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Wrapper script works without HOME variable${NC}"
else
    echo -e "   ${RED}❌ Wrapper script fails without HOME variable${NC}"
fi

# Summary
echo -e "\n${BLUE}5. Summary:${NC}"
if [ "$RECENT_SUCCESS" -gt 0 ] && [ "$RECENT_ERRORS" -eq 0 ]; then
    echo -e "   ${GREEN}🎉 MCP HubSpot Server is working correctly!${NC}"
    echo -e "   ${GREEN}   You can now use HubSpot tools in Claude Desktop${NC}"
else
    echo -e "   ${YELLOW}⚠️  MCP server may need attention${NC}"
    echo -e "   ${BLUE}   Try: just kill-claude && just start-claude${NC}"
fi

echo -e "\n${BLUE}💡 Quick Commands:${NC}"
echo -e "   ${BLUE}just kill-claude${NC}    # Stop all Claude processes"
echo -e "   ${BLUE}just start-claude${NC}   # Start Claude Desktop"
echo -e "   ${BLUE}just test-mcp${NC}       # Test MCP configuration"
echo -e "   ${BLUE}just logs-claude${NC}    # Monitor logs" 