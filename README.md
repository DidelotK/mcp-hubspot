# HubSpot MCP Server

MCP (Model Context Protocol) server for integrating HubSpot with Claude Desktop and other MCP clients. Provides access to HubSpot contacts, companies, and deals through conversational tools.

## 🔀 Installation Approaches

This server can be deployed in **two different ways** depending on your needs:

### 🏠 **Local Installation (stdio mode)**
**Best for:** Claude Desktop integration, local development, and direct client integration

- ✅ Direct integration with Claude Desktop
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

## 📚 Documentation Table of Contents

### 🚀 Getting Started

| Section | Description | Best For |
|---------|-------------|----------|
| **[Local Installation (stdio)](docs/installation-local-stdio.md)** | Install and run locally for Claude Desktop | Personal use, development |
| **[Remote Deployment (SSE)](docs/installation-remote-sse.md)** | Deploy to Kubernetes for production use | Teams, production, scalability |
| **[Configuration Guide](docs/configuration.md)** | Environment setup and API configuration | Both approaches |
| **[Client Integration](docs/integration.md)** | Configure Claude Desktop and other MCP clients | Both approaches |

### 🔧 Usage and Features

| Section | Description |
|---------|-------------|
| **[API Reference](docs/api-reference.md)** | Complete documentation of the 14 available tools |
| **[Semantic Search](docs/semantic-search.md)** | AI-powered semantic search capabilities and usage |
| **[Cache System](docs/caching.md)** | How the shared TTL cache works and how to manage it |
| **[Examples](docs/examples.md)** | Use cases and example conversations with Claude |

### 🛠️ Development and Testing

| Section | Description |
|---------|-------------|
| **[Developer Guide](docs/developer.md)** | Testing, quality assurance, and development workflow |
| **[Contributing](docs/contributing.md)** | Guide for developing new tools |
| **[Troubleshooting](docs/troubleshooting.md)** | Common issues and solutions |
| **[Integration Testing](docs/integration-testing.md)** | Comprehensive testing procedures |

### 📋 Advanced Topics

| Section | Description |
|---------|-------------|
| **[Docker Setup](docs/docker-setup.md)** | Docker configuration and containerization |
| **[Environment Setup](docs/environment-setup.md)** | Advanced environment configuration |
| **[MCP Clients Integration](docs/mcp-clients-integration.md)** | Integration with various MCP clients |

---

## 🛠️ Available Tools

The server provides **14 tools** for comprehensive HubSpot integration:

| Category | Tools | Description |
|----------|--------|-------------|
| **Contacts** | `list_hubspot_contacts`<br/>`get_hubspot_contact_properties` | List contacts and retrieve contact field properties |
| **Companies** | `list_hubspot_companies`<br/>`get_hubspot_company_properties` | List companies and retrieve company field properties |
| **Deals** | `list_hubspot_deals`<br/>`search_hubspot_deals`<br/>`create_deal`<br/>`update_deal`<br/>`get_deal_by_name`<br/>`get_hubspot_deal_properties` | Complete deal management and search capabilities |
| **Engagements** | `list_hubspot_engagements` | List HubSpot engagements with pagination support |
| **AI Search** | `semantic_search_hubspot`<br/>`manage_hubspot_embeddings` | AI-powered semantic search using natural language |
| **System** | `manage_hubspot_cache` | Cache management and statistics |

---

## ⚡ Usage Examples

**Once fully installed and configured** (following the complete installation guides), use natural language phrases with your MCP client:

### 🗣️ **Natural Language Queries**
- *"List my HubSpot contacts"*
- *"Find tech sector companies"*
- *"Show current deals"*
- *"Create a new deal for Project X"*
- *"Search for the 'Project X' deal"*
- *"What contact properties are available?"*

### 🤖 **AI-Powered Semantic Search**
- *"Find software engineers"* → matches "Developer", "Programmer", "Software Architect"
- *"Search for enterprise clients"* → finds large companies without exact keywords
- *"Technology companies in Paris"* → contextual location and industry search

---

## 🎯 Choose Your Installation Method

### For Claude Desktop Users (Recommended: Local)
**What this involves:**
- Installing Python dependencies locally
- Configuring HubSpot API credentials
- Setting up Claude Desktop MCP configuration
- Server runs when Claude Desktop starts

→ **[Complete Local Installation Guide](docs/installation-local-stdio.md)**

### For Production/Team Deployment (Recommended: Remote)
**What this involves:**
- Kubernetes cluster setup and configuration
- External Secrets, Ingress, DNS configuration
- Production-grade security and monitoring
- Helm chart deployment and management

→ **[Complete Remote Deployment Guide](docs/installation-remote-sse.md)**

---

## 🧪 Testing and Quality

Both installation methods include comprehensive testing:

```bash
# Local development testing
just check  # Runs all quality checks

# Remote deployment testing  
./deploy/scripts/test-sse-mcp.sh  # Tests SSE functionality
```

**Current Status:** ✅ 330+ tests passed, 97% coverage, comprehensive AI/embedding functionality

---

## 📋 Prerequisites

### For Local Installation
- Python 3.12+
- uv (package manager)
- HubSpot API key with CRM permissions

### For Remote Deployment
- Kubernetes cluster (>= 1.20)
- Helm 3
- External Secrets Operator
- NGINX Ingress Controller
- Cert-Manager
- External DNS

## 🔐 Secure Environment Configuration

The project uses a secure approach for handling sensitive information:

### 🛡️ **Local Development Setup**

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env.local
   ```

2. **Edit `.env.local` with your real secrets:**
   ```bash
   # Replace with your actual HubSpot API key
   HUBSPOT_API_KEY="pat-na1-your-actual-api-key-here"
   ```

3. **The environment loads automatically with direnv:**
   ```bash
   direnv allow  # Enables automatic loading
   ```

### 🔒 **Security Features**

- ✅ **`.env.local`** - Contains your real secrets (never committed)
- ✅ **`.env.example`** - Safe template file (committed to git)
- ✅ **`.envrc`** - Automatically sources `.env.local` if available
- ✅ **Git protection** - `.env.local` is in `.gitignore`
- ✅ **Clean history** - All secrets removed from Git history

### ⚠️ **Important Security Notes**

- **Never commit** `.env.local` - it contains your real API keys
- **Always use** `.env.example` as a template for new setups
- **Git history** has been cleaned of any exposed secrets
- **Production deployments** use Kubernetes secrets via External Secrets Operator

---

## 🤝 Contributing

Check the [contributing guide](docs/contributing.md) for:
- Development standards
- Tool creation process
- Code and testing conventions
- Git workflow and semantic versioning

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Quick Links

### 🏠 Local Installation
- [Complete Local Setup Guide](docs/installation-local-stdio.md)
- [Claude Desktop Configuration](docs/integration.md#claude-desktop-integration)
- [Local Development Workflow](docs/developer.md)

### 🌐 Remote Deployment
- [Kubernetes Deployment Guide](docs/installation-remote-sse.md)
- [SSE Testing Scripts](docs/installation-remote-sse.md#testing-and-monitoring)
- [Production Configuration](docs/installation-remote-sse.md#configuration-files)

### 📖 General Documentation
- [All Available Tools](docs/api-reference.md)
- [Usage Examples](docs/examples.md)
- [Troubleshooting](docs/troubleshooting.md)
