# Integration Guide

## Overview

This guide provides a comprehensive overview of integrating the HubSpot MCP Server with various clients and platforms. The integration documentation has been organized into dedicated guides for easier navigation and reference.

## Integration Types

### 🖥️ Claude Desktop Integration

The most common integration method for individual users and development work.

**Key Features:**
- Native Claude Desktop support
- Simple JSON configuration
- Environment variable management
- Automatic tool discovery

**Quick Start:**
Configure Claude Desktop by adding the server to your configuration file with your HubSpot API key.

📖 **[Complete Claude Desktop Integration Guide →](claude-desktop-integration.md)**

---

### 🔌 MCP Clients Integration

Integration with other Model Context Protocol clients and custom applications.

**Supported Modes:**
- **SSE Mode**: HTTP-based communication for web applications
- **stdio Mode**: Standard input/output for command-line tools and scripts

**Key Features:**
- RESTful API endpoints
- JSON-RPC 2.0 protocol
- Cross-platform compatibility
- Custom client development support

**Quick Start:**
Start the server in SSE mode and connect via HTTP, or use stdio mode for direct communication.

📖 **[Complete MCP Clients Integration Guide →](mcp-clients-integration.md)**

---

### 🧪 Integration Testing

Comprehensive testing procedures to verify your integration works correctly.

**Testing Coverage:**
- Claude Desktop functionality tests
- MCP client communication tests
- Error handling and edge cases
- Performance and load testing
- Automated testing scripts

**Key Features:**
- Step-by-step testing procedures
- Expected response validation
- Automated test scripts (Python & Bash)
- CI/CD integration examples

**Quick Start:**
Use the provided test scripts to validate your integration setup and functionality.

📖 **[Complete Integration Testing Guide →](integration-testing.md)**

---

### 🔧 Troubleshooting

Diagnose and resolve common integration issues across all platforms.

**Common Issues Covered:**
- Claude Desktop tool recognition problems
- API authentication failures
- Network connectivity issues
- Performance and memory problems
- Configuration and setup errors

**Key Features:**
- Symptom-based problem identification
- Step-by-step solution procedures
- Advanced debugging techniques
- Recovery and maintenance procedures

**Quick Start:**
Identify your issue symptoms and follow the corresponding troubleshooting steps.

📖 **[Complete Troubleshooting Guide →](troubleshooting.md)**

## Getting Started

### Prerequisites

Before integrating, ensure you have:

- [ ] **HubSpot API Key**: Valid private app API key with required permissions
- [ ] **Python 3.12+**: Required runtime environment
- [ ] **uv Package Manager**: For dependency management
- [ ] **Network Access**: Connectivity to HubSpot API endpoints

### Quick Integration Path

1. **Choose Your Integration Type**
   - For Claude Desktop → [Claude Desktop Guide](claude-desktop-integration.md)
   - For custom clients → [MCP Clients Guide](mcp-clients-integration.md)

2. **Configure Your Environment**
   - Set up your HubSpot API key
   - Install dependencies
   - Configure your chosen client

3. **Test Your Integration**
   - Follow the [Testing Guide](integration-testing.md)
   - Validate functionality
   - Run automated tests

4. **Troubleshoot if Needed**
   - Check [Troubleshooting Guide](troubleshooting.md)
   - Review common issues
   - Apply solutions

## Integration Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude        │    │   Custom MCP    │    │   Web           │
│   Desktop       │    │   Client        │    │   Application   │
└─────┬───────────┘    └─────┬───────────┘    └─────┬───────────┘
      │                      │                      │
      │ stdio                │ stdio                │ HTTP/SSE
      │                      │                      │
┌─────▼──────────────────────▼──────────────────────▼───────────┐
│              HubSpot MCP Server                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   Tool Handler  │  │  Format Engine  │  │  Cache Manager  ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────┬─────────────────────────────────┘
                              │ HTTPS
                              │
                    ┌─────────▼─────────┐
                    │   HubSpot API     │
                    │   (api.hubapi.com)│
                    └───────────────────┘
```

## Available Tools

The server provides these HubSpot integration tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_hubspot_contacts` | List and search contacts | `limit`, `filters` |
| `list_hubspot_companies` | List and search companies | `limit`, `filters` |
| `list_hubspot_deals` | List and search deals | `limit`, `filters` |

## Configuration Examples

### Environment Variables

```bash
# Required
export HUBSPOT_API_KEY="pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Optional
export LOG_LEVEL="INFO"
export CACHE_TTL="300"
export API_TIMEOUT="30"
```

### Basic Usage Examples

**List Contacts:**
```
"List my HubSpot contacts"
"Show me the first 10 contacts"
"Find contacts with 'john' in their name"
```

**List Companies:**
```
"Show me HubSpot companies"
"Find tech companies in HubSpot"
"List companies with 'software' in their name"
```

**List Deals:**
```
"Show me all deals"
"Find deals worth more than $10,000"
"List deals in the negotiation stage"
```

## Security Considerations

### API Key Management

- **Never commit API keys** to version control
- **Use environment variables** for key storage
- **Rotate API keys** regularly
- **Limit API key permissions** to required scopes only

### Network Security

- **Use HTTPS** in production environments
- **Configure firewalls** appropriately
- **Implement rate limiting** to prevent abuse
- **Monitor API usage** for unusual patterns

## Performance Optimization

### Caching

The server implements intelligent caching to improve performance:
- Contact data cached for 5 minutes
- Company data cached for 15 minutes
- Deal data cached for 10 minutes

See [Caching Guide](caching.md) for detailed configuration.

### Request Optimization

- Use appropriate `limit` parameters
- Implement pagination for large datasets
- Use specific search filters when possible
- Monitor HubSpot API rate limits

## Support and Resources

### Documentation Links

- [Installation Guide](installation.md) - Initial setup and installation
- [API Reference](api-reference.md) - Detailed API documentation
- [Examples](examples.md) - Usage examples and code samples
- [Contributing](contributing.md) - Development and contribution guidelines

### Community and Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and references
- **Code Examples**: Working examples for common use cases

## Next Steps

1. **Choose your integration method** from the guides above
2. **Follow the step-by-step instructions** in the relevant guide
3. **Test your integration** using the testing procedures
4. **Refer to troubleshooting** if you encounter issues
5. **Explore advanced features** in the API reference

Each integration guide provides complete, self-contained instructions for successful setup and operation. 