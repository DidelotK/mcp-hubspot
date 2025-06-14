# Claude Desktop Integration

## Overview

This guide covers the complete setup process for integrating the HubSpot MCP Server with Claude Desktop application.

## Prerequisites

- Claude Desktop application installed
- HubSpot API key with appropriate permissions
- Python 3.12+ installed
- uv package manager installed

## Setup Steps

### 1. Install Dependencies

First, navigate to your project directory and install the required dependencies:

```bash
cd /path/to/your/mcp-hubspot-project
uv sync
```

This will install all necessary Python packages required for the MCP server to function properly.

### 2. Locate Configuration File

Find the Claude Desktop configuration file based on your operating system:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/claude/claude_desktop_config.json
```

### 3. Development Setup

For development or local installation, add this configuration to your JSON file:

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

**Important:** Replace `/path/to/your/project/` with the actual path to your cloned repository.

### 4. Global Installation Setup

If you have installed the project globally using uv:

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

### 5. Environment Variables

Ensure your HubSpot API key is properly configured:

- **Direct configuration:** Add `HUBSPOT_API_KEY` in the `env` section as shown above
- **System environment:** You can also set it as a system environment variable

### 6. Apply Configuration

After modifying the configuration file:

1. **Save the file** with proper JSON formatting
2. **Completely close** Claude Desktop application
3. **Restart** Claude Desktop
4. **Verify** that HubSpot tools are available in the conversation

## Configuration Validation

### Testing the Connection

Once configured, test the integration by asking Claude:

- "What HubSpot tools are available?"
- "List my HubSpot contacts"
- "Show me HubSpot companies"

### Expected Behavior

When properly configured, Claude should:
- Recognize HubSpot-related requests
- Automatically use the appropriate MCP tools
- Return formatted data from your HubSpot account
- Display tool usage in the conversation

## Configuration Example

Here's a complete `claude_desktop_config.json` example:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "/home/user/projects/mcp-hubspot/main.py",
        "--mode", 
        "stdio"
      ],
      "env": {
        "HUBSPOT_API_KEY": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      }
    }
  }
}
```

## Advanced Configuration

### Custom Script Path

If you need to use a wrapper script or custom startup command:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "/path/to/custom/script.sh",
      "args": [
        "/path/to/project/main.py"
      ],
      "env": {
        "HUBSPOT_API_KEY": "your_hubspot_api_key"
      }
    }
  }
}
```

**Note:** Claude Desktop always uses stdio mode. Port and host configurations are only relevant for SSE mode with other MCP clients.

### Debug Mode

To enable debug logging:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "/path/to/project/main.py",
        "--mode", 
        "stdio"
      ],
      "env": {
        "HUBSPOT_API_KEY": "your_hubspot_api_key",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Security Considerations

- **API Key Security:** Never commit your API key to version control
- **File Permissions:** Ensure the configuration file has appropriate permissions
- **Environment Isolation:** Consider using environment-specific API keys

## Next Steps

After successful configuration:
1. See [Integration Testing](integration-testing.md) for testing guidelines
2. Check [Troubleshooting](troubleshooting.md) if you encounter issues
3. Review [Examples](examples.md) for usage patterns 