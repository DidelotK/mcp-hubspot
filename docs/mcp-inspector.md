# MCP Inspector Integration

This guide explains how to use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to debug and test the HubSpot MCP server.

## 🔍 What is MCP Inspector?

The MCP Inspector is a visual testing tool for MCP servers that provides:
- **Interactive UI** for testing MCP tools and schemas
- **Real-time debugging** of server communications
- **CLI mode** for automation and scripting
- **Multiple transport support** (stdio, SSE, HTTP)

## 🚀 Quick Start

### 1. Basic Inspector (Manual Configuration)

```bash
just inspect
```

This starts the MCP Inspector without any pre-configuration. You'll need to manually configure the server.

### 2. Pre-configured Inspector

```bash
just inspect-config
```

This starts the inspector with our `mcp.json` configuration file, providing these pre-configured servers:
- `hubspot-stdio` - Standard stdio mode
- `hubspot-sse` - SSE mode with authentication
- `hubspot-sse-no-auth` - SSE mode without authentication  
- `hubspot-script` - Using the wrapper script

### 3. Direct stdio Server Launch

```bash
just inspect-stdio
```

This directly launches the inspector with the HubSpot stdio server configuration.

## 📋 Configuration File (mcp.json)

Our project includes a pre-configured `mcp.json` file with four server configurations:

### hubspot-stdio
```json
{
  "command": "uv",
  "args": ["run", "hubspot-mcp-server", "--mode", "stdio"],
  "env": {
    "HUBSPOT_API_KEY": "YOUR_HUBSPOT_API_KEY_HERE"
  }
}
```

### hubspot-sse
```json
{
  "command": "uv",
  "args": ["run", "hubspot-mcp-server", "--mode", "sse", "--host", "localhost", "--port", "8080"],
  "env": {
    "HUBSPOT_API_KEY": "YOUR_HUBSPOT_API_KEY_HERE",
    "MCP_AUTH_KEY": "local-test-key"
  }
}
```

### hubspot-sse-no-auth
```json
{
  "command": "uv",
  "args": ["run", "hubspot-mcp-server", "--mode", "sse", "--host", "localhost", "--port", "8081"],
  "env": {
    "HUBSPOT_API_KEY": "YOUR_HUBSPOT_API_KEY_HERE"
  }
}
```

### hubspot-script
```json
{
  "command": "./scripts/run_mcp_hubspot.sh",
  "args": ["--mode", "stdio"],
  "env": {
    "HUBSPOT_API_KEY": "YOUR_HUBSPOT_API_KEY_HERE"
  }
}
```

## 🔧 Setup Instructions

### 1. Set Your HubSpot API Key

Before using any configuration, update the `HUBSPOT_API_KEY` in `mcp.json`:

```bash
# Edit mcp.json and replace YOUR_HUBSPOT_API_KEY_HERE with your actual API key
sed -i 's/YOUR_HUBSPOT_API_KEY_HERE/pat-na1-your-actual-key-here/g' mcp.json
```

Or edit the file manually:
```bash
# Using your preferred editor
vim mcp.json
# or
code mcp.json
```

### 2. Choose Your Configuration Method

#### Option A: Environment Variables (Recommended)
Keep `mcp.json` with placeholder and use environment variables:

```bash
export HUBSPOT_API_KEY="pat-na1-your-actual-key-here"
just inspect-config
```

#### Option B: Direct File Editing
Edit `mcp.json` directly with your API key (be careful not to commit it).

## 🎯 Using the Inspector

### 1. Start the Inspector

```bash
just inspect-config
```

### 2. Select Server Configuration

In the Inspector UI:
1. Click **"Configuration"** in the sidebar
2. Select **"hubspot-stdio"** from the server dropdown
3. Click **"Connect"**

### 3. Test Available Tools

The inspector will show all available HubSpot MCP tools:
- `list_hubspot_contacts`
- `list_hubspot_companies` 
- `list_hubspot_deals`
- `search_hubspot_deals`
- `create_deal`
- `update_deal`
- `get_deal_by_name`
- `get_hubspot_contact_properties`
- `get_hubspot_company_properties`
- `get_hubspot_deal_properties`
- `list_hubspot_engagements`
- `semantic_search_hubspot`
- `manage_hubspot_embeddings`
- `manage_hubspot_cache`

### 4. Test Tool Execution

1. Select a tool from the list (e.g., `list_hubspot_contacts`)
2. Fill in any required parameters
3. Click **"Execute"**
4. View the response in the output panel

## 🔍 Debugging Features

### Real-time Communication

The inspector shows:
- **Request/Response** cycles in real-time
- **Error messages** with detailed stack traces
- **Performance metrics** for each operation
- **JSON schema validation** results

### Interactive Testing

- **Form-based parameter input** for tools
- **JSON editor** for complex parameters
- **Response visualization** with syntax highlighting
- **Export functionality** for requests/responses

### Advanced Features

- **Request history** for repeated testing
- **Response comparison** between different configurations
- **Streaming support** for progress notifications
- **Authentication testing** for SSE mode

## 🚀 CLI Mode Usage

For automation and scripting, use CLI mode:

```bash
# List available tools
npx @modelcontextprotocol/inspector --cli \
  --config mcp.json --server hubspot-stdio \
  --method tools/list

# Execute a specific tool
npx @modelcontextprotocol/inspector --cli \
  --config mcp.json --server hubspot-stdio \
  --method tools/call \
  --tool-name list_hubspot_contacts \
  --tool-arg limit=5

# Test with SSE mode
npx @modelcontextprotocol/inspector --cli \
  --config mcp.json --server hubspot-sse \
  --method tools/list
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Server not found" error**
   - Ensure `uv` is installed and in PATH
   - Verify the project is properly set up (`uv sync`)

2. **"Invalid API key" error**
   - Check your HubSpot API key is correct
   - Verify the key has the required CRM permissions

3. **"Port already in use" for SSE mode**
   - Use `hubspot-sse-no-auth` on port 8081
   - Or modify the port in `mcp.json`

4. **Authentication errors in SSE mode**
   - Use `hubspot-sse-no-auth` for testing
   - Check `MCP_AUTH_KEY` is set correctly

### Debug Tips

- Use **stdio mode** for simplest debugging
- Check the **console logs** in the inspector
- Use **CLI mode** for reproducible testing
- Compare responses between **different configurations**

## 📚 Additional Resources

- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [HubSpot API Documentation](https://developers.hubspot.com/docs/api/overview)

## 🔗 Integration with Development Workflow

The MCP Inspector integrates well with your development workflow:

1. **During Development**: Use `just inspect-stdio` for quick testing
2. **During Debugging**: Use the UI mode for visual debugging
3. **In CI/CD**: Use CLI mode for automated testing
4. **For Documentation**: Export configurations and responses 