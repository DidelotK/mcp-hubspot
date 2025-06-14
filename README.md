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
uv run hubspot-mcp-server --mode stdio
```

## 📚 Documentation

| Section | Description |
|---------|-------------|
| **[Installation](docs/installation.md)** | Installation and configuration guide |
| **[Integration](docs/integration.md)** | Configuration with Claude Desktop and other MCP clients |
| **[API Reference](docs/api-reference.md)** | Complete documentation of the 14 available tools |
| **[Semantic Search](docs/semantic-search.md)** | AI-powered semantic search capabilities and usage |
| **[Developer Guide](docs/developer.md)** | Testing, quality assurance, and development workflow |
| **[Cache System](docs/caching.md)** | How the shared TTL cache works and how to manage it |
| **[Examples](docs/examples.md)** | Use cases and example conversations with Claude |
| **[Contributing](docs/contributing.md)** | Guide for developing new tools |

## 🧪 Practical Examples

| Example | Description |
|---------|-------------|
| **[Basic Test](examples/basic/)** | Python script to test the MCP server with a client |
| **[FastAgent Chat](examples/fastagent/)** | Interactive chat agent using FastAgent SDK |

## 🛠️ Available Tools

| Tool | Description |
|-------|-------------|
| `list_hubspot_contacts` | List HubSpot contacts with pagination support |
| `get_hubspot_contact_properties` | Retrieve contact field properties with types and descriptions |
| `list_hubspot_companies` | List HubSpot companies with pagination support |
| `get_hubspot_company_properties` | Retrieve company field properties with types and descriptions |
| `list_hubspot_deals` | List HubSpot deals with pagination support |
| `search_hubspot_deals` | Advanced search for deals via HubSpot CRM Search API |
| `create_deal` | Create a new deal in HubSpot |
| `update_deal` | Update an existing deal in HubSpot |
| `get_deal_by_name` | Search for a deal by exact name |
| `get_hubspot_deal_properties` | Retrieve deal field properties with types and descriptions |
| `list_hubspot_engagements` | List HubSpot engagements with pagination support |
| `manage_hubspot_cache` | View statistics or clear the shared TTL cache |
| `semantic_search_hubspot` | AI-powered semantic search across all HubSpot entities using natural language |
| `manage_hubspot_embeddings` | Manage embedding indexes for semantic search (build, clear, stats) |

## ⚡ Usage

Once configured, use natural language phrases:

- *"List my HubSpot contacts"*
- *"Find tech sector companies"*
- *"Show current deals"*
- *"Create a new deal for Project X"*
- *"Search for the 'Project X' deal"*
- *"What contact properties are available?"*
- *"Find software engineers using semantic search"*
- *"Search for technology companies in Paris"*

## 🤖 AI-Powered Semantic Search

The server includes advanced **semantic search capabilities** powered by FAISS and sentence transformers, enabling natural language queries across your HubSpot data.

**Key Features:**
- 🔍 **Natural Language Queries**: Find *"software engineers"* → matches "Developer", "Programmer", "Software Architect"
- 🎯 **Context-Aware**: Search *"enterprise clients"* → finds large companies without exact keyword matches
- 🌐 **Multi-Entity Search**: Search across contacts, companies, deals, and engagements simultaneously
- 🔄 **Hybrid Modes**: Combines AI similarity with traditional API filters

**Quick Start:**
```json
// 1. Build embeddings index
{"name": "manage_hubspot_embeddings", "arguments": {"action": "build"}}

// 2. Perform semantic search
{"name": "semantic_search_hubspot", "arguments": {"query": "technology companies in Paris"}}
```

→ **[Complete Semantic Search Guide](docs/semantic-search.md)** - Detailed usage, examples, and configuration

## 🧪 Testing and Quality

Run all quality checks with a single command:

```bash
just check
```

This performs code formatting, linting, type checking, full test suite, and security scanning.

**Current Status:** ✅ 140+ tests passed, comprehensive coverage including AI/embedding functionality

→ **[Developer Guide](docs/developer.md)** - Complete testing procedures, quality standards, and development workflow

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Useful Links:**
- [Claude Desktop Configuration](docs/integration.md#integration-with-claude-desktop)
- [Usage Examples](docs/examples.md#example-conversations)
- [Complete Tool Reference](docs/api-reference.md)
- [Troubleshooting](docs/integration.md#troubleshooting)

## 🗄️ Cache System

The server uses a **shared in-memory TTL cache** (5-minute default) for all read-only HubSpot calls.  
Benefits:

* 🚀 Faster responses on repeated queries (cache hits)
* 🔄 Automatic refresh every 5 minutes (configurable)
* 🔐 Isolated by API key – no data leaks between accounts

You can interact with the cache via the `manage_hubspot_cache` tool:

```json
{
  "name": "manage_hubspot_cache",
  "arguments": {"action": "info"}
}
```

Actions:

| Action | Description |
|--------|-------------|
| `info` | Show cache size, TTL, utilization and sample keys |
| `clear` | Immediately empty the cache and fetch fresh data on next call |

See full details in [docs/caching.md](docs/caching.md).
