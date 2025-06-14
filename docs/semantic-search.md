# AI-Powered Semantic Search

The HubSpot MCP server includes advanced **semantic search capabilities** powered by FAISS (Facebook AI Similarity Search) and sentence transformers. This enables natural language queries across your HubSpot data.

## ✨ What is Semantic Search?

Instead of exact keyword matching, semantic search understands the **meaning** and **context** of your queries:

- 🔍 **Natural Language**: *"software engineers"* finds contacts with titles like "Developer", "Programmer", "Software Architect"
- 🎯 **Context Aware**: *"enterprise clients"* finds large companies even if they don't contain the word "enterprise"
- 🌐 **Multi-Entity**: Search across contacts, companies, deals, and engagements simultaneously
- 🔄 **Hybrid Mode**: Combines AI similarity with traditional API filters for best results

## 🚀 Getting Started with Semantic Search

### 1. **Build Embedding Index**
First, create AI embeddings for your HubSpot data:

```json
{
  "name": "manage_hubspot_embeddings",
  "arguments": {
    "action": "build",
    "entity_types": ["contacts", "companies", "deals", "engagements"],
    "limit": 1000
  }
}
```

### 2. **Perform Semantic Search**
Search using natural language across all entities:

```json
{
  "name": "semantic_search_hubspot",
  "arguments": {
    "query": "technology companies in San Francisco",
    "limit": 10,
    "search_mode": "hybrid",
    "threshold": 0.5
  }
}
```

## 🎛️ Search Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `semantic` | Pure AI-based similarity search | Finding conceptually related entities |
| `hybrid` | Combines AI + traditional API search | Most accurate and comprehensive results |
| `auto` | Automatically chooses best approach | General use (recommended) |

## 📊 Embedding Management

Monitor and manage your AI indexes:

```json
{
  "name": "manage_hubspot_embeddings",
  "arguments": {"action": "info"}
}
```

**Available Actions:**
- `info` - View embedding system status and statistics
- `build` - Create new embedding indexes  
- `rebuild` - Clear and rebuild all indexes
- `clear` - Remove all embeddings and indexes

## 🎯 Example Queries

**Find Similar Contacts:**
- *"software engineers"* → Developers, Programmers, Architects
- *"decision makers"* → CEOs, CTOs, Directors, VPs
- *"marketing professionals"* → Marketing Managers, Growth Hackers, CMOs

**Discover Companies:**
- *"AI startups"* → Machine Learning, Artificial Intelligence companies
- *"enterprise clients"* → Large corporations, Fortune 500 companies
- *"French companies"* → Organizations based in France

**Search Deals:**
- *"enterprise sales"* → Large B2B deals, corporate contracts
- *"renewal opportunities"* → Contract renewals, subscription extensions
- *"urgent deals"* → Time-sensitive, high-priority opportunities

## ⚙️ Technical Details

- **Model**: all-MiniLM-L6-v2 (384-dimensional embeddings)
- **Index**: FAISS with flat or IVF algorithms
- **Cache**: Persistent embedding cache with TTL
- **Performance**: Sub-second search across thousands of entities
- **Storage**: In-memory with optional persistence

## 🔧 Configuration

The semantic search system automatically:
- Downloads AI models on first use
- Generates embeddings for all entity text content
- Builds optimized FAISS indexes
- Caches results for performance
- Supports incremental updates

## 🔗 Related Tools

- [`semantic_search_hubspot`](api-reference.md#semantic_search_hubspot) - Perform semantic search
- [`manage_hubspot_embeddings`](api-reference.md#manage_hubspot_embeddings) - Manage embeddings
- [`manage_hubspot_cache`](caching.md) - Cache management 