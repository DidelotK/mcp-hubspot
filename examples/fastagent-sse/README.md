# FastAgent HubSpot SSE Example

This example demonstrates how to use the HubSpot MCP server with FastAgent through Server-Sent Events (SSE) to create an interactive chat agent with header-based authentication.

## Overview

This setup allows FastAgent to connect to a locally running HubSpot MCP server via SSE instead of stdio. This is useful for:

- Web-based deployments
- Distributed architectures
- Better error handling and connection management
- Authentication via HTTP headers
- Real-time streaming responses

## Architecture

```text
FastAgent Client ←--SSE Connection--→ Local MCP Server ←--API Calls--→ HubSpot API
     (Port 8000)       (HTTP Headers)       (Port 8080)                    (HTTPS)
```

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.12+ and `uv` installed
2. **HubSpot API Key**: Valid HubSpot private app access token
3. **FastAgent**: Install mcp-agent package
4. **Running MCP Server**: Local HubSpot MCP server running in SSE mode

## Setup

### 1. Install Dependencies

```bash
# From the project root
uv sync
```

### 2. Configure Secrets

Copy the example secrets file and fill in your values:

```bash
cd examples/fastagent-sse/
cp fastagent.secrets.example.yaml fastagent.secrets.yaml
```

Edit `fastagent.secrets.yaml` with your actual values:

```yaml
HUBSPOT_API_KEY: "pat-na1-your-actual-hubspot-token-here"
MCP_AUTH_KEY: "your-secure-auth-key-here"
```

### 3. Start the HubSpot MCP Server in SSE Mode

From the project root, start the server with SSE transport:

```bash
# Terminal 1: Start the MCP server in SSE mode
export HUBSPOT_API_KEY="your_hubspot_api_key_here"
export MCP_AUTH_KEY="your_mcp_auth_key_here"
uv run hubspot-mcp-server --mode sse --port 8080 --auth-header
```

The server will start at `http://localhost:8080/sse` with header authentication enabled.

### 4. Run the FastAgent

In a separate terminal:

```bash
# Terminal 2: Start the FastAgent
cd examples/fastagent-sse/
uv run agent.py
```

## Configuration Details

### SSE Connection

The FastAgent connects to the MCP server using:

- **URL**: `http://localhost:8080/sse`
- **Authentication**: Bearer token in `Authorization` header
- **Transport**: Server-Sent Events (SSE)
- **Timeout**: 30 seconds with retry logic

### Authentication

The system uses header-based authentication:

```yaml
headers:
    X-API-Key: "${MCP_AUTH_KEY}"
    Content-Type: "application/json"
    User-Agent: "FastAgent-SSE/1.0"
```

Make sure the `MCP_AUTH_KEY` in your secrets matches the one used by the MCP server.

## Usage

Once both the MCP server and FastAgent are running, you can interact with your HubSpot CRM using natural language:

### Basic Queries

```text
- "Show me the latest 10 contacts"
- "List all companies in the CRM"
- "Find deals created this month"
- "Show me engagements from last week"
```

### Advanced Searches

```text
- "Find deals worth more than $50,000"
- "Search for companies in the technology industry"
- "Show me contacts from France"
- "List closed-won deals from Q4"
```

### Create Operations

```text
- "Create a new deal for Acme Corp worth $25,000"
- "Add a new contact named John Smith with email john@example.com"
```

### Cache and Search Operations

```text
- "Load all contacts into cache and build embeddings"
- "Search semantically for software engineers"
- "Find similar companies to Microsoft"
- "Clear the cache and refresh data"
```

## Troubleshooting

### Connection Issues

1. **Server Not Running**: Ensure the MCP server is running on port 8080

   ```bash
   curl http://localhost:8080/health
   ```

2. **Authentication Failed**: Check that `MCP_AUTH_KEY` matches in both server and client

   ```bash
   curl -H "X-API-Key: your_key" http://localhost:8080/sse
   ```

3. **Port Conflicts**: Change the port in both server startup and `fastagent.config.yaml`

### FastAgent Issues

1. **Module Not Found**: Install FastAgent properly

   ```bash
   pip install mcp-agent
   ```

2. **Configuration Errors**: Validate your YAML files

   ```bash
   python -c "import yaml; yaml.safe_load(open('fastagent.config.yaml'))"
   ```

### HubSpot API Issues

1. **Invalid API Key**: Test your HubSpot API key

   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
   ```

2. **Rate Limiting**: The server handles rate limits automatically

## Advanced Configuration

### Custom Server URL

Modify `fastagent.config.yaml`:

```yaml
mcp:
    servers:
        hubspot-sse:
            transport:
                url: "http://your-server:8080/sse"
```

### Timeout and Retry Settings

```yaml
mcp:
    servers:
        hubspot-sse:
            transport:
                timeout: 60
                retry_attempts: 5
                retry_delay: 3
```

### Additional Headers

```yaml
mcp:
    servers:
        hubspot-sse:
            transport:
                headers:
                    X-API-Key: "${MCP_AUTH_KEY}"
                    X-Client-Version: "1.0.0"
                    X-Environment: "development"
```

## Security Considerations

1. **Keep Secrets Safe**: Never commit `fastagent.secrets.yaml` to version control
2. **Use Strong Auth Keys**: Generate secure random keys for `MCP_AUTH_KEY`
3. **Network Security**: Use HTTPS in production environments
4. **Rotate Keys**: Regularly rotate API keys and auth tokens

## Performance Tips

1. **Enable Caching**: Use the cache operations for frequently accessed data
2. **Batch Operations**: Group multiple requests when possible
3. **Optimize Queries**: Use specific filters to reduce data transfer
4. **Monitor Usage**: Keep an eye on HubSpot API usage limits

## Files Overview

- `agent.py`: Main FastAgent application
- `fastagent.config.yaml`: FastAgent configuration with SSE transport
- `fastagent.secrets.example.yaml`: Template for secrets (copy to `fastagent.secrets.yaml`)
- `README.md`: This documentation file

## Next Steps

- Explore the full range of HubSpot tools available
- Implement custom workflows using FastAgent's capabilities
- Set up production deployment with proper security
- Add monitoring and logging for production use
