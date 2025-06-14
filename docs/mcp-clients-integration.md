# MCP Clients Integration

## Overview

This guide covers integration with MCP (Model Context Protocol) clients other than Claude Desktop, including SSE (Server-Sent Events) and stdio modes.

## Prerequisites and Setup

Before starting, ensure you have:
- Python 3.12+ installed
- uv package manager installed
- HubSpot API key with appropriate permissions

### Install Dependencies

Navigate to your project directory and install dependencies:

```bash
cd /path/to/your/mcp-hubspot-project
uv sync
```

This installs all required Python packages for the MCP server.

## Supported Integration Modes

### 1. SSE Mode (Server-Sent Events)

SSE mode is ideal for web-based applications and clients that support HTTP-based communication.

#### Starting the Server

```bash
uv run hubspot-mcp-server --mode sse --host 127.0.0.1 --port 8080
```

#### Configuration Options

- `--host`: Server host address (default: 127.0.0.1)
- `--port`: Server port (default: 8080)
- `--cors`: Enable CORS for cross-origin requests

#### Example with Custom Configuration

```bash
# Custom host and port
uv run hubspot-mcp-server --mode sse --host 0.0.0.0 --port 9000

# Enable CORS for web applications  
uv run hubspot-mcp-server --mode sse --host 127.0.0.1 --port 8080 --cors
```

#### Client Connection

Connect your MCP client to:
```
http://127.0.0.1:8080
```

### 2. stdio Mode

stdio mode is perfect for command-line tools and applications that communicate via standard input/output.

#### Starting the Server

```bash
uv run hubspot-mcp-server --mode stdio
```

#### Usage in Scripts

The server communicates via stdin/stdout according to the MCP protocol:

```bash
#!/bin/bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uv run hubspot-mcp-server --mode stdio
```

## Environment Configuration

### Required Environment Variables

Set your HubSpot API key before starting the server:

```bash
export HUBSPOT_API_KEY="your_hubspot_api_key"
uv run hubspot-mcp-server --mode sse --port 8080
```

### Optional Environment Variables

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Set custom timeout
export API_TIMEOUT=30

# Configure caching
export CACHE_TTL=300
```

## Integration Examples

### Python Client Example

```python
import json
import requests

# SSE mode client example
class HubSpotMCPClient:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
    
    def list_tools(self):
        response = requests.post(
            f"{self.base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
        )
        return response.json()
    
    def call_tool(self, tool_name, arguments=None):
        response = requests.post(
            f"{self.base_url}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {}
                }
            }
        )
        return response.json()

# Usage
client = HubSpotMCPClient()
tools = client.list_tools()
contacts = client.call_tool("list_hubspot_contacts", {"limit": 10})
```

### Node.js Client Example

```javascript
const axios = require('axios');

class HubSpotMCPClient {
    constructor(baseUrl = 'http://127.0.0.1:8080') {
        this.baseUrl = baseUrl;
    }

    async listTools() {
        const response = await axios.post(`${this.baseUrl}/mcp`, {
            jsonrpc: '2.0',
            id: 1,
            method: 'tools/list'
        });
        return response.data;
    }

    async callTool(toolName, arguments = {}) {
        const response = await axios.post(`${this.baseUrl}/mcp`, {
            jsonrpc: '2.0',
            id: 2,
            method: 'tools/call',
            params: {
                name: toolName,
                arguments: arguments
            }
        });
        return response.data;
    }
}

// Usage
const client = new HubSpotMCPClient();
client.listTools().then(tools => console.log(tools));
client.callTool('list_hubspot_contacts', { limit: 5 })
    .then(contacts => console.log(contacts));
```

### cURL Examples

```bash
# List available tools
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call a tool
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_hubspot_contacts",
      "arguments": {
        "limit": 10,
        "filters": {
          "search": "example"
        }
      }
    }
  }'
```

## Protocol Specifications

### JSON-RPC Protocol

The server follows the MCP protocol based on JSON-RPC 2.0:

#### Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "method_name",
  "params": {
    "parameter": "value"
  }
}
```

#### Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "data": "response_data"
  }
}
```

#### Error Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32000,
    "message": "Error description"
  }
}
```

### Available Methods

- `tools/list`: Get list of available tools
- `tools/call`: Execute a specific tool
- `resources/list`: Get available resources
- `resources/read`: Read a specific resource

## Performance Considerations

### Connection Pooling

For high-volume applications, use connection pooling:

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

### Async Operations

For async operations in Python:

```python
import aiohttp
import asyncio

async def async_mcp_call():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://127.0.0.1:8080/mcp',
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
        ) as response:
            return await response.json()

# Usage
tools = asyncio.run(async_mcp_call())
```

## Security Considerations

### Network Security

- Use HTTPS in production environments
- Implement proper authentication
- Configure firewall rules appropriately

### API Key Management

- Never expose API keys in client-side code
- Use environment variables or secure configuration
- Implement API key rotation policies

## Next Steps

1. Review [Integration Testing](integration-testing.md) for testing your integration
2. Check [Troubleshooting](troubleshooting.md) for common issues
3. See [API Reference](api-reference.md) for detailed tool documentation 