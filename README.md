# HubSpot MCP Server

MCP (Model Context Protocol) server for integrating HubSpot with Claude Desktop and other MCP clients. Provides access to HubSpot contacts, companies, and deals through conversational tools.

## 🚀 Quick Start

```bash
# Installation
git clone <repo-url>
cd hubspot-mcp-server
uv sync

# Configuration
export HUBSPOT_API_KEY="your_api_key"

# Start
uv run python main.py --mode stdio
```

## 📚 Documentation

| Section | Description |
|---------|-------------|
| **[Installation](docs/installation.md)** | Installation and configuration guide |
| **[Integration](docs/integration.md)** | Configuration with Claude Desktop and other MCP clients |
| **[API Reference](docs/api-reference.md)** | Complete documentation of the 9 available tools |
| **[Examples](docs/examples.md)** | Use cases and example conversations with Claude |
| **[Contributing](docs/contributing.md)** | Guide for developing new tools |

## 🧪 Practical Examples

| Example | Description |
|---------|-------------|
| **[Basic Test](examples/basic/)** | Python script to test the MCP server with a client |

## 🛠️ Available Tools

| Tool | Description |
|-------|-------------|
| `list_hubspot_contacts` | List and filter HubSpot contacts |
| `list_hubspot_companies` | List and filter HubSpot companies |
| `list_hubspot_deals` | List and filter HubSpot deals |
| `create_deal` | Create a new deal in HubSpot |
| `update_deal` | Update an existing deal in HubSpot |
| `get_deal_by_name` | Search for a deal by exact name |
| `get_hubspot_contact_properties` | Retrieve contact field properties with types and descriptions |
| `get_hubspot_company_properties` | Retrieve company field properties with types and descriptions |
| `get_hubspot_deal_properties` | Retrieve deal field properties with types and descriptions |

## ⚡ Usage with Claude

Once configured, use natural language phrases:

- *"List my HubSpot contacts"*
- *"Find tech sector companies"*
- *"Show current deals"*
- *"Create a new deal for Project X"*
- *"Search for the 'Project X' deal"*
- *"What contact properties are available?"*

## 🧪 Testing and Quality

```bash
# Run tests
uv run pytest

# Code coverage
uv run pytest --cov=src --cov-report=html
```

**Current Status:** ✅ 79 tests passed, 96% coverage

## 📋 Prerequisites

- Python 3.12+
- uv (package manager)
- HubSpot API key with CRM permissions

## 🤝 Contributing

Check the [contributing guide](docs/contributing.md) for:
- Development standards
- Tool creation process
- Code and testing conventions
- Git workflow and semantic versioning

## 📄 License

[Project License]

---

**Useful Links:**
- [Claude Desktop Configuration](docs/integration.md#integration-with-claude-desktop)
- [Usage Examples](docs/examples.md#example-conversations)
- [Complete Tool Reference](docs/api-reference.md)
- [Troubleshooting](docs/integration.md#troubleshooting)
