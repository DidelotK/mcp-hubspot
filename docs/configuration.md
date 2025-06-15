# Configuration Guide

This guide covers configuration options for both local (stdio) and remote (SSE) deployment modes of the HubSpot MCP Server.

## 🔧 General Configuration

### Environment Variables

Both deployment modes use these core environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `HUBSPOT_API_KEY` | HubSpot private app API key | ✅ Yes | - |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | ❌ No | `INFO` |
| `MODE` | Server mode (stdio or sse) | ❌ No | `stdio` |
| `HOST` | Host for SSE mode | ❌ No | `0.0.0.0` |
| `PORT` | Port for SSE mode | ❌ No | `8080` |
| `MCP_AUTH_KEY` | Authentication key for SSE mode | ❌ No | - |
| `MCP_AUTH_HEADER` | Authentication header name | ❌ No | `X-API-Key` |

### HubSpot API Configuration

#### Getting Your API Key

1. **Create a Private App** in your HubSpot account:
   - Go to Settings → Integrations → Private Apps
   - Click "Create a private app"
   - Configure scopes and permissions

2. **Required Scopes**:
   ```
   CRM Scopes:
   - crm.objects.contacts.read
   - crm.objects.companies.read
   - crm.objects.deals.read
   - crm.objects.deals.write
   - crm.schemas.contacts.read
   - crm.schemas.companies.read
   - crm.schemas.deals.read
   - crm.objects.engagements.read
   ```

3. **Generate and Copy** the access token

#### API Key Format

HubSpot API keys follow this format:
```
pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 🏠 Local Configuration (stdio mode)

### Basic Setup

```bash
# Set environment variables
export HUBSPOT_API_KEY="pat-na1-your-api-key-here"
export LOG_LEVEL="INFO"

# Optional: Create .env file
echo "HUBSPOT_API_KEY=pat-na1-your-api-key-here" > .env
echo "LOG_LEVEL=INFO" >> .env
```

### Development Configuration

For development, you can set additional options:

```bash
# Enable debug logging
export LOG_LEVEL="DEBUG"

# Enable semantic search features
export EMBEDDINGS_ENABLED="true"

# Configure cache TTL (seconds)
export CACHE_TTL="300"
```

---

## 🌐 Remote Configuration (SSE mode)

### Environment File

The remote deployment uses an `environment` file in the `deploy/` directory:

```bash
# Kubernetes Configuration
export NAMESPACE="mcp-hubspot"
export RELEASE_NAME="hubspot-mcp-server"
export KUBECONFIG="$(dirname "${BASH_SOURCE[0]}")/kubeconfig.yaml"

# Docker Configuration
export IMAGE_NAME="hubspot-mcp-server"
export IMAGE_REGISTRY="your-registry.example.com/your-org"
export IMAGE_TAG="0.1.0"

# Application Configuration
export DOMAIN="mcp-hubspot.your-domain.com"
export CHART_NAME="app-component"
export CHART_REPO="oci://your-registry.example.com/helm-charts"

# Authentication
export MCP_AUTH_KEY="your-secure-auth-key-here"
```

### Helm Values Configuration

The `values-production.yaml` file configures the Kubernetes deployment:

```yaml
app-component:
  fullnameOverride: hubspot-mcp-server

  containers:
    - name: hubspot-mcp-server
      image:
        repository: your-registry.example.com/your-org/hubspot-mcp-server
        pullPolicy: IfNotPresent
        tag: "0.1.0"
      
      # Environment variables for the container
      env:
        - name: MODE
          value: "sse"
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8080"
        - name: HUBSPOT_API_KEY
          valueFrom:
            secretKeyRef:
              name: hubspot-mcp-secrets
              key: hubspot-api-key
        - name: MCP_AUTH_KEY
          valueFrom:
            secretKeyRef:
              name: hubspot-mcp-secrets
              key: mcp-auth-key
        - name: MCP_AUTH_HEADER
          value: "X-API-Key"
```

### Secret Management

Secrets are managed through External Secrets Operator:

#### For Scaleway Secret Manager

```yaml
secrets:
  - name: hubspot-mcp-secrets
    spec:
      secretStoreRef:
        name: secret-store
        kind: ClusterSecretStore
      target:
        name: hubspot-mcp-secrets
        creationPolicy: Owner
      dataFrom:
        - extract:
            key: id:your-secret-id
```

#### For AWS Secrets Manager

```yaml
secrets:
  - name: hubspot-mcp-secrets
    spec:
      secretStoreRef:
        name: aws-secret-store
        kind: ClusterSecretStore
      target:
        name: hubspot-mcp-secrets
        creationPolicy: Owner
      dataFrom:
        - extract:
            key: production/hubspot-mcp-secrets
```

#### For HashiCorp Vault

```yaml
secrets:
  - name: hubspot-mcp-secrets
    spec:
      secretStoreRef:
        name: vault-secret-store
        kind: ClusterSecretStore
      target:
        name: hubspot-mcp-secrets
        creationPolicy: Owner
      data:
        - secretKey: hubspot-api-key
          remoteRef:
            key: secret/hubspot
            property: api-key
        - secretKey: mcp-auth-key
          remoteRef:
            key: secret/hubspot
            property: mcp-auth-key
