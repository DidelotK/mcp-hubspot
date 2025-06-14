#!/bin/bash
set -euo pipefail

# Configuration
IMAGE_NAME="${IMAGE_NAME:-hubspot-mcp-server}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-your-registry}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Build and push image
echo "Building Docker image: ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t "${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" .

echo "Pushing Docker image: ${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
docker push "${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Image built and pushed successfully!" 