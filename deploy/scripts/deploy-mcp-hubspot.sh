#!/bin/bash
set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
load_environment() {
    log_info "Loading environment configuration..."

    if [[ -f "$DEPLOY_DIR/environment" ]]; then
        source "$DEPLOY_DIR/environment"
        log_success "Environment loaded from $DEPLOY_DIR/environment"
    else
        log_error "Environment file not found at $DEPLOY_DIR/environment"
        exit 1
    fi

    # Validate required variables
    local required_vars=("NAMESPACE" "RELEASE_NAME" "IMAGE_TAG" "DOMAIN")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
}

# Create namespace with proper labels
create_namespace() {
    log_info "Creating namespace $NAMESPACE with proper labels..."

    if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_info "Namespace $NAMESPACE already exists"
    else
        log_info "Creating namespace $NAMESPACE..."
        kubectl create namespace "$NAMESPACE"
        log_success "Namespace $NAMESPACE created successfully"
    fi

    # Add required labels for External Secrets
    log_info "Adding labels to namespace..."
    kubectl label namespace "$NAMESPACE" external-secrets=true --overwrite
    kubectl label namespace "$NAMESPACE" name="$NAMESPACE" --overwrite
    kubectl label namespace "$NAMESPACE" kubernetes.io/metadata.name="$NAMESPACE" --overwrite

    log_success "Namespace $NAMESPACE configured with proper labels"
}

# Deploy using the existing script
deploy_application() {
    log_info "Deploying application using existing deployment script..."

    # Make sure we're in the deploy directory
    cd "$DEPLOY_DIR"

    # Source the environment again to ensure variables are available
    source "$DEPLOY_DIR/environment"

    # Run the existing deployment script
    if "$SCRIPT_DIR/deploy.sh" deploy; then
        log_success "Application deployed successfully"
    else
        log_error "Application deployment failed"
        exit 1
    fi
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Check namespace
    kubectl get namespace "$NAMESPACE"

    # Check if deployment exists and is ready
    if kubectl get deployment "$RELEASE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
        kubectl wait --for=condition=available deployment "$RELEASE_NAME" -n "$NAMESPACE" --timeout=300s

        # Show deployment status
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=hubspot-mcp-server
        kubectl get svc -n "$NAMESPACE"
        kubectl get ingress -n "$NAMESPACE"

        log_success "Deployment verification completed"
    else
        log_error "Deployment $RELEASE_NAME not found in namespace $NAMESPACE"
        exit 1
    fi
}

# Main deployment function
main() {
    log_info "=== HubSpot MCP Server Automated Deployment ==="
    log_info "Target namespace: $NAMESPACE"
    log_info "Release name: $RELEASE_NAME"
    log_info "Domain: $DOMAIN"

    load_environment
    create_namespace
    deploy_application
    verify_deployment

    log_success "=== Deployment completed successfully! ==="
    log_info "Your MCP server is available at: https://$DOMAIN"
    log_info "Health check: https://$DOMAIN/health"
    log_info "Ready check: https://$DOMAIN/ready"
}

# Error handling
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"
