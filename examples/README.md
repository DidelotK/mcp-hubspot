# HubSpot MCP Examples

This directory contains example scripts and configurations for working with the HubSpot MCP server.

## Scripts

### clear_and_reindex.py

A utility script to clear and reindex all HubSpot data through the SSE server HTTP endpoints. This script demonstrates how to interact with the server's RESTful API to manage data indexing.

For complete API documentation, see: **[SSE Endpoints Documentation](../docs/sse-endpoints.md)**

#### Features

- ✅ Health and readiness checks
- 📊 Current FAISS data inspection
- 🔄 Complete data reindexing with cache reset
- 🛡️ Authentication support
- 📋 Detailed progress logging
- 🎯 Error handling and recovery

#### Usage

```bash
# Basic usage (no authentication)
python clear_and_reindex.py

# With custom server URL
python clear_and_reindex.py --server-url http://your-server:8080

# With authentication
python clear_and_reindex.py --auth-key your-secret-key

# Using environment variables
export SSE_SERVER_URL="http://localhost:8080"
export SSE_AUTH_KEY="your-secret-key"
export DATA_PROTECTION_DISABLED="true"  # Disable auth for testing
python clear_and_reindex.py
```

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SSE_SERVER_URL` | Base URL of the SSE server | `http://localhost:8080` |
| `SSE_AUTH_KEY` | Authentication key for protected endpoints | None |
| `DATA_PROTECTION_DISABLED` | When `true`, disables auth for data endpoints | `false` |

#### Requirements

```bash
# Install required dependencies
pip install aiohttp
```

#### Example Output

```text
🔧 HubSpot Data Clear and Reindex Tool
==================================================
Server URL: http://localhost:8080
Auth Key: ✅ Provided
🔓 Data protection is disabled - authentication not required

🚀 Starting HubSpot data clear and reindex process
============================================================

1️⃣ Checking server health...
✅ Server is healthy: {'status': 'healthy', 'timestamp': '2024-01-15T10:30:00Z'}

2️⃣ Checking server readiness...
✅ Server is ready: {'status': 'ready', 'hubspot_configured': True}

3️⃣ Getting current FAISS data...
📊 Current FAISS data: {
  "status": "ready",
  "total_entities": 1500,
  "dimension": 384,
  "index_type": "Flat"
}

4️⃣ Force reindexing all data...
🔄 Starting force reindex process...
✅ Force reindex completed successfully!

📋 Process Log:
  🧹 Clearing all existing data and embeddings...
  ✅ Successfully cleared all data
  📥 Loading contacts with all properties...
  ✅ contacts: Loaded 500 entities with embeddings
  📥 Loading companies with all properties...
  ✅ companies: Loaded 300 entities with embeddings
  📥 Loading deals with all properties...
  ✅ deals: Loaded 700 entities with embeddings
  🔍 Building FAISS indexes for semantic search...
  ✅ Final index stats: 1500 entities indexed
  🎉 Force reindex process completed!
  📈 Summary: 3/3 entity types successful, 1500 total entities loaded
  ✅ Semantic search is now fully available!

📈 Summary:
  • Entity types processed: 3
  • Successful types: 3
  • Total entities loaded: 1500
  • Embeddings ready: True
  • Semantic search available: True

🏢 Entity Results:
  • contacts: 500 entities loaded, embeddings: ✅
  • companies: 300 entities loaded, embeddings: ✅
  • deals: 700 entities loaded, embeddings: ✅

🎉 Clear and reindex process completed successfully!

5️⃣ Verifying final state...
📊 Current FAISS data: {
  "status": "ready",
  "total_entities": 1500,
  "dimension": 384,
  "index_type": "Flat",
  "model_name": "all-MiniLM-L6-v2"
}
```

#### Error Handling

The script provides detailed error messages for common issues:

- **Server unreachable**: Network connectivity problems
- **Authentication required**: Missing or invalid auth key
- **HubSpot API issues**: API key not configured or rate limits
- **Partial failures**: Some entity types fail while others succeed
- **Server errors**: Internal server issues with detailed error logs

#### Authentication Configuration

To disable authentication requirements for testing, set the environment variable:

```bash
export DATA_PROTECTION_DISABLED=true
```

This allows the `/force-reindex` endpoint to be accessed without authentication headers.

## Other Examples

- `basic/`: Basic MCP client examples
- `claude/`: Claude Desktop integration examples
- `fastagent-stdio/`: FastAgent stdio examples
- `fastagent-sse/`: FastAgent SSE examples
- `python-stdio-mcp-client/`: Python MCP client examples
