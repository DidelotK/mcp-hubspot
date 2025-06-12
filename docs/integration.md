# Integration with MCP Clients

## Integration with Claude Desktop

To use this MCP server with Claude Desktop, follow these steps:

### 1. Claude Desktop Configuration

Edit the Claude Desktop configuration file:

**On macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**On Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**On Linux:**
```bash
~/.config/claude/claude_desktop_config.json
```

### 2. Add MCP Server

Add the following configuration to the JSON file (or copy the provided `claude_desktop_config.example.json` file):

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "/path/to/your/project/main.py",
        "--mode", 
        "stdio"
      ],
      "env": {
        "HUBSPOT_API_KEY": "your_hubspot_api_key"
      }
    }
  }
}
```

### 3. Configuration with globally installed uv

If you have installed the project globally with uv:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "hubspot-mcp-server",
      "env": {
        "HUBSPOT_API_KEY": "your_hubspot_api_key"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After modifying the configuration:
1. Completely close Claude Desktop
2. Restart the application
3. HubSpot tools will be available in Claude

## Integration with Other MCP Clients

### SSE Mode (Server-Sent Events)

To integrate with other MCP clients supporting SSE:

1. **Start the server in SSE mode:**
```bash
uv run python main.py --mode sse --host 127.0.0.1 --port 8080
```

2. **Connect your MCP client to:**
```
http://127.0.0.1:8080
```

### stdio Mode

For clients supporting stdio:

```bash
uv run python main.py --mode stdio
```

The server will communicate via stdin/stdout according to the MCP protocol.

## Integration Testing

Once configured, you can test the tools in Claude using phrases like:

- *"List HubSpot contacts"*
- *"Find companies in the tech sector"*
- *"Show all deals"*
- *"Search for the deal named 'Premium Contract'"*

Claude will automatically use the appropriate MCP tools to respond to your requests.

## Troubleshooting

### Common Issues

**1. Claude doesn't see HubSpot tools**
- Check that the configuration file is in the correct directory
- Make sure the JSON syntax is correct
- Completely restart Claude Desktop
- Check Claude Desktop logs for errors

**2. "Invalid API key" error**
- Verify that your HubSpot API key is correct
- Make sure the key has the necessary permissions (contacts, deals, companies)
- Test the key with the HubSpot API directly

**3. Server won't start**
- Check that Python 3.12+ is installed
- Make sure uv is installed: `pip install uv`
- Verify that all dependencies are installed: `uv sync`

**4. In SSE mode, unable to connect**
- Check that port 8080 is not used by another service
- Test with another port: `--port 8081`
- Check firewall permissions

### Logs and Debugging

To enable detailed logging:

```bash
export PYTHONPATH=/path/to/project
export LOG_LEVEL=DEBUG
uv run python main.py --mode stdio
``` 