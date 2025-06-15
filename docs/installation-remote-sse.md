# Remote Deployment Guide (SSE Mode)

## Overview

This guide explains how to deploy the HubSpot MCP Server to Kubernetes for production use with SSE (Server-Sent Events) protocol. This approach is ideal for teams, scalable deployments, and production environments.

## 🎯 When to Use Remote Deployment

**Best for:**
- ✅ Production environments
- ✅ Team usage and collaboration
- ✅ Scalable deployments
- ✅ High availability requirements
- ✅ Multi-user access
- ✅ Centralized management

**Features:**
- 🌐 SSE (Server-Sent Events) protocol
- 🔐 Authentication and security
- 📈 Horizontal scaling
- 🔄 Automatic deployments
- 🧪 Comprehensive testing
- 📊 Monitoring and health checks

---

## 📋 Prerequisites

### Kubernetes Cluster Requirements

Ensure your Kubernetes cluster has:

- **Kubernetes** (>= 1.20) with proper access
- **Helm 3** installed and configured
- **kubectl** configured with cluster access
- **External Secrets Operator** for secret management
- **NGINX Ingress Controller** for traffic routing
- **Cert-Manager** for TLS certificate management
- **External DNS** for automatic DNS record management

### Local Development Tools

- **Git** for repository access
- **Docker** with registry access
- **curl** and **jq** for testing
- **uv** for local development (optional)

---

## 🚀 Quick Start Deployment

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd mcp-hubspot

# Navigate to deployment directory
cd deploy/
```

### 2. Configure Environment

```bash
# Copy configuration templates
cp environment.example environment
cp values.example.yaml values-production.yaml

# Edit with your specific values
nano environment
nano values-production.yaml
```

### 3. Deploy to Kubernetes

```bash
# Automated deployment
./scripts/deploy-mcp-hubspot.sh

# Or manual step-by-step
./scripts/build-image.sh        # Build and push Docker image
./scripts/deploy.sh deploy      # Deploy with Helm
```

### 4. Test Deployment

```bash
# Test SSE functionality
./scripts/test-sse-mcp.sh

# Test general deployment
./scripts/test-deployment.sh
```

---

## 📁 Configuration Files

### Environment Configuration (`environment`)

The environment file contains deployment-specific settings:

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
```

### Helm Values (`values-production.yaml`)

⚠️ **Important**: Copy `values.example.yaml` to `values-production.yaml` and customize:

```bash
cp values.example.yaml values-production.yaml
nano values-production.yaml  # Customize with your values
```

**Key sections to customize:**

#### 1. Docker Image Configuration
```yaml
app-component:
  containers:
    - name: hubspot-mcp-server
      image:
        repository: your-registry.example.com/your-org/hubspot-mcp-server
        tag: "0.1.0"  # Your image tag
```

#### 2. Secret Management
```yaml
  secrets:
    - name: hubspot-mcp-secrets
      spec:
        dataFrom:
          - extract:
              # For Scaleway Secret Manager:
              key: id:your-secret-id
              # For other providers:
              # key: production/hubspot-mcp-secrets
```

#### 3. Domain and Ingress
```yaml
  ingress:
    hosts:
      - host: mcp-hubspot.your-domain.com  # YOUR domain
    tls:
      - hosts:
        - mcp-hubspot.your-domain.com
    annotations:
      # External DNS will automatically create DNS records
      external-dns.alpha.kubernetes.io/hostname: mcp-hubspot.your-domain.com
```

#### 4. Environment and Namespace
```yaml
  commonLabels:
    environment: production  # Your environment name
  
  commonAnnotations:
    meta.helm.sh/release-namespace: mcp-hubspot  # Your namespace
```

---

## 🔐 Secret Management

The deployment uses **External Secrets Operator** for secure secret management:

### Required Secrets

Your secret store must contain:
- **`hubspot-api-key`**: Your HubSpot API key for CRM access
- **`mcp-auth-key`**: Authentication key for MCP server access

### External Secrets Configuration

**For Scaleway Secret Manager:**
```yaml
secrets:
  - name: hubspot-mcp-secrets
    spec:
      dataFrom:
        - extract:
            key: id:your-secret-id
```

**For other providers:**
```yaml
secrets:
  - name: hubspot-mcp-secrets
    spec:
      dataFrom:
        - extract:
            key: production/hubspot-mcp-secrets
```

