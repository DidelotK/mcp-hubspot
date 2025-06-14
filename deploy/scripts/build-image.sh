#!/bin/bash
set -euo pipefail

# Configuration
IMAGE_NAME="${IMAGE_NAME:-hubspot-mcp-server}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-rg.fr-par.scw.cloud/keltio-public}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY_USERNAME="${REGISTRY_USERNAME:-nologin}"

# Ensure REGISTRY_PASSWORD is set
if [[ -z "${REGISTRY_PASSWORD:-}" ]]; then
    echo "Error: REGISTRY_PASSWORD environment variable must be set"
    exit 1
fi

# Docker authentication
echo "Authenticating with Scaleway Container Registry..."
echo "$REGISTRY_PASSWORD" | docker login "$IMAGE_REGISTRY" -u "$REGISTRY_USERNAME" --password-stdin

# Check if buildx is available
if docker buildx version >/dev/null 2>&1; then
    echo "Using Docker buildx for warning-free builds..."
    
    # Initialize buildx builder if not exists
    echo "Initializing Docker buildx..."
    if ! docker buildx ls | grep -q "multiarch"; then
        docker buildx create --name multiarch --use --bootstrap
    else
        docker buildx use multiarch
    fi

    # Build and push image using buildx
    echo "Building Docker image with buildx: ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    docker buildx build \
        --platform linux/amd64 \
        --tag "${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" \
        --push \
        .
    
    echo "Image built and pushed successfully with buildx!"
else
    echo "Docker buildx not available, using standard docker build..."
    echo "Note: You may see some warnings. Install docker-buildx package to eliminate them."
    
    # Build image with standard docker build
    echo "Building Docker image: ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    docker build \
        --tag "${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" \
        .

    echo "Pushing Docker image: ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    docker push "${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    
    echo "Image built and pushed successfully!"
    echo "💡 Tip: Install docker-buildx for better build experience: sudo apt install docker-buildx-plugin"
fi 