# Claude Desktop Integration

This guide provides detailed instructions for integrating Claude Desktop with the HubSpot MCP Server in both **stdio** and **SSE** modes.

## 🔀 Configuration Modes

The HubSpot MCP Server can be used with Claude Desktop in two different ways:

### 🏠 **stdio Mode (Local)**
- Server runs locally and communicates directly with Claude Desktop
- Best for: Personal use, development, simple setup
- Pros: Simple, direct communication, no network dependencies
- Cons: Server must run on same machine as Claude Desktop

### 🌐 **SSE Mode (Remote)**
- Server runs as a web service, Claude Desktop connects via HTTP
- Best for: Production deployments, team usage, remote server setups
- Pros: Server can run anywhere, scalable, multiple clients
- Cons: Requires network connection, more complex authentication

---

## 🏠 stdio Mode Configuration

### Prerequisites

- Python 3.12+
- uv package manager
- HubSpot API key
- Git (for cloning the repository)

### Step 1: Install the MCP Server Prerequisites

```bash
# Clone the repository
git clone https://github.com/DidelotK/mcp-hubspot
cd mcp-hubspot

# Install dependencies
uv sync

# Test the installation
uv run hubspot-mcp-server --help
```

### Step 2: Configure Claude Desktop

**Location**: `~/.config/Claude/claude_desktop_config.json`

Choose the appropriate configuration file from the examples:

| Configuration Type | File | Description |
|-------------------|------|-------------|
| **Standard stdio** | [`claude_desktop_config_stdio.example.json`](../examples/claude/claude_desktop_config_stdio.example.json) | Direct uv command execution |
| **Script-based stdio** | [`claude_desktop_config_stdio_with_launch_script.example.json`](../examples/claude/claude_desktop_config_stdio_with_launch_script.example.json) | Uses wrapper script for easier setup |

**Important**: 
- Copy the example file content to your Claude Desktop configuration
- Replace placeholder values with your actual paths and API keys

### Step 3: Test stdio Configuration

1. **Restart Claude Desktop** : Make sur all process of Claude Desktop are stopped during restart
2. **Check MCP Status**: Look for MCP connection indicators in Claude Desktop
3. **Test Basic Commands**: 
   - "List my HubSpot contacts"
   - "Show my HubSpot deals"
   - "What contact properties are available?"

---

## 🌐 SSE Mode Configuration

### Prerequisites

- Node.js and npm (for mcp-remote)
- Running HubSpot MCP Server in SSE mode
- HubSpot API key
- Network access to the SSE server

### Step 1: Install mcp-remote

```bash
# Install mcp-remote globally
npm install -g mcp-remote

# Or use npx (no installation required)
npx mcp-remote --help
```

### Step 2: Start the SSE Server

#### Local SSE Server (for testing):

```bash
# Clone the repository
git clone https://github.com/DidelotK/mcp-hubspot
cd mcp-hubspot

# Install dependencies
uv sync

# Test the installation
uv run hubspot-mcp-server --help

# Start local SSE server
MCP_AUTH_KEY="your-auth-key-here" \
HUBSPOT_API_KEY="pat-na1-your-actual-api-key-here" \
uv run hubspot-mcp-server --mode sse --host localhost --port 8080
```

#### Remote SSE Server:

For production deployments, follow the [Remote Deployment Guide](installation-remote-sse.md).

### Step 3: Claude Desktop Configuration for SSE

Choose the appropriate SSE configuration file from the examples:

| Configuration Type | File | Description |
|-------------------|------|-------------|
| **Local SSE Server** | [`claude_desktop_config_sse_local.example.json`](../examples/claude/claude_desktop_config_sse_local.example.json) | For local development with SSE mode |
| **Remote SSE Server** | [`claude_desktop_config_sse.example.json`](../examples/claude/claude_desktop_config_sse.example.json) | For production remote SSE servers |

**Important**: 
- Copy the example file content to your Claude Desktop configuration
- Replace placeholder values with your actual server URLs and authentication keys
- For local development, ensure the SSE server is running on the specified port

### Step 4: Test SSE Configuration

1. **Verify Server is Running**:
   ```bash
   curl -H "X-API-Key: your-auth-key" http://localhost:8080/health
   ```