### DNS Management

**External DNS Integration** provides automatic DNS record management:

- ✅ Automatic DNS records based on Ingress annotations
- ✅ Domain synchronization when Ingress changes
- ✅ Support for major DNS providers (Cloudflare, Route53, etc.)

When you deploy, External DNS will:
1. Detect the new Ingress resource
2. Extract hostname from annotations
3. Create appropriate DNS record pointing to load balancer
4. Monitor and update records as needed

---

## 🛠️ Deployment Scripts

### 🚀 `deploy-mcp-hubspot.sh` - Main Deployment Script

Automated deployment with namespace creation and verification:

```bash
./scripts/deploy-mcp-hubspot.sh
```

**Features:**
- Creates namespace with proper labels
- Deploys application using Helm
- Verifies deployment status
- Comprehensive error handling
- Color-coded output

### 🔧 `deploy.sh` - Helm Operations

Lower-level Helm operations:

```bash
# Deploy or upgrade
./scripts/deploy.sh deploy

# Uninstall
./scripts/deploy.sh uninstall

# Show status
./scripts/deploy.sh status
```

### 🐳 `build-image.sh` - Docker Build

Builds and pushes Docker image:

```bash
./scripts/build-image.sh
```

**Features:**
- Loads environment configuration
- Builds multi-architecture image
- Pushes to configured registry
- Error handling and validation

---

## 🧪 Testing and Monitoring

### SSE MCP Server Testing

Use the dedicated SSE test script for comprehensive functionality testing:

```bash
# Test with environment configuration
./scripts/test-sse-mcp.sh

# Test specific domain and auth key
./scripts/test-sse-mcp.sh -d mcp.example.com -k your-auth-key

# Test with custom parameters
./scripts/test-sse-mcp.sh -d mcp.example.com -k your-auth-key -l 10 -t 60
```

**Test Categories:**

1. **Basic Connectivity**
   - Health endpoint (`/health`)
   - Readiness endpoint (`/ready`)

2. **SSE Functionality**
   - SSE endpoint accessibility
   - Authentication security
   - SSE streaming capability

3. **MCP Protocol**
   - Tools listing (`tools/list`)
   - Tool execution (`tools/call`)
   - HubSpot API integration

4. **Performance**
   - Response times
   - Request throughput
   - Error rates

### Health Endpoints

- **`/health`** - Liveness probe (no auth required)
- **`/ready`** - Readiness probe (no auth required)
- **`/metrics`** - Prometheus metrics (auth required)
- **`/sse`** - SSE MCP endpoint (auth required)

### Manual Testing Commands

```bash
# Health check
curl -k https://mcp-hubspot.your-domain.com/health

# Ready check
curl -k https://mcp-hubspot.your-domain.com/ready

# SSE endpoint (should require auth)
curl -k https://mcp-hubspot.your-domain.com/sse

# MCP tools list (authenticated)
curl -k -H "X-API-Key: your-auth-key" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  https://mcp-hubspot.your-domain.com/

# MCP tool execution (authenticated)
curl -k -H "X-API-Key: your-auth-key" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_hubspot_contacts","arguments":{"limit":5}}}' \
  https://mcp-hubspot.your-domain.com/
```

---

## 🏗️ Architecture Overview

The HubSpot MCP Server deployment includes:

- **External Secrets Operator** for secure secret management
- **NGINX Ingress** for external access with TLS
- **Cert-Manager** for automatic TLS certificate provisioning
- **External DNS** for automatic DNS record management
- **Horizontal Pod Autoscaler** for automatic scaling
- **Network Policies** for security
- **Service Monitor** for Prometheus monitoring
- **Header-based authentication** for API access

### Scaling Configuration

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Security Features

- **Authentication**: X-API-Key header authentication
- **TLS**: Automatic certificate management
- **Network Policies**: Restrict ingress/egress traffic
- **Security Context**: Non-root user, dropped capabilities

---

## 🔄 Deployment Workflow

### Automated Deployment

```bash
# 1. Build and push image
./scripts/build-image.sh

# 2. Deploy to Kubernetes
./scripts/deploy-mcp-hubspot.sh

# 3. Test deployment
./scripts/test-sse-mcp.sh
```

### Manual Step-by-Step

