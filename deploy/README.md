# HubSpot MCP Server - Production Deployment

This directory contains production deployment configurations and scripts for the HubSpot MCP Server using Kubernetes and Helm.

## Quick Start

### 1. Prerequisites Setup

Ensure you have:
- **Kubernetes cluster** (>= 1.20) with proper access
- **Helm 3** installed
- **kubectl** configured
- **External Secrets Operator** installed in your cluster
- **NGINX Ingress Controller** installed
- **Cert-Manager** for TLS certificate management

### 2. Configuration

```bash
# Copy configuration templates
cp environment.example environment
cp values.example.yaml values-production.yaml

# Edit with your specific values
nano environment
nano values-production.yaml
```

#### 📝 Configure `values-production.yaml`

This file contains your **environment-specific configuration** and is **excluded from Git**. You must customize:

1. **Docker image**: Update `repository` and `tag` with your values
2. **Domain**: Replace `mcp-hubspot.your-domain.com` with your actual domain
3. **Secret ID**: Update with your External Secrets secret identifier
4. **Environment labels**: Set your environment name and namespace

See detailed configuration instructions in the [Helm Values section](#helm-values-values-productionyaml) below.

### 3. Build and Push Docker Image

```bash
# Build and push image
./scripts/build-image.sh

# Or use just command from project root
just docker-build
```

### 4. Deploy to Kubernetes

```bash
# Automated deployment
./scripts/deploy-mcp-hubspot.sh

# Or manual deployment
./scripts/deploy.sh deploy
```

### 5. Test Deployment

```bash
# Run comprehensive tests
./scripts/test-deployment.sh
```

## Files Structure

```
deploy/
├── Chart.yaml                     # Helm chart configuration
├── Chart.lock                     # Helm dependencies lock
├── charts/                        # Helm chart dependencies
├── values.example.yaml           # Helm values template
├── values-production.yaml        # Your production values (not in git)
├── environment.example            # Environment variables template
├── environment                    # Your environment config (not in git)
├── kubeconfig.yaml               # Your kubeconfig (not in git)
├── scripts/                      # Deployment scripts
│   ├── deploy-mcp-hubspot.sh    # Main deployment script
│   ├── deploy.sh                 # Helm deployment script
│   ├── build-image.sh            # Docker build script
│   ├── docker-utils.sh           # Docker utility functions
│   └── test-deployment.sh        # Deployment testing script
└── README.md                     # This documentation
```

## Scripts Overview

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

### 🔧 `deploy.sh` - Helm Deployment Script

Lower-level Helm operations:

```bash
# Deploy or upgrade
./scripts/deploy.sh deploy

# Uninstall
./scripts/deploy.sh uninstall

# Show status
./scripts/deploy.sh status
```

### 🐳 `build-image.sh` - Docker Build Script

Builds and pushes Docker image:

```bash
./scripts/build-image.sh
```

**Features:**
- Loads environment configuration
- Builds multi-architecture image
- Pushes to configured registry
- Error handling and validation

### 🧪 `test-deployment.sh` - Testing Script

Comprehensive deployment testing:

```bash
./scripts/test-deployment.sh
```

**Tests include:**
- Kubernetes resources verification
- Health endpoint checks
- Authentication testing
- TLS certificate validation
- Performance testing

### 🛠️ `docker-utils.sh` - Docker Utilities

Utility functions for Docker operations (sourced by other scripts).

## Configuration Files

### Environment Configuration (`environment`)

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

⚠️ **Important**: Copy `values.example.yaml` to `values-production.yaml` and customize with your specific values:

```bash
cp values.example.yaml values-production.yaml
nano values-production.yaml  # or use your preferred editor
```

**Key sections you MUST customize:**

#### 1. Docker Image Configuration
```yaml
app-component:
  containers:
    - name: hubspot-mcp-server
      image:
        repository: your-registry.example.com/your-org/hubspot-mcp-server  # YOUR registry
        tag: "0.1.0"  # YOUR image tag
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
        - mcp-hubspot.your-domain.com  # YOUR domain
```

#### 4. Environment and Namespace
```yaml
  commonLabels:
    environment: your-environment-name  # e.g., production, staging
  
  commonAnnotations:
    meta.helm.sh/release-namespace: your-namespace  # e.g., mcp-hubspot
```

**Note**: The `values-production.yaml` file is excluded from Git for security and contains your environment-specific configuration.

## Architecture Overview

The HubSpot MCP Server is deployed as a containerized application in Kubernetes with:

- **External Secrets Operator** for secure secret management
- **NGINX Ingress** for external access with TLS
- **Horizontal Pod Autoscaler** for automatic scaling
- **Network Policies** for security
- **Service Monitor** for Prometheus monitoring
- **Header-based authentication** for API access

## Secret Management

### External Secrets Configuration

The deployment uses External Secrets Operator with a ClusterSecretStore. Configure your secrets in your secret management system:

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

### Required Secrets

Your secret must contain:
- **`hubspot-api-key`**: Your HubSpot API key
- **`mcp-auth-key`**: Authentication key for MCP server access

## Deployment Workflow

### Automated Deployment

```bash
# 1. Build and push image
./scripts/build-image.sh

# 2. Deploy to Kubernetes
./scripts/deploy-mcp-hubspot.sh

# 3. Test deployment
./scripts/test-deployment.sh
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

## Monitoring and Health Checks

### Health Endpoints

- **`/health`** - Liveness probe (no auth required)
- **`/ready`** - Readiness probe (no auth required)
- **`/metrics`** - Prometheus metrics (auth required)

### Testing Commands

```bash
# Health check
curl -k https://mcp-hubspot.your-domain.com/health

# Ready check
curl -k https://mcp-hubspot.your-domain.com/ready

# Authenticated endpoint
curl -k -H "X-API-Key: your-auth-key" https://mcp-hubspot.your-domain.com/sse
```

## Troubleshooting

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

## Security

### Authentication

The server includes header-based authentication:
- **Header**: `X-API-Key` (configurable)
- **Exempt paths**: `/health`, `/ready`
- **Auth key**: From External Secrets

### Network Security

- **Network Policies**: Restrict ingress/egress traffic
- **TLS**: Automatic certificate management
- **Security Context**: Non-root user, dropped capabilities

## Scaling

### Horizontal Pod Autoscaler

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Manual Scaling

```bash
kubectl scale deployment hubspot-mcp-server -n $NAMESPACE --replicas=5
```

## Maintenance

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

## Support

For issues with:
- **Scripts**: Check script logs and environment configuration
- **Helm Chart**: Check [app-component documentation](https://gitlab.com/keltiotechnology/helm-charts/-/tree/master/app-component)
- **External Secrets**: Check External Secrets Operator logs
- **Application**: Check pod logs and health endpoints 