2. **Restart Claude Desktop**

3. **Test MCP Connection**: Try the same commands as in stdio mode

---

## 🔍 Troubleshooting

### stdio Mode Issues

**Server Not Starting**:
```bash
# Check if uv is installed
uv --version

# Test server directly
cd /path/to/mcp-hubspot
uv run hubspot-mcp-server --mode stdio
```

**Environment Variables Not Loading**:
```bash
# Check if direnv is working
direnv status

# Manually source environment
source .env.local
```

**Claude Desktop Not Connecting**:
1. Check Claude Desktop logs
2. Verify absolute paths in configuration
3. Ensure HubSpot API key is valid
4. Restart Claude Desktop

### SSE Mode Issues

**Connection Refused**:
```bash
# Check if server is running
ss -tlnp | grep 8080

# Test server health
curl http://localhost:8080/health
```

**Authentication Errors**:
```bash
# Test with curl
curl -H "X-API-Key: your-key" http://localhost:8080/sse

# Check server logs for authentication details
```

**mcp-remote Issues**:
```bash
# Update mcp-remote
npm update -g mcp-remote

# Test direct connection
npx mcp-remote http://localhost:8080/sse --header "X-API-Key: your-key"
```

---

## 🔐 Security Considerations

### stdio Mode Security

- ✅ Local execution - no network exposure
- ✅ Environment variables isolated to local machine
- ⚠️ API keys stored in configuration files
- ⚠️ Process arguments may be visible in system logs

### SSE Mode Security

- ✅ Authentication required for all endpoints
- ✅ HTTPS in production deployments
- ✅ Environment variables separated from configuration
- ⚠️ Network traffic (use HTTPS in production)
- ⚠️ Authentication keys in network requests

### Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Use HTTPS** for remote SSE deployments
5. **Limit API key permissions** in HubSpot
6. **Monitor access logs** for unusual activity

---

## 🚀 Quick Setup Scripts

### stdio Mode Quick Setup

```bash
#!/bin/bash
# Quick setup for stdio mode

# Set your API key here
HUBSPOT_API_KEY="pat-na1-your-key-here"
PROJECT_PATH="$(pwd)"

# Create Claude Desktop configuration from example
mkdir -p ~/.config/Claude
cp examples/claude/claude_desktop_config_stdio_with_launch_script.example.json ~/.config/Claude/claude_desktop_config.json

# Replace placeholders
sed -i "s|/ABSOLUTE_PATH_TO_YOUR_PROJECT|$PROJECT_PATH|g" ~/.config/Claude/claude_desktop_config.json
sed -i "s|YOUR_HUBSPOT_API_KEY_HERE|$HUBSPOT_API_KEY|g" ~/.config/Claude/claude_desktop_config.json

echo "✅ Claude Desktop configured for stdio mode using example file"
echo "🔄 Please restart Claude Desktop"
```

### SSE Mode Quick Setup

```bash
#!/bin/bash
# Quick setup for SSE mode

# Set your configuration here
HUBSPOT_API_KEY="pat-na1-your-key-here"
MCP_AUTH_KEY="local-test-key"

# Start SSE server in background
echo "🚀 Starting SSE server..."
MCP_AUTH_KEY="$MCP_AUTH_KEY" \
HUBSPOT_API_KEY="$HUBSPOT_API_KEY" \
uv run hubspot-mcp-server --mode sse --host localhost --port 8080 &

# Wait for server to start
sleep 5

# Create Claude Desktop configuration from example
mkdir -p ~/.config/Claude
cp examples/claude/claude_desktop_config_sse_local.example.json ~/.config/Claude/claude_desktop_config.json

# Replace placeholders
sed -i "s|YOUR_HUBSPOT_API_KEY_HERE|$HUBSPOT_API_KEY|g" ~/.config/Claude/claude_desktop_config.json
sed -i "s|local-test-key|$MCP_AUTH_KEY|g" ~/.config/Claude/claude_desktop_config.json

echo "✅ Claude Desktop configured for SSE mode using example file"
echo "🔄 Please restart Claude Desktop" 
echo "🌐 SSE server running on http://localhost:8080"
```