```

---

## 🔐 Authentication Configuration

### For Local Mode (stdio)

Local mode typically doesn't require authentication as it runs locally and communicates via stdio.

### For Remote Mode (SSE)

Remote mode uses header-based authentication for security:

#### Authentication Header

- **Default Header**: `X-API-Key`
- **Configurable via**: `MCP_AUTH_HEADER` environment variable

#### Authentication Key

- **Required**: Yes, for all non-health endpoints
- **Set via**: `MCP_AUTH_KEY` environment variable
- **Source**: External Secrets in production

#### Exempt Endpoints

These endpoints don't require authentication:
- `/health` - Health check
- `/ready` - Readiness check

#### Example Usage

```bash
# Authenticated request
curl -H "X-API-Key: your-auth-key" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
     https://mcp-hubspot.your-domain.com/
```

---

## 🎛️ Advanced Configuration

### Caching Configuration

Configure the TTL cache system:

```bash
# Cache TTL in seconds (default: 300 = 5 minutes)
export CACHE_TTL="300"

# Disable caching (not recommended)
export CACHE_ENABLED="false"
```

### Semantic Search Configuration

Enable and configure semantic search features:

```bash
# Enable embeddings and semantic search
export EMBEDDINGS_ENABLED="true"

# Embedding model configuration
export EMBEDDING_MODEL="all-MiniLM-L6-v2"

# FAISS index type (flat, ivf)
export FAISS_INDEX_TYPE="flat"
```

### Logging Configuration

Configure logging levels and output:

```bash
# Logging level
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR

# Log format (for development)
export LOG_FORMAT="detailed"  # simple, detailed

# Enable request logging (SSE mode)
export LOG_REQUESTS="true"
```

### Performance Configuration

Tune performance settings:

```bash
# Request timeout (seconds)
export REQUEST_TIMEOUT="30"

# Maximum concurrent requests
export MAX_CONCURRENT_REQUESTS="100"

# Enable request rate limiting
export RATE_LIMIT_ENABLED="true"
export RATE_LIMIT_REQUESTS="100"
export RATE_LIMIT_WINDOW="60"
```

---

## 🔍 Configuration Validation

### Local Configuration Check

```bash
# Test basic configuration
uv run python -c "
import os
from hubspot_mcp.config import HubSpotConfig
config = HubSpotConfig()
print(f'✅ API Key configured: {bool(config.api_key)}')
print(f'✅ Config valid: {config.api_key is not None}')
"

# Test server startup
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | \
  uv run python -m hubspot_mcp --mode stdio
```

### Remote Configuration Check

```bash
# Check environment configuration
source deploy/environment
echo "✅ Namespace: $NAMESPACE"
echo "✅ Domain: $DOMAIN"
echo "✅ Image: $IMAGE_REGISTRY/$IMAGE_NAME:$IMAGE_TAG"

# Test deployment configuration
helm template hubspot-mcp-server . \
  -f values-production.yaml \
  --dry-run --debug
```

---

## 🚨 Configuration Troubleshooting

### Common Issues

#### 1. Invalid API Key

**Symptoms:**
- 401 Unauthorized errors
- "Invalid API key" messages

**Solutions:**
```bash
# Verify API key format
echo $HUBSPOT_API_KEY | grep -E "^pat-[a-z0-9]+-[a-f0-9-]+$"

# Test API key
curl -H "Authorization: Bearer $HUBSPOT_API_KEY" \
     "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
```

#### 2. Missing Environment Variables

**Symptoms:**
- Server fails to start
- Configuration errors

**Solutions:**
```bash
# Check required variables
env | grep -E "(HUBSPOT_API_KEY|MCP_AUTH_KEY|DOMAIN)"

# Load environment file
source deploy/environment
```

#### 3. Authentication Issues (SSE Mode)

**Symptoms:**
- 401 errors on API calls
- Authentication failures

**Solutions:**
```bash
# Test authentication
curl -I -H "X-API-Key: $MCP_AUTH_KEY" \
     https://$DOMAIN/ready

# Check secret synchronization
kubectl get secrets -n $NAMESPACE
kubectl describe externalsecret hubspot-mcp-secrets -n $NAMESPACE
```

---

## 📋 Configuration Checklist

### Local Deployment

- [ ] HubSpot API key obtained and configured
- [ ] Environment variables set
- [ ] Claude Desktop configuration updated
- [ ] Server starts without errors
- [ ] Tools list successfully

### Remote Deployment

- [ ] Kubernetes cluster access configured
- [ ] External Secrets Operator installed and configured
- [ ] Secret store contains required secrets
- [ ] Domain configured and DNS accessible
- [ ] `environment` file customized
- [ ] `values-production.yaml` customized
- [ ] Deployment successful
- [ ] Health endpoints accessible
- [ ] Authentication working
- [ ] MCP tools functional

---

## 🔗 Related Documentation

- **[Local Installation Guide](installation-local-stdio.md)** - Complete local setup
- **[Remote Deployment Guide](installation-remote-sse.md)** - Kubernetes deployment
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions 