# HubSpot MCP Server - Production Deployment

This directory contains production deployment configurations for the HubSpot MCP Server using Kubernetes and Helm.

## Architecture Overview

The HubSpot MCP Server is deployed as a containerized application in Kubernetes with:
- **External Secrets Operator** for secure secret management
- **NGINX Ingress** for external access with TLS
- **Horizontal Pod Autoscaler** for automatic scaling
- **Network Policies** for security
- **Service Monitor** for Prometheus monitoring
- **Header-based authentication** for API access

## Files Structure

```
deploy/
├── values-production.yaml    # Helm values for production environment
├── environment.example       # Environment variables template
├── README.md                # This documentation
└── scripts/                 # Deployment scripts (if any)
```

## Prerequisites

Before deploying, ensure you have:

1. **Kubernetes cluster** (>= 1.20)
2. **Helm 3** installed and configured
3. **External Secrets Operator** installed in the cluster
4. **NGINX Ingress Controller** installed
5. **Cert-Manager** for TLS certificate management
6. **Prometheus Operator** (optional, for monitoring)
7. **ClusterSecretStore** configured for External Secrets
8. **Docker** with access to Scaleway Container Registry
9. **direnv** for automatic environment variable management (recommended)

## Docker Registry Authentication

The project uses Scaleway Container Registry. To authenticate:

```bash
# Set your Scaleway registry password
export REGISTRY_PASSWORD="your-scaleway-registry-password"

# Authenticate with the registry
docker login rg.fr-par.scw.cloud/keltio-public -u nologin --password-stdin <<< "$REGISTRY_PASSWORD"

# Alternative: using echo
echo "$REGISTRY_PASSWORD" | docker login rg.fr-par.scw.cloud/keltio-public -u nologin --password-stdin
```

### Build and Push Image

```bash
# Build and tag the image
docker build -t rg.fr-par.scw.cloud/keltio-public/hubspot-mcp-server:1.0.0 .

# Push to registry
docker push rg.fr-par.scw.cloud/keltio-public/hubspot-mcp-server:1.0.0
```

## Environment Variables Management with direnv

### Overview

The project uses `direnv` for automatic environment variable management. This provides a seamless development experience where environment variables are automatically loaded when entering the project directory and unloaded when leaving.

### Setup direnv

#### 1. Install direnv

```bash
# Ubuntu/Debian
sudo apt install direnv

# macOS with Homebrew
brew install direnv

# Other systems: https://direnv.net/docs/installation.html
```

#### 2. Configure your shell

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# For bash
eval "$(direnv hook bash)"

# For zsh  
eval "$(direnv hook zsh)"

# For fish
direnv hook fish | source
```

Restart your shell or run `source ~/.bashrc` (or your shell config file).

### Project Setup

#### 1. Create environment file

```bash
# Copy the template
cp deploy/environment.example deploy/environment

# Edit with your actual values
nano deploy/environment  # or your preferred editor
```

#### 2. Configure your environment

Edit `deploy/environment` with your values:

```bash
# Docker Image Configuration
IMAGE_REGISTRY=rg.fr-par.scw.cloud/keltio-public
IMAGE_NAME=hubspot-mcp-server
IMAGE_TAG=0.1.0

# Registry Authentication (Scaleway Container Registry)
REGISTRY_URL=rg.fr-par.scw.cloud/keltio-public
REGISTRY_USERNAME=nologin
REGISTRY_PASSWORD=your-actual-scaleway-password

# HubSpot Configuration
HUBSPOT_API_KEY=pat-eu1-your-actual-key

# MCP Authentication Configuration
MCP_AUTH_KEY=your-secure-auth-key
MCP_AUTH_HEADER=X-API-Key

# Kubernetes Configuration
NAMESPACE=production
DOMAIN=mcp-hubspot.keltio.fr
```

#### 3. Allow direnv

```bash
# Allow direnv to load the configuration
direnv allow

# You should see output like:
# 🔧 Loading environment variables from deploy/environment...
# ✅ Environment variables loaded successfully!
# 📋 Current configuration:
#    - IMAGE_TAG: 0.1.0
#    - IMAGE_REGISTRY: rg.fr-par.scw.cloud/keltio-public
#    - NAMESPACE: production
#    - DOMAIN: mcp-hubspot.keltio.fr
```

### Development Workflow

#### Automatic Variable Loading

```bash
# Enter project directory → variables automatically load
cd /path/to/mcp-hubspot
# 🔧 Loading environment variables from deploy/environment...
# ✅ Environment variables loaded successfully!

