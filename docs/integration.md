# Integration Guide

## Overview

This guide provides a comprehensive overview of integrating the HubSpot MCP Server with various clients and platforms. The integration documentation has been organized into dedicated guides for easier navigation and reference.

## 🔀 Installation Approaches

This server can be deployed in **two different ways** depending on your needs:

### 🏠 **Local Installation (stdio mode)**

**Best for:** Local development, and direct client integration

- ✅ Direct integration with Claude Desktop or any local MCP Client
- ✅ Runs locally on your machine
- ✅ Perfect for personal use
- ✅ Uses stdio protocol for communication
- ⚠️ **Requires MCP client configuration** (like Claude Desktop)

### 🌐 **Remote Deployment (SSE mode)**

**Best for:** Production environments, team usage, scalable deployments

- ✅ Production-ready Kubernetes deployment
- ✅ Scalable and highly available
- ✅ SSE (Server-Sent Events) protocol
- ✅ Authentication and security
- ✅ Multi-user support
- ⚠️ **Requires Kubernetes cluster and infrastructure setup**

---

## Integration Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude        │    │   Custom MCP    │    │   Web           │
│   Desktop       │    │   Client        │    │   Application   │
└─────┬───────────┘    └─────┬───────────┘    └─────┬───────────┘
      │                      │                      │
      │ stdio                │ stdio                │ HTTP/SSE
      │                      │                      │
┌─────▼──────────────────────▼──────────────────────▼───────────┐
│              HubSpot MCP Server                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   Tool Handler  │  │  Format Engine  │  │  Cache Manager  ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────┬─────────────────────────────────┘
                              │ HTTPS
                              │
                    ┌─────────▼─────────┐
                    │   HubSpot API     │
                    │   (api.hubapi.com)│
                    └───────────────────┘
```

---

## 🎯 Choose Your Installation Method

### For Claude Desktop Users (Recommended: Local)

**What this involves:**

- Installing Python dependencies locally
- Configuring HubSpot API credentials
- Setting up Claude Desktop MCP configuration
- Server runs when Claude Desktop starts

**Prerequisites:**

- Python 3.12+
- uv (package manager)
- HubSpot API key with CRM permissions

→ **[Complete Local Installation Guide](installation-local-stdio.md)**

### For Production/Team Deployment (Recommended: Remote)

**What this involves:**

- Kubernetes cluster setup and configuration
- External Secrets, Ingress, DNS configuration
- Production-grade security and monitoring
- Helm chart deployment and management

**Prerequisites:**

- Kubernetes cluster (>= 1.20)
- Helm 3
- External Secrets Operator
- NGINX Ingress Controller
- Cert-Manager
- External DNS

→ **[Complete Remote Deployment Guide](installation-remote-sse.md)**

---

## 🔌 MCP Clients Integration

**Quick Start:**

📖 **[Complete MCP Clients Integration Guide →](mcp-clients-integration.md)**
📖 **[Dedicated Claude Integration Guide →](claude-desktop-integration.md)**
