#!/bin/bash
set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source shared Docker utilities
source "$SCRIPT_DIR/docker-utils.sh"

# Configuration
NAMESPACE="${NAMESPACE:-production}"
RELEASE_NAME="${RELEASE_NAME:-hubspot-mcp-server}"
CHART_VERSION="${CHART_VERSION:-1.0.0}"
DOMAIN="${DOMAIN:-mcp-hubspot.keltio.fr}"
IMAGE_TAG="${IMAGE_TAG:-1.0.0}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-rg.fr-par.scw.cloud/keltio-public}"
REGISTRY_USERNAME="${REGISTRY_USERNAME:-nologin}"

# Colors and logging functions are already defined in docker-utils.sh

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."

    # Check required commands
    local required_commands=("kubectl" "helm" "docker")
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            log_error "$cmd is required but not installed"
            exit 1
        fi
    done

    # Check kubectl context
    local current_context=$(kubectl config current-context)
    log_info "Current kubectl context: $current_context"

    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_warning "Namespace $NAMESPACE does not exist, creating it..."
        kubectl create namespace "$NAMESPACE"
        kubectl label namespace "$NAMESPACE" name="$NAMESPACE"
    fi

    log_success "Prerequisites validated"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Checking Docker image availability..."

    local image_name="${IMAGE_REGISTRY}/hubspot-mcp-server:${IMAGE_TAG}"

    # Check if image already exists in registry
    if docker manifest inspect "$image_name" >/dev/null 2>&1; then
        log_success "Image already exists in registry: $image_name"
        return 0
    fi

    log_info "Building and pushing Docker image..."

    # Check if REGISTRY_PASSWORD is set for authentication
    if [[ -n "${REGISTRY_PASSWORD:-}" ]]; then
        # Use shared function for building and pushing
        if docker_build_and_push "$image_name" "$IMAGE_REGISTRY" "$REGISTRY_USERNAME"; then
            log_success "Image built and pushed: $image_name"
        else
            log_error "Failed to build and push image"
            return 1
        fi
    else
        log_warning "REGISTRY_PASSWORD not set, attempting build without push..."
        if docker_build_local "$image_name"; then
            log_success "Image built locally: $image_name"
            log_warning "Image was not pushed to registry (REGISTRY_PASSWORD not set)"
        else
            log_error "Failed to build image"
            return 1
        fi
    fi
}

# Deploy with Helm
deploy_helm_chart() {
    log_info "Deploying Helm chart..."

    # Update dependencies to pull from OCI
    helm dependency update .

    # Deploy directly with Helm using the local chart
    helm upgrade --install "$RELEASE_NAME" . \
        --namespace "$NAMESPACE" \
        --values ./values-production.yaml \
        --set image.repository="${IMAGE_REGISTRY}/hubspot-mcp-server" \
        --set image.tag="$IMAGE_TAG" \
        --set ingress.hosts[0].host="$DOMAIN" \
        --set ingress.tls[0].hosts[0]="$DOMAIN" \
        --wait \
        --timeout=600s

    log_success "Helm chart deployed successfully"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=hubspot-mcp-server -n "$NAMESPACE" --timeout=300s

    # Check deployment status
    kubectl get deployment "$RELEASE_NAME" -n "$NAMESPACE"
    kubectl get pods -l app.kubernetes.io/name=hubspot-mcp-server -n "$NAMESPACE"
    kubectl get services -l app.kubernetes.io/name=hubspot-mcp-server -n "$NAMESPACE"
    kubectl get ingress -n "$NAMESPACE"

    # Test health endpoint
    local service_url="https://$DOMAIN/health"
    log_info "Testing health endpoint: $service_url"

    # Wait a bit for ingress to be ready
    sleep 30

    if curl -f -s "$service_url" >/dev/null; then
        log_success "Health endpoint is responding"
    else
        log_warning "Health endpoint is not yet responding (this may take a few minutes for DNS/TLS)"
    fi

    log_success "Deployment verification completed"
}

# Main deployment function
deploy() {
    log_info "Starting deployment of HubSpot MCP Server..."
    log_info "Namespace: $NAMESPACE"
    log_info "Release: $RELEASE_NAME"
    log_info "Domain: $DOMAIN"
    log_info "Image: ${IMAGE_REGISTRY}/hubspot-mcp-server:${IMAGE_TAG}"

    validate_prerequisites
    build_and_push_image
    deploy_helm_chart
    verify_deployment

    log_success "Deployment completed successfully!"
    log_info "Access your MCP server at: https://$DOMAIN"
    log_info "Health check: https://$DOMAIN/health"
    log_info "Readiness check: https://$DOMAIN/ready"
}

# Rollback function
rollback() {
    local revision=${1:-}
    log_info "Rolling back deployment..."

    if [ -n "$revision" ]; then
        helm rollback "$RELEASE_NAME" "$revision" -n "$NAMESPACE"
    else
        helm rollback "$RELEASE_NAME" -n "$NAMESPACE"
    fi

    log_success "Rollback completed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up deployment..."

    helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"
    kubectl delete externalsecret hubspot-mcp-secrets -n "$NAMESPACE" --ignore-not-found
    kubectl delete secret hubspot-mcp-secrets -n "$NAMESPACE" --ignore-not-found

    log_success "Cleanup completed"
}

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback "${2:-}"
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|rollback [revision]|cleanup}"
        exit 1
        ;;
esac
