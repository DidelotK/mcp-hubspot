#!/bin/bash
set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source shared Docker utilities
source "$SCRIPT_DIR/docker-utils.sh"

# Configuration
IMAGE_NAME="${IMAGE_NAME:-hubspot-mcp-server}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-rg.fr-par.scw.cloud/keltio-public}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY_USERNAME="${REGISTRY_USERNAME:-nologin}"

# Validate environment
if ! docker_validate_environment; then
    exit 1
fi

# Build full image name
FULL_IMAGE_NAME="${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

log_info "Building and pushing Docker image: $FULL_IMAGE_NAME"

# Build and push image using shared function
if docker_build_and_push "$FULL_IMAGE_NAME" "$IMAGE_REGISTRY" "$REGISTRY_USERNAME"; then
    log_success "Docker image build and push completed successfully!"
else
    log_error "Docker image build and push failed!"
    exit 1
fi