# Variables are now available
echo $IMAGE_TAG                    # → 0.1.0
echo $REGISTRY_PASSWORD           # → your-password
echo $HUBSPOT_API_KEY             # → your-api-key

# Use variables directly in commands
docker build -t $IMAGE_REGISTRY/$IMAGE_NAME:$IMAGE_TAG .
./deploy/scripts/build-image.sh   # Uses loaded variables automatically

# Leave directory → variables automatically unload
cd /other/directory
echo $IMAGE_TAG                   # → (empty)
```

#### Manual Commands

```bash
# Reload environment after changes
direnv reload

# Check direnv status
direnv status

# Temporarily disable
direnv deny

# Re-enable
direnv allow
```

### Security Notes

#### File Permissions
```bash
# Secure your environment file
chmod 600 deploy/environment

# Verify git ignores it
git status --ignored | grep deploy/environment
```

#### What's Versioned
- ✅ **`.envrc`** - Direnv configuration (no secrets)
- ✅ **`deploy/environment.example`** - Template file
- ❌ **`deploy/environment`** - Your actual config (contains secrets)

#### Best Practices
- Never commit `deploy/environment` to git
- Use strong, unique passwords and API keys
- Regularly rotate secrets, especially API keys
- Keep `deploy/environment.example` updated with new variables

### Troubleshooting

#### Variables not loading
```bash
# Check if direnv is working
direnv status

# Check if file exists
ls -la deploy/environment

# Force reload
direnv reload
```

#### Permission issues
```bash
# Fix file permissions
chmod 600 deploy/environment
direnv allow
```

#### Getting help
```bash
# If environment file is missing, you'll see:
cd mcp-hubspot
# ⚠️  Environment file not found!
# 
# 📝 To set up your environment:
#    1. Copy the example file:
#       cp deploy/environment.example deploy/environment
#    2. Edit deploy/environment with your values
#    3. Run 'direnv allow' to reload this configuration
```

## Secret Management

### External Secrets Operator Setup

The deployment uses External Secrets Operator with a ClusterSecretStore. Configure your secrets in your secret management system:

```yaml
# Example secret structure in your secret store
production/hubspot-mcp-secrets:
  hubspot-api-key: "your-hubspot-api-key"
  mcp-auth-key: "your-secure-mcp-auth-key"
```

### Required Secrets

- **`hubspot-api-key`**: Your HubSpot API key for accessing HubSpot APIs
- **`mcp-auth-key`**: Authentication key for securing MCP server access

## Helm Configuration

The deployment uses the [Keltio Technology app-component Helm chart](https://gitlab.com/keltiotechnology/helm-charts/-/tree/master/app-component).

### Key Configuration Sections

#### Container Configuration
```yaml
containers:
  - name: hubspot-mcp-server
    image:
      repository: rg.fr-par.scw.cloud/keltio-public/hubspot-mcp-server
      tag: "1.0.0"
      pullPolicy: IfNotPresent
    ports:
      - containerPort: 8080
        name: http
        protocol: TCP
    resources:
      requests:
        cpu: "200m"
        memory: "256Mi"
      limits:
        cpu: "500m"
        memory: "512Mi"
```

#### External Secrets Configuration
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
            key: production/hubspot-mcp-secrets
```

#### Environment Variables
```yaml
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
```

#### Ingress Configuration
```yaml
ingress:
  enabled: true
  ingressClassName: nginx
  annotations:
    cert-manager.io/cluster-issuer: cert-manager
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: mcp-hubspot.keltio.fr
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: hubspot-mcp-server-prod-tls
      hosts:
        - mcp-hubspot.keltio.fr
```

## Deployment Instructions

### 1. Prepare Environment

Copy and customize the environment configuration:
```bash
cp environment.example environment.prod
# Edit environment.prod with your specific values
```

### 2. Add Helm Repository

Add the Keltio Technology Helm repository:
```bash
helm repo add keltio https://gitlab.com/keltiotechnology/helm-charts
helm repo update
```

### 3. Deploy to Production

Deploy using Helm with the app-component chart:
```bash
# Create namespace
kubectl create namespace production

# Deploy with Helm
helm install hubspot-mcp-server keltio/app-component \
  -f values-production.yaml \
  -n production \
  --wait \
  --timeout=10m
```

### 4. Verify Deployment

