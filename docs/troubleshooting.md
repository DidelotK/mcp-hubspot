# Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve common issues when integrating the HubSpot MCP Server with various clients.

## Common Issues

### 1. Claude Desktop Integration Issues

#### Claude doesn't see HubSpot tools

**Symptoms:**

- Claude responds with "I don't have access to HubSpot tools"
- No HubSpot-related functionality available
- Tool list is empty or missing HubSpot tools

**Potential Causes & Solutions:**

1. **Incorrect Configuration File Location**

   ```bash
   # Verify the correct path for your OS
   # macOS
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Linux
   ls -la ~/.config/claude/claude_desktop_config.json

   # Windows (in PowerShell)
   ls $env:APPDATA\Claude\claude_desktop_config.json
   ```

2. **Invalid JSON Syntax**

   ```bash
   # Validate JSON syntax
   cat ~/.config/claude/claude_desktop_config.json | jq .
   ```

   **Fix:** Ensure proper JSON formatting with matching brackets and quotes

3. **Incorrect Path to Server**

   ```json
   {
     "mcpServers": {
       "hubspot": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "/correct/absolute/path/to/your/project/scripts/run_mcp_hubspot.sh",
           "--mode",
           "stdio"
         ]
       }
     }
   }
   ```

4. **Claude Desktop Not Restarted**
   - Completely quit Claude Desktop (not just close window)
   - Restart the application
   - Wait for initialization to complete

#### "Invalid API key" error

**Symptoms:**

- Error message: "Authentication failed"
- "Invalid API key" in error responses
- Tools fail to execute with authorization errors

**Solutions:**

1. **Verify API Key Format**

   ```bash
   # HubSpot API keys should start with 'pat-na1-'
   echo $HUBSPOT_API_KEY | grep -E '^pat-na1-'
   ```

2. **Check API Key Permissions**
   - Log into HubSpot
   - Go to Settings > Integrations > Private Apps
   - Verify the API key has required scopes:
     - `crm.objects.contacts.read`
     - `crm.objects.companies.read`
     - `crm.objects.deals.read`

3. **Test API Key Directly**

   ```bash
   curl -H "Authorization: Bearer $HUBSPOT_API_KEY" \
        "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
   ```

4. **Environment Variable Setup**

   ```bash
   # Make sure the API key is properly set
   export HUBSPOT_API_KEY="your-actual-api-key"

   # Or add to Claude Desktop config
   {
     "mcpServers": {
       "hubspot": {
         "env": {
           "HUBSPOT_API_KEY": "your-actual-api-key"
         }
       }
     }
   }
   ```

#### Server won't start

**Symptoms:**

- Claude shows "Server not responding" errors
- No tool responses
- Connection timeouts

**Solutions:**

1. **Check Python Environment**

   ```bash
   # Verify Python version (3.12+ required)
   python --version

   # Check if uv is installed
   uv --version

   # Verify dependencies
   cd /path/to/project
   uv sync
   ```

2. **Test Server Manually**

   ```bash
   # Try starting server manually
   cd /path/to/project
   export HUBSPOT_API_KEY="your-api-key"
   uv run hubspot-mcp-server --mode stdio
   ```

3. **Check for Port Conflicts**

   ```bash
   # If using custom port, check if it's available
   netstat -tulpn | grep 8080
   ```

4. **Verify File Permissions**

   ```bash
   # Ensure the wrapper script is executable
   ls -la /path/to/project/scripts/run_mcp_hubspot.sh
   chmod +x /path/to/project/scripts/run_mcp_hubspot.sh
   ```

### 2. MCP Client Integration Issues

#### SSE Mode Connection Problems

**Symptoms:**

- Unable to connect to `http://127.0.0.1:8080`
- Connection refused errors
- Timeout errors

**Solutions:**

1. **Verify Server is Running**

   ```bash
   # Start server in SSE mode
   uv run hubspot-mcp-server --mode sse --host 127.0.0.1 --port 8080

   # Check if server is listening
   netstat -tulpn | grep 8080
   ```

