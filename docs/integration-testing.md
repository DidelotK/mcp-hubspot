# Integration Testing Guide

## Overview

This guide provides comprehensive testing procedures to verify that your HubSpot MCP Server integration is working correctly across different clients and configurations.

## Pre-Testing Checklist

Before starting integration tests, ensure:

- [ ] HubSpot API key is valid and has appropriate permissions
- [ ] Server starts without errors
- [ ] All dependencies are properly installed
- [ ] Environment variables are correctly set
- [ ] Network connectivity to HubSpot API is available

## Claude Desktop Testing

### Initial Connection Test

1. **Verify Configuration**
   ```bash
   # Check if configuration file exists and is valid JSON
   cat ~/.config/claude/claude_desktop_config.json | jq .
   ```

2. **Test Basic Connectivity**
   
   Ask Claude: *"What HubSpot tools are available?"*
   
   **Expected Response:**
   Claude should list available tools like:
   - `list_hubspot_contacts`
   - `list_hubspot_companies`
   - `list_hubspot_deals`

### Functional Testing

#### Contact Management Tests

1. **List Contacts**
   ```
   User: "List my HubSpot contacts"
   Expected: Formatted list of contacts with names, emails, and IDs
   ```

2. **Search Contacts**
   ```
   User: "Find HubSpot contacts with 'john' in their name"
   Expected: Filtered list of contacts matching the search term
   ```

3. **Limit Results**
   ```
   User: "Show me the first 5 HubSpot contacts"
   Expected: Exactly 5 contacts displayed
   ```

#### Company Management Tests

1. **List Companies**
   ```
   User: "Show me HubSpot companies"
   Expected: Formatted list of companies with names, domains, and IDs
   ```

2. **Search Companies**
   ```
   User: "Find companies in the tech industry"
   Expected: Filtered list based on industry property
   ```

#### Deal Management Tests

1. **List Deals**
   ```
   User: "List my HubSpot deals"
   Expected: Formatted list of deals with names, amounts, and stages
   ```

2. **Filter Deals**
   ```
   User: "Show me deals worth more than $10,000"
   Expected: Deals filtered by amount
   ```

### Error Handling Tests

1. **Invalid API Key**
   - Temporarily set an invalid API key
   - Expected: Clear error message about authentication failure

2. **Network Issues**
   - Disconnect from internet during a request
   - Expected: Timeout or network error message

3. **Invalid Parameters**
   - Request with invalid limit (e.g., negative number)
   - Expected: Validation error message

## MCP Clients Testing

### SSE Mode Testing

#### Server Startup Test

```bash
# Start server in SSE mode
uv run python main.py --mode sse --host 127.0.0.1 --port 8080
```

**Expected Output:**
```
Starting HubSpot MCP Server in SSE mode
Server listening on http://127.0.0.1:8080
```

#### Tools List Test

```bash
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "list_hubspot_contacts",
        "description": "Lists HubSpot contacts with filtering capability"
      }
    ]
  }
}
```

#### Tool Execution Test

```bash
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_hubspot_contacts",
      "arguments": {"limit": 5}
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": [
    {
      "type": "text",
      "text": "🧑‍💼 **HubSpot Contacts** (5 found)\n\n**John Doe**\n..."
    }
  ]
}
```

### stdio Mode Testing

#### Basic Communication Test

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uv run python main.py --mode stdio
```

**Expected Output:**
Valid JSON response with available tools

#### Tool Execution Test

```bash
echo '{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "list_hubspot_contacts",
    "arguments": {"limit": 3}
  }
}' | uv run python main.py --mode stdio
```

**Expected Output:**
JSON response with formatted contact data

## Performance Testing

### Response Time Tests

1. **Small Datasets (< 100 records)**
   - Expected response time: < 2 seconds
   - Test with `{"limit": 10}`

2. **Medium Datasets (100-500 records)**
   - Expected response time: < 5 seconds
   - Test with `{"limit": 100}`

3. **Large Datasets (500+ records)**
   - Expected response time: < 10 seconds
   - Test with `{"limit": 1000}`

### Load Testing

#### Concurrent Requests Test

```bash
# Create multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://127.0.0.1:8080/mcp \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "id": '$i', "method": "tools/list"}' &
done
wait
```

**Expected Behavior:**
- All requests should complete successfully
- Response times should remain reasonable
- No server crashes or errors

## Data Validation Testing

### Contact Data Validation

Verify that returned contact data includes:
- [ ] Valid contact ID
- [ ] Email address (if available)
- [ ] First name and last name
- [ ] Creation and modification dates
- [ ] Proper formatting with emojis

### Company Data Validation

Verify that returned company data includes:
- [ ] Valid company ID
- [ ] Company name
- [ ] Domain (if available)
- [ ] Industry information
- [ ] Creation and modification dates

### Deal Data Validation

Verify that returned deal data includes:
- [ ] Valid deal ID
- [ ] Deal name
- [ ] Amount (if available)
- [ ] Deal stage
- [ ] Close date (if available)

## Error Scenarios Testing

### API Errors

1. **Rate Limiting**
   ```bash
   # Make many rapid requests to trigger rate limiting
   for i in {1..100}; do
     curl -X POST http://127.0.0.1:8080/mcp \
       -H "Content-Type: application/json" \
       -d '{"jsonrpc": "2.0", "id": '$i', "method": "tools/call", "params": {"name": "list_hubspot_contacts"}}'
   done
   ```
   
   **Expected:** Rate limit error with proper error message

2. **Invalid Tool Parameters**
   ```bash
   curl -X POST http://127.0.0.1:8080/mcp \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/call",
       "params": {
         "name": "list_hubspot_contacts",
         "arguments": {"limit": -1}
       }
     }'
   ```
   
   **Expected:** Validation error for negative limit

### Network Errors

1. **Timeout Testing**
   - Set very low timeout values
   - Expected: Timeout error with clear message

2. **DNS Resolution**
   - Test with invalid HubSpot API endpoints
   - Expected: DNS resolution error

## Automated Testing Scripts

### Python Test Script

```python
#!/usr/bin/env python3
"""Integration test suite for HubSpot MCP Server."""

