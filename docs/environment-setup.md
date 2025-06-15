# Environment Variables Management with direnv

This document provides complete instructions for setting up and using direnv for automatic environment variable management in the HubSpot MCP Server project.

## Overview

The project uses `direnv` for automatic environment variable management. This provides a seamless development experience where environment variables are automatically loaded when entering the project directory and unloaded when leaving.

### Benefits

1. **Security**: Secrets never appear in shell history
2. **Convenience**: No manual `export` commands needed
3. **Consistency**: Same setup process for all developers
4. **Isolation**: Variables don't pollute global environment
5. **Automation**: Integrates seamlessly with development workflow

## Installation

### 1. Install direnv

```bash
# Ubuntu/Debian
sudo apt install direnv

# macOS with Homebrew
brew install direnv

# Other systems: https://direnv.net/docs/installation.html
```

### 2. Configure your shell

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

## Project Setup

### 1. Create environment file

```bash
# Copy the template
cp deploy/environment.example deploy/environment

# Edit with your actual values
nano deploy/environment  # or your preferred editor
```

### 2. Configure your environment

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

### 3. Allow direnv

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

## Development Workflow

### Automatic Variable Loading

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
docker buildx build --platform linux/amd64 --tag $IMAGE_REGISTRY/$IMAGE_NAME:$IMAGE_TAG --push .
./deploy/scripts/build-image.sh   # Uses loaded variables automatically

# Leave directory → variables automatically unload
cd /other/directory
echo $IMAGE_TAG                   # → (empty)
```

### Manual Commands

#### Essential Commands

```bash
# Allow direnv for current directory
direnv allow

# Reload environment (after changes)
direnv reload

# Check direnv status
direnv status

# Manually trigger reload
direnv exec . bash

# Disable direnv temporarily
direnv deny
```

#### Development Workflow

```bash
# 1. Enter project directory → variables auto-load
cd /path/to/project
# 🔧 Loading environment variables...
# ✅ Environment variables loaded successfully!

# 2. Work with loaded variables
docker buildx build --platform linux/amd64 --tag $IMAGE_REGISTRY/app:$IMAGE_TAG --push .
./deploy/scripts/build-image.sh

# 3. Exit directory → variables auto-unload
cd /other/directory
# Variables are automatically cleaned from environment
```

## Security

### File Permissions

```bash
# Secure your environment file
chmod 600 deploy/environment

# Verify git ignores it
git status --ignored | grep deploy/environment
```

### What's Versioned

- ✅ **`.envrc`** - Direnv configuration (no secrets)
- ✅ **`deploy/environment.example`** - Template file
- ❌ **`deploy/environment`** - Your actual config (contains secrets)

### Best Practices

- Never commit `deploy/environment` to git
- Use strong, unique passwords and API keys
- Regularly rotate secrets, especially API keys
- Keep `deploy/environment.example` updated with new variables

## Troubleshooting

### Common Issues

#### Variables not loading

```bash
# Check direnv status
direnv status

# Force reload
direnv reload

# Check if file exists and has correct permissions
ls -la deploy/environment
```

#### Permission denied

```bash
# Fix file permissions
chmod 600 deploy/environment

# Re-allow direnv
direnv allow
```

#### Variables persist after leaving directory

```bash
# Check if direnv hook is properly installed
echo $DIRENV_DIR  # Should be empty outside project

# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc
```

### Debugging

```bash
# Verbose direnv output
DIRENV_LOG_FORMAT="$(printf "%%s \033[2mdirenv: %%s\033[0m")" direnv allow

# Check which variables are set
direnv exec . env | grep -E "(IMAGE_|REGISTRY_|HUBSPOT_)"
```

### Getting Help

If environment file is missing, you'll see:

```bash
cd mcp-hubspot
# ⚠️  Environment file not found!
#
# 📝 To set up your environment:
#    1. Copy the example file:
#       cp deploy/environment.example deploy/environment
#    2. Edit deploy/environment with your values
#    3. Run 'direnv allow' to reload this configuration
```

## Integration with Development Tools

### IDE Configuration

Most IDEs support direnv through plugins:

- **VS Code**: `direnv` extension
- **JetBrains**: `direnv` plugin
- **Vim**: `direnv.vim` plugin

### CI/CD Integration

For CI/CD pipelines, export variables manually:

```bash
# In CI scripts
export IMAGE_TAG="$CI_COMMIT_TAG"
export REGISTRY_PASSWORD="$CI_REGISTRY_PASSWORD"
```

## How It Works

### .envrc Configuration

The `.envrc` file automatically:

- Checks if `deploy/environment` exists
- Loads all variables using `set -a` + `source` + `set +a` technique
- Displays helpful setup instructions if file is missing
- Shows current configuration status

```bash
#!/bin/bash
# Example .envrc structure
if [ -f "deploy/environment" ]; then
    # Load environment variables
    set -a
    source deploy/environment
    set +a

    echo "✅ Environment loaded!"
else
    echo "⚠️ Please create deploy/environment from deploy/environment.example"
fi
```

### Security Implementation

The system ensures that:

- Secrets are stored in `deploy/environment` (not versioned)
- No secrets are embedded in `.envrc` (versioned)
- Variables are automatically cleaned when leaving the directory
- File permissions are secure (600 for environment file)

## Docker Registry Authentication

With direnv, Scaleway authentication becomes seamless:

```bash
# Variables are automatically available
docker login $REGISTRY_URL -u $REGISTRY_USERNAME --password-stdin <<< "$REGISTRY_PASSWORD"

# Initialize buildx builder
docker buildx create --name multiarch --use --bootstrap

# Build and push with loaded variables using buildx
docker buildx build \
    --platform linux/amd64 \
    --tag $IMAGE_REGISTRY/$IMAGE_NAME:$IMAGE_TAG \
    --push \
    .
```

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `IMAGE_REGISTRY` | Docker registry URL | `rg.fr-par.scw.cloud/keltio-public` |
| `IMAGE_NAME` | Docker image name | `hubspot-mcp-server` |
| `IMAGE_TAG` | Docker image tag | `0.1.0` |
| `REGISTRY_USERNAME` | Registry username | `nologin` |
| `REGISTRY_PASSWORD` | Registry password | `your-scaleway-password` |
| `HUBSPOT_API_KEY` | HubSpot API key | `pat-eu1-your-key` |
| `MCP_AUTH_KEY` | MCP authentication key | `your-secure-key` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_AUTH_HEADER` | Auth header name | `X-API-Key` |
| `NAMESPACE` | Kubernetes namespace | `production` |
| `DOMAIN` | Application domain | `mcp-hubspot.keltio.fr` |

## Migration from Manual Export

If you were previously using manual `export` commands:

### Before (Manual)

```bash
export IMAGE_TAG=0.1.0
export REGISTRY_PASSWORD=your-password
docker build -t registry/app:$IMAGE_TAG .
docker push registry/app:$IMAGE_TAG
```

### After (direnv)

```bash
# Just enter the directory
cd mcp-hubspot
# Variables are automatically available
docker buildx build --platform linux/amd64 --tag $IMAGE_REGISTRY/$IMAGE_NAME:$IMAGE_TAG --push .
```

## Best Practices

1. **Always use the template**: Start from `deploy/environment.example`
2. **Secure permissions**: `chmod 600 deploy/environment`
3. **Update template**: Keep `deploy/environment.example` current
4. **Document changes**: Update this file when adding new variables
5. **Test setup**: Verify `direnv allow` works correctly
6. **Regular rotation**: Rotate secrets periodically
7. **Clean environment**: Don't export variables manually when using direnv
