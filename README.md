# HubSpot MCP Server

MCP (Model Context Protocol) server for integrating HubSpot with MCP clients (like Claude Desktop). Provides access to HubSpot contacts, companies, and deals through conversational tools.

## 🛠️ Available Tools

The server provides **14 tools** for comprehensive HubSpot integration:

| Category | Tools | Description |
|----------|--------|-------------|
| **Contacts** | `list_hubspot_contacts`<br/>`get_hubspot_contact_properties` | List contacts and retrieve contact field properties |
| **Companies** | `list_hubspot_companies`<br/>`get_hubspot_company_properties` | List companies and retrieve company field properties |
| **Deals** | `list_hubspot_deals`<br/>`search_hubspot_deals`<br/>`create_deal`<br/>`update_deal`<br/>`get_deal_by_name`<br/>`get_hubspot_deal_properties` | Complete deal management and search capabilities |
| **Engagements** | `list_hubspot_engagements` | List HubSpot engagements with pagination support |
| **AI Search** | `semantic_search_hubspot`<br/>`manage_hubspot_embeddings` | AI-powered semantic search using natural language |
| **System** | `manage_hubspot_cache` | Cache management and statistics |

A complete documentation of the tools can be found here : [Tools documentation](docs/tools.md)

---

## ⚡ Usage Examples

**Once fully installed and configured** (following the complete installation guides), use natural language phrases with your MCP client:

### 🗣️ **Natural Language Queries**

- *"List my HubSpot contacts"*
- *"Find tech sector companies"*
- *"Show current deals"*
- *"Create a new deal for Project X"*
- *"Search for the 'Project X' deal"*
- *"What contact properties are available?"*

### 🤖 **AI-Powered Semantic Search**

- *"Find software engineers"* → matches "Developer", "Programmer", "Software Architect"
- *"Search for enterprise clients"* → finds large companies without exact keywords
- *"Technology companies in Paris"* → contextual location and industry search

A complete documentation of the differents usage can be found here : [Usage examples](docs/usage-examples.md)

---

## 📚 Documentation Table of Contents

### 🚀 Getting Started

| Section | Description |
|---------|-------------|
| **[Client Integration](docs/integration.md)** | Complete Guide for MCP Client Integration |
| **[Claude Desktop Integration](docs/claude-desktop-integration.md)** | Complete guide for stdio and SSE modes with Claude Desktop |

### 🔧 Extra Features

| Section | Description |
|---------|-------------|
| **[Semantic Search](docs/semantic-search.md)** | AI-powered semantic search capabilities and usage |
| **[Cache System](docs/caching.md)** | How the shared TTL cache works and how to manage it |

### 🛠️ Development and Testing

| Section | Description |
|---------|-------------|
| **[Developer Guide](docs/developer.md)** | Testing, quality assurance, and development workflow |
| **[MCP Inspector](docs/mcp-inspector.md)** | Visual debugging and testing with MCP Inspector |
| **[Troubleshooting](docs/troubleshooting.md)** | Common issues and solutions |
| **[Integration Testing](docs/integration-testing.md)** | Comprehensive testing procedures |
| **[Local Installation (stdio)](docs/installation-local-stdio.md)** | Install and run locally |
| **[Remote Deployment (SSE)](docs/installation-remote-sse.md)** | Deploy to Kubernetes for production use |
| **[Environment Setup](docs/environment-setup.md)** | Advanced environment configuration |

**📋 Quality Assurance**: Pre-commit hooks ensure automatic code formatting, documentation linting, and broken link checking on every commit. Install with `just install-dev`.

---

## 🤝 Contributing

Check the [contributing guide](docs/contributing.md) for:

- Development standards
- Tool creation process
- Code and testing conventions
- Git workflow and semantic versioning

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