import json
import requests
import subprocess
import time
import sys

def test_sse_mode():
    """Test SSE mode functionality."""
    print("Testing SSE mode...")
    
    # Start server (you might want to do this in a separate process)
    base_url = "http://127.0.0.1:8080"
    
    try:
        # Test tools list
        response = requests.post(
            f"{base_url}/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                print("✅ Tools list test passed")
                return True
            else:
                print("❌ Tools list test failed: Invalid response format")
                return False
        else:
            print(f"❌ Tools list test failed: HTTP {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ SSE mode test failed: {e}")
        return False

def test_tool_execution():
    """Test tool execution."""
    print("Testing tool execution...")
    
    base_url = "http://127.0.0.1:8080"
    
    try:
        response = requests.post(
            f"{base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "list_hubspot_contacts",
                    "arguments": {"limit": 5}
                }
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                print("✅ Tool execution test passed")
                return True
            else:
                print("❌ Tool execution test failed: No result in response")
                return False
        else:
            print(f"❌ Tool execution test failed: HTTP {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Tool execution test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting HubSpot MCP Server integration tests...\n")
    
    tests = [
        test_sse_mode,
        test_tool_execution
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
```

### Bash Test Script

```bash
#!/bin/bash
# Integration test script for HubSpot MCP Server

echo "Starting HubSpot MCP Server integration tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
TOTAL=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    TOTAL=$((TOTAL + 1))
    
    if eval "$test_command" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ $test_name passed${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ $test_name failed${NC}"
    fi
    echo
}

# Test tools list
run_test "Tools List" \
    "curl -s -X POST http://127.0.0.1:8080/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\"}'" \
    "list_hubspot_contacts"

# Test contact listing
run_test "Contact Listing" \
    "curl -s -X POST http://127.0.0.1:8080/mcp -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 2, \"method\": \"tools/call\", \"params\": {\"name\": \"list_hubspot_contacts\", \"arguments\": {\"limit\": 5}}}'" \
    "HubSpot Contacts"

# Summary
echo "Tests completed: $PASSED/$TOTAL passed"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
```

## Troubleshooting Test Failures

### Common Issues and Solutions

1. **Server Not Starting**
   - Check if port is already in use: `netstat -tulpn | grep 8080`
   - Verify Python environment: `which python`
   - Check dependencies: `uv sync`

2. **API Authentication Errors**
   - Verify API key format: Should start with `pat-na1-`
   - Check API key permissions in HubSpot
   - Test API key directly: `curl -H "Authorization: Bearer $HUBSPOT_API_KEY" https://api.hubapi.com/crm/v3/objects/contacts`

3. **Timeout Errors**
   - Increase timeout values in tests
   - Check network connectivity
   - Verify HubSpot API status

4. **Data Format Issues**
   - Check if returned data matches expected schema
   - Verify emoji rendering in formatted output
   - Ensure proper JSON structure

## Continuous Integration Testing

### GitHub Actions Example

```yaml
name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync
    
    - name: Start MCP Server
      run: |
        uv run python main.py --mode sse --port 8080 &
        sleep 5
      env:
        HUBSPOT_API_KEY: ${{ secrets.HUBSPOT_API_KEY }}
    
    - name: Run integration tests
      run: |
        python tests/integration_tests.py
```

## Best Practices

1. **Test Environment Isolation**
   - Use separate HubSpot accounts for testing
   - Implement test data cleanup procedures
   - Use environment-specific configurations

2. **Comprehensive Coverage**
   - Test all available tools
   - Cover error scenarios
   - Test different parameter combinations

3. **Performance Monitoring**
   - Track response times
   - Monitor memory usage
   - Check for resource leaks

4. **Documentation**
   - Keep test documentation updated
   - Document expected behaviors
   - Record known issues and workarounds 