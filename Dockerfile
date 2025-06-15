# Multi-stage Dockerfile for HubSpot MCP Server
FROM python:3.12-slim as builder

# Set build arguments
ARG UV_VERSION=0.4.27

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv==$UV_VERSION

# Set working directory
WORKDIR /app

# Copy dependency files and source code
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Build the package
RUN uv build

# Production stage
FROM python:3.12-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp -s /bin/false mcp

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv in production
RUN pip install uv==0.4.27

# Set working directory
WORKDIR /app

# Copy built wheel from builder stage
COPY --from=builder /app/dist/*.whl /tmp/

# Install the application
RUN uv pip install --system /tmp/*.whl && rm /tmp/*.whl

# Copy entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create app directory and change ownership
RUN chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["--mode", "sse", "--host", "0.0.0.0", "--port", "8080"]
