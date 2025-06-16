# SSE Server Endpoints

This document describes the REST API endpoints available when running the HubSpot MCP server in SSE (Server-Sent Events) mode.

## Overview

The SSE server provides HTTP endpoints for health monitoring, data management, and direct API access. These endpoints complement the MCP protocol tools and are particularly useful for:

- Server health monitoring
- Administrative data management
- Direct integration with web applications
- Bulk data operations

## Available Endpoints

### Health and Status Endpoints

#### `GET /health`

Basic health check endpoint to verify server is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "server": "hubspot-mcp-server",
  "version": "0.1.0"
}
```

#### `GET /ready`

Readiness check that verifies HubSpot API connectivity.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "hubspot_configured": true,
  "server": "hubspot-mcp-server",
  "version": "0.1.0"
}
```

### Data Management Endpoints

#### `GET /faiss-data`

Retrieves information about the current FAISS index state and statistics.

**Authentication:** Required by default (can be disabled with `FAISS_DATA_SECURE=false`)

**Response:**
```json
{
  "status": "ready",
  "total_entities": 4500,
  "dimension": 384,
  "index_type": "Flat",
  "model_name": "all-MiniLM-L6-v2",
  "entities_by_type": {
    "contacts": 1500,
    "companies": 800,
    "deals": 2200
  }
}
```

#### `POST /force-reindex`

Performs a complete cache reset and rebuilds all FAISS indexes with the latest HubSpot data.

**Authentication:** Required by default (can be disabled with `DATA_PROTECTION_DISABLED=true`)

**What it does:**

1. **Clears existing data**: Removes all cached entities and embeddings
2. **Loads fresh data**: Retrieves all contacts, companies, and deals with complete property data
3. **Builds indexes**: Creates optimized FAISS indexes for semantic search
4. **Returns progress**: Provides detailed logs and statistics

**Usage:**

```bash
# Start the MCP server in SSE mode
python -m hubspot_mcp --mode sse --port 8080

# Call the force reindex endpoint (with authentication)
curl -X POST http://localhost:8080/force-reindex \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_AUTH_KEY"

# Call without authentication (if DATA_PROTECTION_DISABLED=true)
curl -X POST http://localhost:8080/force-reindex \
  -H "Content-Type: application/json"
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

**Error responses:**

```json
{
  "status": "error",
  "error": "HUBSPOT_API_KEY not configured",
  "message": "Cannot perform reindexing without HubSpot API access",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**When to use:**

- After major HubSpot data changes
- When semantic search returns outdated results  
- To ensure FAISS indexes have the latest property data
- During initial setup for optimal performance
- After server restarts to warm up caches

**Performance notes:**

- Process may take several minutes depending on data volume
- Handles up to 10,000 entities per type (contacts, companies, deals)
- Loads all available properties for comprehensive indexing
- Uses background processing to avoid timeouts

## Authentication

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_AUTH_KEY` | None | API key for endpoint authentication |
| `MCP_AUTH_HEADER` | `X-API-Key` | Header name for authentication |
| `FAISS_DATA_SECURE` | `true` | Require auth for `/faiss-data` endpoint |
| `DATA_PROTECTION_DISABLED` | `false` | Disable auth for data endpoints |

### Security Configuration

**Default (secure):**
- All data endpoints require authentication
- Health endpoints (`/health`, `/ready`) are always public

**Development/Testing:**
```bash
# Disable protection for all data endpoints
export DATA_PROTECTION_DISABLED=true

# Or disable protection for specific endpoints
export FAISS_DATA_SECURE=false
```

## Usage Patterns

### Health Monitoring

```bash
# Basic health check
curl http://localhost:8080/health

# Readiness check with HubSpot connectivity
curl http://localhost:8080/ready
```

### Data Management Workflow

```bash
# 1. Check current index state
curl -H "X-API-Key: YOUR_KEY" http://localhost:8080/faiss-data

# 2. Force complete reindexing
curl -X POST -H "X-API-Key: YOUR_KEY" http://localhost:8080/force-reindex

# 3. Verify new index state
curl -H "X-API-Key: YOUR_KEY" http://localhost:8080/faiss-data
```

### Integration with Scripts

See `examples/clear_and_reindex.py` for a complete Python script that demonstrates:

- Server health checks
- Authentication handling  
- Error management
- Progress monitoring
- Result verification

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | Success | Operation completed successfully |
| `401` | Unauthorized | Missing or invalid API key |
| `500` | Internal Server Error | HubSpot API issues, server errors |

### Error Response Format

```json
{
  "status": "error",
  "error": "Specific error type",
  "message": "Human-readable error description", 
  "timestamp": "2024-01-15T10:30:00.000Z",
  "process_log": ["Error details..."]  // For /force-reindex
}
```

## Integration Examples

### Docker Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Monitoring Scripts

```bash
#!/bin/bash
# Simple monitoring script
HEALTH=$(curl -s http://localhost:8080/health | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
  echo "Server unhealthy!"
  exit 1
fi
``` 