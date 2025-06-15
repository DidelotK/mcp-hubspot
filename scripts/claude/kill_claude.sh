#!/bin/bash
# Script to kill all Claude Desktop processes
# Author: Auto-generated for MCP HubSpot project

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Searching for Claude Desktop processes...${NC}"

# Function to check if any Claude processes are running
check_claude_processes() {
    ps aux | grep -i claude | grep -v grep | grep -v "kill_claude.sh" || true
}

# Function to count Claude processes
count_claude_processes() {
    ps aux | grep -i claude | grep -v grep | grep -v "kill_claude.sh" | wc -l
}

# Initial count
initial_count=$(count_claude_processes)

if [ "$initial_count" -eq 0 ]; then
    echo -e "${GREEN}✅ No Claude Desktop processes found.${NC}"
    exit 0
fi

echo -e "${YELLOW}📋 Found $initial_count Claude Desktop process(es):${NC}"
check_claude_processes

echo -e "\n${BLUE}🔄 Step 1: Graceful termination with SIGTERM...${NC}"
pkill -f claude-desktop 2>/dev/null || echo "No processes matched claude-desktop pattern"

# Wait a bit for graceful shutdown
sleep 2

# Check if processes still exist
remaining_count=$(count_claude_processes)
if [ "$remaining_count" -eq 0 ]; then
    echo -e "${GREEN}✅ All Claude Desktop processes terminated gracefully.${NC}"
    exit 0
fi

echo -e "${YELLOW}⚠️  $remaining_count process(es) still running. Trying killall...${NC}"

echo -e "\n${BLUE}🔄 Step 2: Force termination with killall...${NC}"
killall -9 claude-desktop 2>/dev/null || echo "No claude-desktop processes to kill"
killall -9 electron 2>/dev/null || echo "No electron processes to kill"

# Wait a bit
sleep 1

# Check again
remaining_count=$(count_claude_processes)
if [ "$remaining_count" -eq 0 ]; then
    echo -e "${GREEN}✅ All Claude Desktop processes terminated with killall.${NC}"
    exit 0
fi

echo -e "${YELLOW}⚠️  $remaining_count process(es) still running. Using individual kill...${NC}"

echo -e "\n${BLUE}🔄 Step 3: Individual process termination...${NC}"

# Get PIDs of Claude processes and kill them individually
claude_pids=$(ps aux | grep -i claude | grep -v grep | grep -v "kill_claude.sh" | awk '{print $2}' || true)

if [ -n "$claude_pids" ]; then
    echo "Killing individual PIDs: $claude_pids"
    for pid in $claude_pids; do
        kill -9 "$pid" 2>/dev/null || echo "Process $pid already terminated"
    done
fi

# Final check
sleep 1
final_count=$(count_claude_processes)

if [ "$final_count" -eq 0 ]; then
    echo -e "\n${GREEN}🎉 SUCCESS: All Claude Desktop processes have been terminated!${NC}"
    echo -e "${GREEN}📊 Processes terminated: $initial_count${NC}"
else
    echo -e "\n${RED}❌ WARNING: $final_count process(es) still running:${NC}"
    check_claude_processes
    echo -e "\n${YELLOW}💡 You may need to manually investigate these processes.${NC}"
    exit 1
fi

echo -e "\n${BLUE}💡 To restart Claude Desktop, run: ${GREEN}claude-desktop${NC}"
