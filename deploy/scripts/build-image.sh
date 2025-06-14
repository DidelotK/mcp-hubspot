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

# Build and push image
echo "Building Docker image: ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t "${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" .

echo "Pushing Docker image: ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
docker push "${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Image built and pushed successfully!" 