2. **Test with cURL**

   ```bash
   # Simple connectivity test
   curl -X POST http://127.0.0.1:8080/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
   ```

3. **Check Firewall Settings**

   ```bash
   # Allow port 8080 through firewall (Linux example)
   sudo ufw allow 8080/tcp
   ```

4. **Try Different Port**

   ```bash
   # Use alternative port
   uv run hubspot-mcp-server --mode sse --port 8081
   ```

#### stdio Mode Communication Issues

**Symptoms:**

- No response from stdin/stdout
- Invalid JSON responses
- Broken pipe errors

**Solutions:**

1. **Test Basic Communication**

   ```bash
   # Simple echo test
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | \
     uv run hubspot-mcp-server --mode stdio
   ```

2. **Check Input Format**

   ```bash
   # Ensure proper JSON formatting
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq .
   ```

3. **Verify Environment Variables**

   ```bash
   # Export API key before running
   export HUBSPOT_API_KEY="your-api-key"
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | \
     uv run hubspot-mcp-server --mode stdio
   ```

### 3. API and Network Issues

#### Rate Limiting

**Symptoms:**

- HTTP 429 "Too Many Requests" errors
- Requests failing after working initially
- Temporary API unavailability

**Solutions:**

1. **Implement Request Throttling**

   ```bash
   # Reduce request frequency
   # Add delays between requests in your client
   ```

2. **Check HubSpot API Limits**
   - Review your HubSpot subscription limits
   - Monitor API usage in HubSpot dashboard
   - Consider upgrading subscription if needed

3. **Implement Retry Logic**

   ```python
   import time
   import requests
   from requests.adapters import HTTPAdapter
   from requests.packages.urllib3.util.retry import Retry

   session = requests.Session()
   retry_strategy = Retry(
       total=3,
       backoff_factor=2,
       status_forcelist=[429, 500, 502, 503, 504]
   )
   adapter = HTTPAdapter(max_retries=retry_strategy)
   session.mount("http://", adapter)
   session.mount("https://", adapter)
   ```

#### Network Connectivity Issues

**Symptoms:**

- Timeout errors
- DNS resolution failures
- Connection refused errors

**Solutions:**

1. **Test Network Connectivity**

   ```bash
   # Test HubSpot API connectivity
   ping api.hubapi.com

   # Test HTTPS connectivity
   curl -I https://api.hubapi.com/crm/v3/objects/contacts
   ```

2. **Check DNS Resolution**

   ```bash
   # Verify DNS resolution
   nslookup api.hubapi.com
   dig api.hubapi.com
   ```

3. **Proxy Configuration**

   ```bash
   # If behind corporate proxy
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

### 4. Data and Formatting Issues

#### Missing or Incorrect Data

**Symptoms:**

- Empty responses
- Missing fields in output
- Incorrect data formatting

**Solutions:**

1. **Check HubSpot Data**

   ```bash
   # Verify data exists in HubSpot
   curl -H "Authorization: Bearer $HUBSPOT_API_KEY" \
        "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
   ```

2. **Verify Property Mappings**
   - Check if requested properties exist in HubSpot
   - Ensure property names match exactly
   - Verify data types are compatible

3. **Test with Minimal Request**

   ```bash
   # Test with basic request
   curl -X POST http://127.0.0.1:8080/mcp \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/call",
       "params": {
         "name": "list_hubspot_contacts",
         "arguments": {"limit": 1}
       }
     }'
   ```

#### Encoding Issues

**Symptoms:**

- Garbled text in responses
- Unicode characters not displaying correctly
- Encoding errors in logs

**Solutions:**

1. **Set Proper Encoding**

   ```bash
   # Set UTF-8 encoding
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

2. **Check Terminal Encoding**

   ```bash
   # Verify terminal supports UTF-8
   locale charmap
   ```

3. **Update System Locale**

   ```bash
   # Ubuntu/Debian
   sudo locale-gen en_US.UTF-8
   sudo update-locale LANG=en_US.UTF-8
   ```

## Debugging Tools and Techniques