Check the deployment status:
```bash
# Check pods
kubectl get pods -n production -l app.kubernetes.io/name=hubspot-mcp-server

# Check services
kubectl get svc -n production

# Check ingress
kubectl get ingress -n production

# Check external secrets
kubectl get externalsecrets -n production
```

### 5. Test the Service

Test the deployed service:
```bash
# Test health endpoint
curl -k https://mcp-hubspot.keltio.fr/health

# Test ready endpoint
curl -k https://mcp-hubspot.keltio.fr/ready

# Test authenticated endpoint (replace YOUR_AUTH_KEY)
curl -k -H "X-API-Key: YOUR_AUTH_KEY" https://mcp-hubspot.keltio.fr/sse
```

## Authentication

The server includes header-based authentication for security:

### Configuration
- **Authentication Header**: `X-API-Key` (configurable via `MCP_AUTH_HEADER`)
- **Auth Key**: Set via `MCP_AUTH_KEY` environment variable from External Secrets
- **Exempt Paths**: `/health` and `/ready` (no authentication required)

### Client Usage
All API clients must include the authentication header:
```bash
curl -H "X-API-Key: your-mcp-auth-key" https://mcp-hubspot.keltio.fr/sse
```

### Health Endpoints
Health check endpoints are accessible without authentication:
- `GET /health` - Liveness probe endpoint
- `GET /ready` - Readiness probe endpoint (includes auth status)

## Monitoring

### Prometheus Integration
If Prometheus Operator is installed, the service monitor will be automatically created:
```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    labels:
      app: hubspot-mcp-server
    interval: 30s
    path: /metrics
```

### Key Metrics
The server exposes metrics at `/metrics` endpoint including:
- HTTP request metrics
- Application-specific metrics
- Authentication success/failure rates

## Scaling

### Horizontal Pod Autoscaler
Automatic scaling based on CPU and memory usage:
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### Manual Scaling
Scale manually if needed:
```bash
kubectl scale deployment hubspot-mcp-server -n production --replicas=5
```

## Security

### Network Policies
Network policies restrict traffic to necessary communications only:
- Ingress: Only from NGINX Ingress Controller
- Egress: HTTPS to HubSpot API and DNS resolution

### Pod Security Context
Pods run with restricted security context:
- Non-root user (UID: 1000)
- Read-only root filesystem
- Dropped capabilities

### Secret Management
- Secrets are managed via External Secrets Operator
- No secrets stored in Helm values or Git
- Automatic secret rotation supported

## Troubleshooting

### Common Issues

#### 1. External Secrets Not Syncing
```bash
# Check external secret status
kubectl describe externalsecret hubspot-mcp-secrets -n production

# Check secret store
kubectl describe clustersecretstore secret-store
```

#### 2. Pod Startup Issues
```bash
# Check pod logs
kubectl logs -f deployment/hubspot-mcp-server -n production

# Check pod events
kubectl describe pod <pod-name> -n production
```

#### 3. Ingress/TLS Issues
```bash
# Check ingress status
kubectl describe ingress hubspot-mcp-server -n production

# Check certificate status
kubectl describe certificate hubspot-mcp-server-prod-tls -n production
```

#### 4. Authentication Issues
```bash
# Test health endpoint (no auth required)
curl -k https://mcp-hubspot.keltio.fr/health

# Check ready endpoint for auth status
curl -k https://mcp-hubspot.keltio.fr/ready

# Verify auth header and key
curl -v -H "X-API-Key: your-key" https://mcp-hubspot.keltio.fr/sse
```

### Debug Authentication

The `/ready` endpoint provides authentication status information:
```json
{
  "status": "ready",
  "auth_enabled": true,
  "auth_header": "X-API-Key",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Upgrade

### Upgrade Process
```bash
# Update Helm repository
helm repo update

# Upgrade deployment
helm upgrade hubspot-mcp-server keltio/app-component \
  -f values-production.yaml \
  -n production \
  --wait \
  --timeout=10m
```

### Rollback
```bash
# List releases
helm history hubspot-mcp-server -n production

# Rollback to previous version
helm rollback hubspot-mcp-server 1 -n production
```

## Cleanup

To completely remove the deployment:
```bash
# Uninstall Helm release
helm uninstall hubspot-mcp-server -n production

# Remove namespace (optional)
kubectl delete namespace production
```

## Support

For issues with:
- **Helm Chart**: Check [Keltio Technology Helm Charts](https://gitlab.com/keltiotechnology/helm-charts)
- **External Secrets**: Check External Secrets Operator documentation
- **Application**: Check application logs and configuration 