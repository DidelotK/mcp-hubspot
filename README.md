# HubSpot MCP Server

MCP (Model Context Protocol) server for integrating HubSpot with MCP clients (like Claude Desktop). Provides access to HubSpot contacts, companies, and deals through conversational tools.

## 🛠️ Available Tools

The server provides **18 tools** for comprehensive HubSpot integration:

| Category | Tools | Description |
|----------|--------|-------------|
| **📋 Entity Listing** | `list_hubspot_contacts`<br/>`list_hubspot_companies`<br/>`list_hubspot_deals`<br/>`list_hubspot_engagements` | List and browse HubSpot entities with pagination support |
| **🔧 Properties** | `get_hubspot_contact_properties`<br/>`get_hubspot_company_properties`<br/>`get_hubspot_deal_properties` | Retrieve field properties and schemas for each entity type |
| **🔍 Search & Filtering** | `search_hubspot_contacts`<br/>`search_hubspot_companies`<br/>`search_hubspot_deals` | Advanced search with filters for each entity type |
| **💼 Deal Management** | `get_deal_by_name`<br/>`create_deal`<br/>`update_deal` | Complete deal lifecycle management |
| **🤖 AI-Powered Search** | `semantic_search_hubspot`<br/>`manage_hubspot_embeddings`<br/>`browse_hubspot_indexed_data` | Semantic search using natural language with FAISS vector database |
| **⚡ Cache & Performance** | `load_hubspot_entities_to_cache`<br/>`manage_hubspot_cache` | Bulk loading, caching, and performance optimization |

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

## Force Reindexing Endpoint

A new SSE endpoint is available for forcing complete reindexing of all HubSpot entities:

### `POST /force-reindex`

This endpoint performs a complete cache reset and rebuilds all FAISS indexes with the latest HubSpot data.

**What it does:**

1. Clears all existing cache and embeddings
2. Loads all contacts, companies, and deals with their complete property data
3. Builds FAISS indexes for semantic search
4. Returns detailed progress and results

**Usage:**

```bash
# Start the MCP server in SSE mode
python -m hubspot_mcp --mode sse --port 8080

# Call the force reindex endpoint
curl -X POST http://localhost:8080/force-reindex \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_KEY"  # If auth is enabled
```

**Response format:**

```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "server_info": {
    "server": "hubspot-mcp-server",
    "version": "0.1.0",
    "mode": "sse"
  },
  "process_log": [
    "🗑️ Clearing existing cache and embeddings...",
    "✅ Cache and embeddings cleared successfully",
    "📥 Loading contacts with all properties...",
    "✅ contacts: Loaded 1500 entities with embeddings",
    "📥 Loading companies with all properties...",
    "✅ companies: Loaded 800 entities with embeddings",
    "📥 Loading deals with all properties...",
    "✅ deals: Loaded 2200 entities with embeddings",
    "📊 Gathering final statistics...",
    "✅ Final index stats: 4500 entities indexed",
    "🎉 Force reindex process completed!",
    "📈 Summary: 3/3 entity types successful, 4500 total entities loaded",
    "✅ Semantic search is now fully available!"
  ],
  "entity_results": {
    "contacts": {
      "status": "success",
      "entities_loaded": 1500,
      "embeddings_built": true
    },
    "companies": {
      "status": "success",
      "entities_loaded": 800,
      "embeddings_built": true
    },
    "deals": {
      "status": "success",
      "entities_loaded": 2200,
      "embeddings_built": true
    }
  },
  "final_stats": {
    "status": "ready",
    "total_entities": 4500,
    "dimension": 384,
    "index_type": "Flat",
    "model_name": "all-MiniLM-L6-v2"
  },
  "summary": {
    "total_entity_types_processed": 3,
    "successful_entity_types": 3,
    "failed_entity_types": 0,
    "total_entities_loaded": 4500,
    "embeddings_ready": true,
    "semantic_search_available": true
  }
}
```

**When to use:**

- After major HubSpot data changes
- When semantic search returns outdated results
- To ensure FAISS indexes have the latest property data
- During initial setup for optimal performance

**Note:** This process may take several minutes depending on the amount of HubSpot data. The endpoint processes up to 10,000 entities per type (contacts, companies, deals) with all their properties.
