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