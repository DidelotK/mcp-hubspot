# Docker Setup for Warning-Free Builds

This document explains how to set up Docker with buildx to eliminate build warnings and improve the build experience.

## Current Status

The project's build scripts automatically detect whether Docker buildx is available:
- ✅ **With buildx**: Warning-free builds with advanced features
- ⚠️ **Without buildx**: Standard builds with potential warnings

## Why Use Docker Buildx?

Docker buildx provides several advantages:
- **No build warnings**: Clean, professional build output
- **Multi-platform support**: Build for different architectures
- **Advanced caching**: Faster subsequent builds
- **Better error reporting**: More informative build feedback
- **Modern build features**: Latest Docker build capabilities

## Installing Docker Buildx

### Ubuntu/Debian

```bash
# Install buildx plugin
sudo apt update
sudo apt install docker-buildx-plugin

# Verify installation
docker buildx version
```

### Alternative Installation Methods

#### Option 1: Manual Plugin Installation
```bash
# Download latest buildx plugin
BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -LO https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-amd64

# Install plugin
mkdir -p ~/.docker/cli-plugins
mv buildx-${BUILDX_VERSION}.linux-amd64 ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx
```

#### Option 2: Docker Desktop
If using Docker Desktop, buildx is included by default.

## Verification

After installation, verify buildx is working:

```bash
# Check buildx is available
docker buildx version

# List available builders
docker buildx ls

# Test with our project
cd mcp-hubspot
just docker-build-local
```

## Build Script Behavior

### With Buildx Available
```bash
just docker-build-local
# 🐳 Building Docker image locally...
# ✅ Using Docker buildx for warning-free builds...
# 📋 Initializing buildx builder...
# 🔨 Building image for local use with buildx...
# ✅ Docker image built locally with buildx!
```

### Without Buildx (Fallback)
```bash
just docker-build-local
# 🐳 Building Docker image locally...
# ⚠️  Docker buildx not available, using standard docker build...
# 💡 Install docker-buildx-plugin for warning-free builds
# 🔨 Building image for local use...
# ✅ Docker image built locally!
```

## Docker Permissions

If you see permission errors, ensure your user is in the docker group:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart session or run:
newgrp docker

# Verify docker access
docker info
```

## Common Build Warnings (Without Buildx)

Without buildx, you might see warnings like:
- `#1 [internal] load build definition from Dockerfile`
- `DEPRECATED: The legacy builder is deprecated...`
- Various caching and progress warnings

These are eliminated when using buildx.

## Environment Variables

The build commands use these environment variables:
- `IMAGE_REGISTRY`: Docker registry URL
- `IMAGE_NAME`: Image name
- `IMAGE_TAG`: Image tag
- `REGISTRY_PASSWORD`: Registry authentication

With direnv, these are automatically loaded from `deploy/environment`.

## Commands Available

### With Just (Recommended)
```bash
# Build locally (no push to registry)
just docker-build-local

# Build and push to registry
just docker-build

# Show build help
just help-build
```

### Direct Script Usage
```bash
# Using build script directly
./deploy/scripts/build-image.sh

# Using deploy script (includes build)
./deploy/scripts/deploy.sh
```

## Troubleshooting

### Buildx Not Found
```bash
# Check if plugin is installed
ls ~/.docker/cli-plugins/

# Check system package
dpkg -l | grep docker-buildx

# Reinstall if needed
sudo apt install --reinstall docker-buildx-plugin
```

### Builder Issues
```bash
# List builders
docker buildx ls

# Remove problematic builder
docker buildx rm multiarch

# Create new builder
docker buildx create --name multiarch --use --bootstrap
```

### Permission Issues
```bash
# Check docker group membership
groups $USER

# If docker not in groups, add it
sudo usermod -aG docker $USER
newgrp docker
```

## Best Practices

1. **Install buildx**: For the best development experience
2. **Use direnv**: Automatic environment variable management
3. **Use just commands**: Simplified build workflow
4. **Check permissions**: Ensure docker group membership
5. **Regular updates**: Keep buildx plugin updated

## Integration with CI/CD

For CI/CD pipelines, buildx is typically available in modern Docker environments:

```yaml
# GitHub Actions example
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  run: |
    docker buildx build \
      --platform linux/amd64 \
      --tag ${{ env.IMAGE_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }} \
      --push \
      .
```

## Summary

- **Recommended**: Install `docker-buildx-plugin` for warning-free builds
- **Automatic fallback**: Scripts work with or without buildx
- **Better experience**: Buildx provides cleaner output and advanced features
- **Easy setup**: Single package installation on Ubuntu/Debian 