#!/bin/bash
# Docker utility functions for build processes
# This file contains shared functions to avoid code duplication

# Colors for output (if not already defined)
if [[ -z "${RED:-}" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
fi

# Logging functions (if not already defined)
if ! declare -f log_info >/dev/null 2>&1; then
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
fi

# Function to authenticate with Docker registry
docker_authenticate() {
    local registry="${1:-${IMAGE_REGISTRY}}"
    local username="${2:-${REGISTRY_USERNAME:-nologin}}"
    
    if [[ -z "${REGISTRY_PASSWORD:-}" ]]; then
        log_error "REGISTRY_PASSWORD environment variable must be set"
        return 1
    fi
    
    log_info "Authenticating with registry: $registry"
    echo "$REGISTRY_PASSWORD" | docker login "$registry" -u "$username" --password-stdin
}

# Function to check if buildx is available and initialize if needed
docker_init_buildx() {
    if docker buildx version >/dev/null 2>&1; then
        log_info "Docker buildx is available"
        
        # Initialize buildx builder if not exists
        if ! docker buildx ls | grep -q "multiarch"; then
            log_info "Initializing buildx builder..."
            docker buildx create --name multiarch --use --bootstrap
        else
            log_info "Using existing buildx builder..."
            docker buildx use multiarch
        fi
        return 0
    else
        log_warning "Docker buildx not available"
        return 1
    fi
}

# Function to build Docker image with buildx
docker_build_with_buildx() {
    local image_name="$1"
    local push_flag="${2:-false}"
    local platform="${3:-linux/amd64}"
    
    log_info "Building image with buildx: $image_name"
    
    if [[ "$push_flag" == "true" ]]; then
        docker buildx build \
            --platform "$platform" \
            --tag "$image_name" \
            --push \
            .
        log_success "Image built and pushed with buildx: $image_name"
    else
        docker buildx build \
            --platform "$platform" \
            --tag "$image_name" \
            --load \
            .
        log_success "Image built locally with buildx: $image_name"
    fi
}

# Function to build Docker image with standard docker build
docker_build_standard() {
    local image_name="$1"
    local push_flag="${2:-false}"
    
    log_warning "Using standard docker build (may show warnings)"
    log_info "💡 Tip: Install docker-buildx-plugin for warning-free builds"
    
    log_info "Building image: $image_name"
    docker build --tag "$image_name" .
    
    if [[ "$push_flag" == "true" ]]; then
        log_info "Pushing image: $image_name"
        docker push "$image_name"
        log_success "Image built and pushed: $image_name"
    else
        log_success "Image built locally: $image_name"
    fi
}

# Main function to build Docker image (with automatic buildx detection)
docker_build_image() {
    local image_name="$1"
    local push_flag="${2:-false}"
    local platform="${3:-linux/amd64}"
    
    # Validate required parameters
    if [[ -z "$image_name" ]]; then
        log_error "Image name is required"
        return 1
    fi
    
    # Try buildx first, fallback to standard build
    if docker_init_buildx; then
        docker_build_with_buildx "$image_name" "$push_flag" "$platform"
    else
        docker_build_standard "$image_name" "$push_flag"
    fi
}

# Function to build and push Docker image with authentication
docker_build_and_push() {
    local image_name="$1"
    local registry="${2:-${IMAGE_REGISTRY}}"
    local username="${3:-${REGISTRY_USERNAME:-nologin}}"
    local platform="${4:-linux/amd64}"
    
    # Authenticate with registry
    if ! docker_authenticate "$registry" "$username"; then
        log_error "Failed to authenticate with Docker registry"
        return 1
    fi
    
    # Build and push image
    docker_build_image "$image_name" "true" "$platform"
}

# Function to build Docker image locally (no push)
docker_build_local() {
    local image_name="$1"
    local platform="${2:-linux/amd64}"
    
    docker_build_image "$image_name" "false" "$platform"
}

# Function to validate Docker build environment
docker_validate_environment() {
    local required_vars=("IMAGE_REGISTRY" "IMAGE_NAME" "IMAGE_TAG")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            return 1
        fi
    done
    
    # Check if docker is available
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is not installed or not in PATH"
        return 1
    fi
    
    log_info "Docker build environment validated"
    return 0
} 