```bash
# 1. Load environment
source environment

# 2. Create namespace
kubectl create namespace $NAMESPACE
kubectl label namespace $NAMESPACE external-secrets=true

# 3. Deploy with Helm
helm install $RELEASE_NAME $CHART_REPO/$CHART_NAME \
  -f values-production.yaml \
  -n $NAMESPACE \
  --wait

# 4. Verify deployment
kubectl get pods -n $NAMESPACE
kubectl get ingress -n $NAMESPACE
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Script Permissions
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

#### 2. Environment Variables
```bash
# Check environment is loaded
source environment
echo $NAMESPACE $RELEASE_NAME $DOMAIN
```

#### 3. Kubernetes Access
```bash
# Test cluster access
kubectl cluster-info
kubectl get nodes
```

#### 4. External Secrets Issues
```bash
# Check external secret status
kubectl describe externalsecret hubspot-mcp-secrets -n $NAMESPACE

# Check secret creation
kubectl get secrets -n $NAMESPACE
```

#### 5. Ingress/TLS Issues
```bash
# Check ingress status
kubectl describe ingress -n $NAMESPACE

# Check certificate status
kubectl get certificates -n $NAMESPACE
```

### Debug Commands

```bash
# Pod logs
kubectl logs -f deployment/hubspot-mcp-server -n $NAMESPACE

# Pod events
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'

# Resource status
kubectl get all -n $NAMESPACE
```

---

## 🔧 Maintenance

### Upgrade Application

```bash
# Update image tag in values-production.yaml
# Then run upgrade
./scripts/deploy.sh deploy
```

### Rollback

```bash
# Check history
helm history $RELEASE_NAME -n $NAMESPACE

# Rollback
helm rollback $RELEASE_NAME 1 -n $NAMESPACE
```

### Cleanup

```bash
# Uninstall application
./scripts/deploy.sh uninstall

# Remove namespace
kubectl delete namespace $NAMESPACE
```

---

## 🔗 Client Integration

### With MCP Clients

Configure MCP clients to use the SSE endpoint:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "curl",
      "args": [
        "-H", "X-API-Key: your-auth-key",
        "-H", "Accept: text/event-stream",
        "https://mcp-hubspot.your-domain.com/sse"
      ]
    }
  }
}
```

### API Integration

Use the HTTP/JSON-RPC API directly:

```bash
# List tools
curl -H "X-API-Key: your-auth-key" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
     https://mcp-hubspot.your-domain.com/

# Execute tool
curl -H "X-API-Key: your-auth-key" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_hubspot_contacts","arguments":{"limit":5}}}' \
     https://mcp-hubspot.your-domain.com/
```

---

## 📈 Performance and Scaling

### Horizontal Scaling

The deployment supports automatic scaling based on resource usage:

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### Manual Scaling

```bash
kubectl scale deployment hubspot-mcp-server -n $NAMESPACE --replicas=5
```

### Performance Monitoring

Monitor performance through:
- **Prometheus metrics** at `/metrics` endpoint
- **Health checks** at `/health` and `/ready`
- **Kubernetes resources** monitoring
- **Application logs** via kubectl

---

## 🔒 Security Best Practices

### Authentication

- ✅ Use strong authentication keys
- ✅ Rotate keys regularly
- ✅ Limit access to necessary endpoints
- ✅ Monitor authentication failures

### Network Security

- ✅ Use TLS for all communications
- ✅ Implement network policies
- ✅ Restrict ingress/egress traffic
- ✅ Use secure service mesh if available

### Secret Management

- ✅ Use External Secrets Operator
- ✅ Never store secrets in code
- ✅ Implement secret rotation
- ✅ Monitor secret access

---

## 📚 Related Documentation

- **[Local Installation Guide](installation-local-stdio.md)** - For local development
- **[Configuration Guide](configuration.md)** - Environment setup
- **[Tools](tools.md)** - Complete tool documentation
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Developer Guide](developer.md)** - Development workflow

---

## 🎯 Next Steps

After successful deployment:

1. **Test functionality**: Use `./scripts/test-sse-mcp.sh`
2. **Configure clients**: Set up MCP client integration
3. **Monitor deployment**: Set up monitoring and alerting
4. **Scale as needed**: Adjust replicas based on usage
5. **Maintain regularly**: Keep dependencies and secrets updated

**Happy deploying!** 🚀 