### 1. Enable Debug Logging

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
uv run hubspot-mcp-server --mode stdio
```

### 2. Use Logging to File

```bash
# Redirect logs to file for analysis
export LOG_LEVEL=DEBUG
uv run hubspot-mcp-server --mode stdio 2> debug.log
```

### 3. Network Debugging

```bash
# Monitor network traffic
sudo tcpdump -i any port 443 and host api.hubapi.com

# Use curl with verbose output
curl -v -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

### 4. JSON Validation

```bash
# Validate JSON requests/responses
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq .

# Pretty print JSON
cat response.json | jq .
```

## Performance Troubleshooting

### 1. Slow Response Times

**Diagnosis:**

```bash
# Test response times
time curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_hubspot_contacts", "arguments": {"limit": 100}}}'
```

**Solutions:**

- Reduce data request size (lower limit)
- Implement caching (see [Caching Guide](caching.md))
- Use pagination for large datasets
- Optimize network connection

### 2. Memory Issues

**Diagnosis:**

```bash
# Monitor memory usage
ps aux | grep python
top -p $(pgrep -f "hubspot-mcp-server")
```

**Solutions:**

- Reduce batch sizes
- Implement streaming for large responses
- Add garbage collection hints
- Check for memory leaks

### 3. CPU Usage

**Diagnosis:**

```bash
# Monitor CPU usage
htop
iotop
```

**Solutions:**

- Optimize data processing
- Use async operations where possible
- Implement request queuing
- Scale horizontally if needed

## Recovery Procedures

### 1. Server Recovery

```bash
# Kill existing server processes
pkill -f "hubspot-mcp-server"

# Clean restart
cd /path/to/project
uv sync
export HUBSPOT_API_KEY="your-api-key"
uv run hubspot-mcp-server --mode sse --port 8080
```

### 2. Configuration Reset

```bash
# Backup current configuration
cp ~/.config/claude/claude_desktop_config.json ~/.config/claude/claude_desktop_config.json.backup

# Reset to minimal configuration
cat > ~/.config/claude/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "hubspot": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/project",
        "hubspot-mcp-server",
        "--mode",
        "stdio"
      ],
      "env": {
        "HUBSPOT_API_KEY": "your_hubspot_api_key"
      }
    }
  }
}
EOF
```

### 3. Dependency Reset

```bash
# Clean and reinstall dependencies
cd /path/to/project
rm -rf .venv
uv sync --reinstall
```

## Getting Help

### 1. Log Collection

Before seeking help, collect relevant logs:

```bash
# Collect system information
uname -a
python --version
uv --version

# Collect error logs
export LOG_LEVEL=DEBUG
uv run hubspot-mcp-server --mode stdio 2> error.log

# Collect configuration
cat ~/.config/claude/claude_desktop_config.json (remove API key)
```

### 2. Error Reporting

When reporting issues, include:

- Operating system and version
- Python version
- Complete error messages
- Steps to reproduce
- Configuration (with API key removed)
- Log files

### 3. Community Resources

- Check project documentation
- Search existing issues on GitHub
- Review [Integration Testing Guide](integration-testing.md)

## Preventive Measures

### 1. Regular Maintenance

```bash
# Weekly maintenance script
#!/bin/bash
cd /path/to/project
git pull origin main
uv sync
uv run python -m pytest tests/
```

### 2. Monitoring

- Set up log rotation
- Monitor API usage
- Track response times
- Watch for error patterns

### 3. Backup and Recovery

- Backup configuration files
- Document custom settings
- Test recovery procedures
- Maintain rollback procedures

## Advanced Troubleshooting

### 1. Packet Capture

```bash
# Capture network traffic for deep analysis
sudo tcpdump -i any -w hubspot_traffic.pcap port 443 and host api.hubapi.com
```

### 2. Strace/Dtrace

```bash
# Trace system calls (Linux)
strace -f -o trace.log uv run hubspot-mcp-server --mode stdio

# Trace on macOS
sudo dtruss -f -o trace.log uv run hubspot-mcp-server --mode stdio
```

### 3. Memory Profiling

```python
# Add to main.py for memory profiling
import tracemalloc
tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```
