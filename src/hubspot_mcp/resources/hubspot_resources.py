"""HubSpot MCP Server resources for client guidance."""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import mcp.types as types


class HubSpotResources:
    """Collection of resources to help MCP clients use HubSpot tools effectively."""

    @staticmethod
    def get_resource_definitions() -> List[types.Resource]:
        """Get all available resource definitions.

        Returns:
            List[types.Resource]: List of all resource definitions
        """
        return [
            HubSpotResources._get_tool_examples_resource(),
            HubSpotResources._get_field_mappings_resource(),
            HubSpotResources._get_configuration_template_resource(),
            HubSpotResources._get_best_practices_resource(),
            HubSpotResources._get_troubleshooting_resource(),
            HubSpotResources._get_api_reference_resource(),
        ]

    @staticmethod
    def _get_tool_examples_resource() -> types.Resource:
        """Resource with JSON examples for all tools."""
        return types.Resource(
            uri="hubspot://examples/tools",
            name="HubSpot Tool Usage Examples",
            description="Complete JSON examples for all 18 HubSpot MCP tools with common use cases",
            mimeType="application/json",
        )

    @staticmethod
    def _get_field_mappings_resource() -> types.Resource:
        """Resource with HubSpot field mappings and schemas."""
        return types.Resource(
            uri="hubspot://schemas/fields",
            name="HubSpot Field Mappings",
            description="Complete field mappings, schemas, and property definitions for contacts, companies, deals, and engagements",
            mimeType="application/json",
        )

    @staticmethod
    def _get_configuration_template_resource() -> types.Resource:
        """Resource with configuration templates."""
        return types.Resource(
            uri="hubspot://config/template",
            name="Server Configuration Template",
            description="Complete configuration template with environment variables, authentication setup, and deployment options",
            mimeType="application/json",
        )

    @staticmethod
    def _get_best_practices_resource() -> types.Resource:
        """Resource with best practices guide."""
        return types.Resource(
            uri="hubspot://guides/best-practices",
            name="HubSpot MCP Best Practices",
            description="Comprehensive best practices guide for optimal performance, caching strategies, and API usage patterns",
            mimeType="text/markdown",
        )

    @staticmethod
    def _get_troubleshooting_resource() -> types.Resource:
        """Resource with troubleshooting guide."""
        return types.Resource(
            uri="hubspot://guides/troubleshooting",
            name="Troubleshooting Guide",
            description="Common issues, error codes, and solutions for HubSpot MCP server integration",
            mimeType="text/markdown",
        )

    @staticmethod
    def _get_api_reference_resource() -> types.Resource:
        """Resource with condensed API reference."""
        return types.Resource(
            uri="hubspot://docs/api-reference",
            name="HubSpot API Quick Reference",
            description="Condensed reference of HubSpot API endpoints, parameters, and response formats used by MCP tools",
            mimeType="text/markdown",
        )

    @staticmethod
    def read_resource(uri: str) -> str:
        """Read the content of a resource by URI.

        Args:
            uri: The URI of the resource to read

        Returns:
            str: The content of the resource

        Raises:
            ValueError: If the resource URI is not found
        """
        resource_map = {
            "hubspot://examples/tools": HubSpotResources._generate_tool_examples,
            "hubspot://schemas/fields": HubSpotResources._generate_field_mappings,
            "hubspot://config/template": HubSpotResources._generate_configuration_template,
            "hubspot://guides/best-practices": HubSpotResources._generate_best_practices,
            "hubspot://guides/troubleshooting": HubSpotResources._generate_troubleshooting,
            "hubspot://docs/api-reference": HubSpotResources._generate_api_reference,
        }

        if uri not in resource_map:
            raise ValueError(f"Resource not found: {uri}")

        return resource_map[uri]()

    @staticmethod
    def _generate_tool_examples() -> str:
        """Generate comprehensive tool usage examples."""
        examples = {
            "hubspot_mcp_tool_examples": {
                "version": "1.0.0",
                "description": "Complete JSON examples for all HubSpot MCP tools",
                "tools": {
                    "entity_listing": {
                        "list_hubspot_contacts": [
                            {
                                "name": "list_hubspot_contacts",
                                "arguments": {},
                                "description": "List first 100 contacts with default properties",
                            },
                            {
                                "name": "list_hubspot_contacts",
                                "arguments": {"limit": 10, "after": "cursor123"},
                                "description": "List 10 contacts with pagination",
                            },
                        ],
                        "list_hubspot_companies": [
                            {
                                "name": "list_hubspot_companies",
                                "arguments": {"limit": 50},
                                "description": "List first 50 companies",
                            }
                        ],
                        "list_hubspot_deals": [
                            {
                                "name": "list_hubspot_deals",
                                "arguments": {"limit": 25},
                                "description": "List first 25 deals",
                            }
                        ],
                        "list_hubspot_engagements": [
                            {
                                "name": "list_hubspot_engagements",
                                "arguments": {"limit": 20},
                                "description": "List first 20 engagements",
                            }
                        ],
                    },
                    "properties": {
                        "get_hubspot_contact_properties": [
                            {
                                "name": "get_hubspot_contact_properties",
                                "arguments": {},
                                "description": "Get all contact field definitions and schemas",
                            }
                        ],
                        "get_hubspot_company_properties": [
                            {
                                "name": "get_hubspot_company_properties",
                                "arguments": {},
                                "description": "Get all company field definitions and schemas",
                            }
                        ],
                        "get_hubspot_deal_properties": [
                            {
                                "name": "get_hubspot_deal_properties",
                                "arguments": {},
                                "description": "Get all deal field definitions and schemas",
                            }
                        ],
                    },
                    "search_and_filtering": {
                        "search_hubspot_contacts": [
                            {
                                "name": "search_hubspot_contacts",
                                "arguments": {
                                    "filters": {"email": "@techcorp.com"},
                                    "limit": 50,
                                },
                                "description": "Search contacts by email domain",
                            },
                            {
                                "name": "search_hubspot_contacts",
                                "arguments": {
                                    "filters": {
                                        "firstname": "John",
                                        "lastname": "Smith",
                                    }
                                },
                                "description": "Search contacts by name",
                            },
                        ],
                        "search_hubspot_companies": [
                            {
                                "name": "search_hubspot_companies",
                                "arguments": {
                                    "filters": {"industry": "TECHNOLOGY"},
                                    "limit": 100,
                                },
                                "description": "Search technology companies",
                            }
                        ],
                        "search_hubspot_deals": [
                            {
                                "name": "search_hubspot_deals",
                                "arguments": {
                                    "filters": {
                                        "dealstage": "presentation",
                                        "pipeline": "default",
                                    }
                                },
                                "description": "Search deals in presentation stage",
                            }
                        ],
                    },
                    "deal_management": {
                        "get_deal_by_name": [
                            {
                                "name": "get_deal_by_name",
                                "arguments": {
                                    "deal_name": "Enterprise Software License"
                                },
                                "description": "Find specific deal by exact name",
                            }
                        ],
                        "create_deal": [
                            {
                                "name": "create_deal",
                                "arguments": {
                                    "dealname": "New Enterprise Deal",
                                    "amount": "50000",
                                    "pipeline": "default",
                                    "dealstage": "appointment",
                                },
                                "description": "Create new deal with basic properties",
                            }
                        ],
                        "update_deal": [
                            {
                                "name": "update_deal",
                                "arguments": {
                                    "deal_id": "12345",
                                    "properties": {
                                        "dealstage": "presentation",
                                        "amount": "75000",
                                    },
                                },
                                "description": "Update deal stage and amount",
                            }
                        ],
                    },
                    "ai_powered_search": {
                        "semantic_search_hubspot": [
                            {
                                "name": "semantic_search_hubspot",
                                "arguments": {
                                    "query": "software engineers in Paris",
                                    "limit": 10,
                                },
                                "description": "Natural language search for contacts",
                            },
                            {
                                "name": "semantic_search_hubspot",
                                "arguments": {
                                    "query": "enterprise technology companies",
                                    "entity_types": ["companies"],
                                    "search_mode": "hybrid",
                                },
                                "description": "Hybrid search for companies only",
                            },
                        ],
                        "manage_hubspot_embeddings": [
                            {
                                "name": "manage_hubspot_embeddings",
                                "arguments": {"action": "info"},
                                "description": "Get embedding index status",
                            },
                            {
                                "name": "manage_hubspot_embeddings",
                                "arguments": {
                                    "action": "build",
                                    "entity_types": ["contacts", "companies"],
                                },
                                "description": "Build AI search index",
                            },
                        ],
                        "browse_hubspot_indexed_data": [
                            {
                                "name": "browse_hubspot_indexed_data",
                                "arguments": {"action": "stats"},
                                "description": "View index statistics",
                            },
                            {
                                "name": "browse_hubspot_indexed_data",
                                "arguments": {
                                    "action": "search",
                                    "search_text": "technology",
                                },
                                "description": "Search indexed content",
                            },
                        ],
                    },
                    "cache_and_performance": {
                        "load_hubspot_entities_to_cache": [
                            {
                                "name": "load_hubspot_entities_to_cache",
                                "arguments": {
                                    "entity_type": "contacts",
                                    "build_embeddings": True,
                                    "max_entities": 5000,
                                },
                                "description": "Bulk load contacts with AI indexing",
                            }
                        ],
                        "manage_hubspot_cache": [
                            {
                                "name": "manage_hubspot_cache",
                                "arguments": {"action": "info"},
                                "description": "View cache statistics",
                            },
                            {
                                "name": "manage_hubspot_cache",
                                "arguments": {"action": "clear"},
                                "description": "Clear all cached data",
                            },
                        ],
                    },
                },
            }
        }

        return json.dumps(examples, indent=2)

    @staticmethod
    def _generate_field_mappings() -> str:
        """Generate HubSpot field mappings and schemas."""
        mappings = {
            "hubspot_field_mappings": {
                "version": "1.0.0",
                "description": "HubSpot field mappings and schemas for MCP tools",
                "entities": {
                    "contacts": {
                        "standard_properties": [
                            {
                                "name": "firstname",
                                "type": "string",
                                "description": "Contact's first name",
                            },
                            {
                                "name": "lastname",
                                "type": "string",
                                "description": "Contact's last name",
                            },
                            {
                                "name": "email",
                                "type": "string",
                                "description": "Primary email address",
                            },
                            {
                                "name": "phone",
                                "type": "string",
                                "description": "Primary phone number",
                            },
                            {
                                "name": "company",
                                "type": "string",
                                "description": "Company name",
                            },
                            {
                                "name": "jobtitle",
                                "type": "string",
                                "description": "Job title",
                            },
                            {
                                "name": "hubspot_owner_id",
                                "type": "string",
                                "description": "Owner ID in HubSpot",
                            },
                            {
                                "name": "createdate",
                                "type": "datetime",
                                "description": "Creation timestamp",
                            },
                            {
                                "name": "lastmodifieddate",
                                "type": "datetime",
                                "description": "Last modification timestamp",
                            },
                            {
                                "name": "lifecyclestage",
                                "type": "enumeration",
                                "description": "Contact lifecycle stage",
                            },
                        ],
                        "search_filters": {
                            "email": "CONTAINS_TOKEN",
                            "firstname": "CONTAINS_TOKEN",
                            "lastname": "CONTAINS_TOKEN",
                            "company": "CONTAINS_TOKEN",
                            "hubspot_owner_id": "EQ",
                            "lifecyclestage": "EQ",
                        },
                    },
                    "companies": {
                        "standard_properties": [
                            {
                                "name": "name",
                                "type": "string",
                                "description": "Company name",
                            },
                            {
                                "name": "domain",
                                "type": "string",
                                "description": "Company domain",
                            },
                            {
                                "name": "industry",
                                "type": "enumeration",
                                "description": "Industry category",
                            },
                            {
                                "name": "city",
                                "type": "string",
                                "description": "Company city",
                            },
                            {
                                "name": "state",
                                "type": "string",
                                "description": "Company state/region",
                            },
                            {
                                "name": "country",
                                "type": "string",
                                "description": "Company country",
                            },
                            {
                                "name": "phone",
                                "type": "string",
                                "description": "Company phone",
                            },
                            {
                                "name": "numberofemployees",
                                "type": "number",
                                "description": "Employee count",
                            },
                            {
                                "name": "annualrevenue",
                                "type": "number",
                                "description": "Annual revenue",
                            },
                            {
                                "name": "hubspot_owner_id",
                                "type": "string",
                                "description": "Owner ID in HubSpot",
                            },
                        ],
                        "search_filters": {
                            "name": "CONTAINS_TOKEN",
                            "domain": "CONTAINS_TOKEN",
                            "industry": "EQ",
                            "city": "CONTAINS_TOKEN",
                            "country": "CONTAINS_TOKEN",
                            "hubspot_owner_id": "EQ",
                        },
                    },
                    "deals": {
                        "standard_properties": [
                            {
                                "name": "dealname",
                                "type": "string",
                                "description": "Deal name",
                            },
                            {
                                "name": "amount",
                                "type": "number",
                                "description": "Deal value",
                            },
                            {
                                "name": "dealstage",
                                "type": "enumeration",
                                "description": "Current deal stage",
                            },
                            {
                                "name": "pipeline",
                                "type": "enumeration",
                                "description": "Sales pipeline",
                            },
                            {
                                "name": "closedate",
                                "type": "date",
                                "description": "Expected close date",
                            },
                            {
                                "name": "hubspot_owner_id",
                                "type": "string",
                                "description": "Deal owner ID",
                            },
                            {
                                "name": "dealtype",
                                "type": "enumeration",
                                "description": "Type of deal",
                            },
                            {
                                "name": "createdate",
                                "type": "datetime",
                                "description": "Creation timestamp",
                            },
                            {
                                "name": "source",
                                "type": "enumeration",
                                "description": "Deal source",
                            },
                        ],
                        "search_filters": {
                            "dealname": "CONTAINS_TOKEN",
                            "dealstage": "EQ",
                            "pipeline": "EQ",
                            "hubspot_owner_id": "EQ",
                            "amount": "GT",
                            "closedate": "GT",
                        },
                    },
                    "engagements": {
                        "standard_properties": [
                            {
                                "name": "type",
                                "type": "enumeration",
                                "description": "Engagement type (EMAIL, CALL, MEETING, etc.)",
                            },
                            {
                                "name": "subject",
                                "type": "string",
                                "description": "Engagement subject",
                            },
                            {
                                "name": "body",
                                "type": "string",
                                "description": "Engagement content",
                            },
                            {
                                "name": "timestamp",
                                "type": "datetime",
                                "description": "Engagement timestamp",
                            },
                            {
                                "name": "hubspot_owner_id",
                                "type": "string",
                                "description": "Owner ID",
                            },
                            {
                                "name": "status",
                                "type": "enumeration",
                                "description": "Engagement status",
                            },
                        ],
                        "search_filters": {
                            "type": "EQ",
                            "subject": "CONTAINS_TOKEN",
                            "hubspot_owner_id": "EQ",
                            "timestamp": "GT",
                        },
                    },
                },
                "api_endpoints": {
                    "contacts": "https://api.hubapi.com/crm/v3/objects/contacts",
                    "companies": "https://api.hubapi.com/crm/v3/objects/companies",
                    "deals": "https://api.hubapi.com/crm/v3/objects/deals",
                    "engagements": "https://api.hubapi.com/crm/v3/objects/engagements",
                },
                "filter_operators": {
                    "EQ": "Equal to",
                    "NEQ": "Not equal to",
                    "LT": "Less than",
                    "LTE": "Less than or equal to",
                    "GT": "Greater than",
                    "GTE": "Greater than or equal to",
                    "CONTAINS_TOKEN": "Contains (partial match)",
                    "NOT_CONTAINS_TOKEN": "Does not contain",
                },
            }
        }

        return json.dumps(mappings, indent=2)

    @staticmethod
    def _generate_configuration_template() -> str:
        """Generate server configuration template."""
        config = {
            "hubspot_mcp_configuration": {
                "version": "1.0.0",
                "description": "Complete configuration template for HubSpot MCP Server",
                "environment_variables": {
                    "required": {
                        "HUBSPOT_API_KEY": {
                            "description": "HubSpot private app access token",
                            "example": "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                            "source": "HubSpot Developer Account > Private Apps",
                        }
                    },
                    "optional": {
                        "HUBSPOT_BASE_URL": {
                            "description": "HubSpot API base URL (change for different regions)",
                            "default": "https://api.hubapi.com",
                            "examples": [
                                "https://api.hubapi.com",
                                "https://api.hubapi.eu",
                            ],
                        },
                        "MCP_AUTH_KEY": {
                            "description": "Authentication key for MCP server (SSE mode)",
                            "example": "your-secret-auth-key",
                            "note": "Required for production SSE deployments",
                        },
                        "MCP_AUTH_HEADER": {
                            "description": "HTTP header name for authentication",
                            "default": "X-API-Key",
                        },
                        "HOST": {
                            "description": "Host to bind SSE server",
                            "default": "localhost",
                        },
                        "PORT": {
                            "description": "Port for SSE server",
                            "default": "8080",
                            "type": "integer",
                        },
                        "MODE": {
                            "description": "Server communication mode",
                            "default": "stdio",
                            "options": ["stdio", "sse"],
                        },
                        "LOG_LEVEL": {
                            "description": "Logging level",
                            "default": "INFO",
                            "options": ["DEBUG", "INFO", "WARNING", "ERROR"],
                        },
                        "DEBUG": {
                            "description": "Enable debug mode",
                            "default": "False",
                            "type": "boolean",
                        },
                        "FAISS_DATA_SECURE": {
                            "description": "Require authentication for FAISS data endpoint",
                            "default": "True",
                            "type": "boolean",
                        },
                    },
                },
                "deployment_modes": {
                    "claude_desktop": {
                        "mode": "stdio",
                        "description": "Direct integration with Claude Desktop",
                        "configuration": {
                            "file": "claude_desktop_config.json",
                            "location": "~/.claude/claude_desktop_config.json",
                            "example": {
                                "mcpServers": {
                                    "hubspot": {
                                        "command": "uv",
                                        "args": ["run", "hubspot-mcp-server"],
                                        "env": {"HUBSPOT_API_KEY": "your-api-key"},
                                    }
                                }
                            },
                        },
                    },
                    "web_server": {
                        "mode": "sse",
                        "description": "HTTP server for web clients",
                        "environment": {
                            "MODE": "sse",
                            "HOST": "localhost",
                            "PORT": "8080",
                            "MCP_AUTH_KEY": "your-secret-key",
                        },
                        "endpoints": [
                            {"path": "/sse", "description": "MCP SSE endpoint"},
                            {"path": "/health", "description": "Health check"},
                            {"path": "/ready", "description": "Readiness check"},
                            {
                                "path": "/faiss-data",
                                "description": "FAISS data inspection",
                            },
                        ],
                    },
                },
                "hubspot_setup": {
                    "steps": [
                        "1. Go to HubSpot Developer Account (developers.hubspot.com)",
                        "2. Create or select an app",
                        "3. Navigate to 'Auth' > 'Private Apps'",
                        "4. Create a new private app",
                        "5. Configure scopes: crm.objects.contacts.read, crm.objects.companies.read, crm.objects.deals.read, crm.objects.deals.write",
                        "6. Generate access token",
                        "7. Copy token to HUBSPOT_API_KEY environment variable",
                    ],
                    "required_scopes": [
                        "crm.objects.contacts.read",
                        "crm.objects.companies.read",
                        "crm.objects.deals.read",
                        "crm.objects.deals.write",
                        "crm.objects.engagements.read",
                        "crm.schemas.contacts.read",
                        "crm.schemas.companies.read",
                        "crm.schemas.deals.read",
                    ],
                },
                "performance_tuning": {
                    "caching": {
                        "enabled": True,
                        "ttl_seconds": 3600,
                        "description": "Response caching to reduce API calls",
                    },
                    "embeddings": {
                        "enabled": True,
                        "index_type": "flat",
                        "batch_size": 1000,
                        "description": "AI-powered semantic search",
                    },
                    "bulk_loading": {
                        "max_entities": 10000,
                        "page_size": 100,
                        "description": "Bulk data loading for large datasets",
                    },
                },
            }
        }

        return json.dumps(config, indent=2)

    @staticmethod
    def _generate_best_practices() -> str:
        """Generate best practices guide."""
        guide = """# HubSpot MCP Best Practices

## 🚀 Performance Optimization

### 1. Caching Strategy
- **Always enable caching** for production environments
- Use `manage_hubspot_cache` to monitor cache performance
- Clear cache after bulk data updates: `manage_hubspot_cache` with `{"action": "clear"}`
- Cache TTL is 1 hour - adjust based on data freshness needs

### 2. Bulk Operations
- Use `load_hubspot_entities_to_cache` for initial data loading
- Load in batches: set `max_entities` to 5000-10000 for optimal performance
- Enable embeddings during bulk load: `{"build_embeddings": true}`
- Monitor progress with cache statistics

### 3. AI Search Optimization
- Build embeddings index: `manage_hubspot_embeddings` with `{"action": "build"}`
- Use semantic search for natural language queries
- Use hybrid search mode for best results: `{"search_mode": "hybrid"}`
- Limit results appropriately: 10-50 for interactive use

## 🔍 Search Best Practices

### 1. Effective Search Patterns
```json
// Good: Specific filters
{"filters": {"email": "@company.com", "lifecyclestage": "customer"}}

// Better: Combined with limit
{"filters": {"industry": "TECHNOLOGY"}, "limit": 100}

// Best: Targeted semantic search
{"query": "software engineers in San Francisco", "limit": 20}
```

### 2. Filter Operators
- Use `CONTAINS_TOKEN` for partial text matches
- Use `EQ` for exact matches (enumerations, IDs)
- Use `GT`/`LT` for numerical comparisons
- Combine multiple filters for precision

## 📊 Monitoring & Maintenance

### 1. Cache Management
```json
// Check cache statistics
{"name": "manage_hubspot_cache", "arguments": {"action": "info"}}

// Clear cache when needed
{"name": "manage_hubspot_cache", "arguments": {"action": "clear"}}
```

### 2. AI Index Management
```json
// Check embedding status
{"name": "manage_hubspot_embeddings", "arguments": {"action": "info"}}

// Rebuild index periodically
{"name": "manage_hubspot_embeddings", "arguments": {"action": "build"}}
```

## 🔒 Security Best Practices

### 1. API Key Management
- Use environment variables: `HUBSPOT_API_KEY`
- Never hardcode API keys in configuration files
- Rotate API keys regularly
- Use least-privilege principle for HubSpot scopes

### 2. Authentication
- Enable authentication for production SSE mode: `MCP_AUTH_KEY`
- Use HTTPS in production deployments
- Implement proper access controls

## ⚡ Development Workflow

### 1. Local Development
1. Set up environment variables
2. Test connection: `list_hubspot_contacts` with limit 1
3. Verify permissions with property tools
4. Build cache for testing: `load_hubspot_entities_to_cache`

### 2. Production Deployment
1. Configure all required environment variables
2. Set up monitoring and logging
3. Enable caching and performance optimizations
4. Test all tools in production environment
5. Set up regular cache refresh schedules

Following these best practices ensures optimal performance, security, and reliability of your HubSpot MCP integration.
"""
        return guide

    @staticmethod
    def _generate_troubleshooting() -> str:
        """Generate troubleshooting guide."""
        guide = """# HubSpot MCP Troubleshooting Guide

## 🔧 Common Issues & Solutions

### 1. Authentication Errors

#### Error: "Invalid API key" or "Unauthorized"
**Symptoms:**
- Tools return authentication errors
- 401 Unauthorized responses

**Solutions:**
1. Verify `HUBSPOT_API_KEY` environment variable is set correctly
2. Check API key format: `pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
3. Verify HubSpot private app is active and not revoked
4. Test with simple tool: `list_hubspot_contacts` with limit 1

#### Error: "Insufficient permissions" or "Forbidden"
**Symptoms:**
- Some tools work, others return 403 errors
- Missing data in responses

**Solutions:**
1. Check HubSpot app scopes include:
   - `crm.objects.contacts.read`
   - `crm.objects.companies.read`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`
   - `crm.objects.engagements.read`
   - All relevant `crm.schemas.*.read` scopes

### 2. Performance Issues

#### Error: Slow response times (>10 seconds)
**Symptoms:**
- Tools take very long to respond
- Timeouts in Claude Desktop

**Solutions:**
1. **Enable caching:**
   ```json
   {"name": "manage_hubspot_cache", "arguments": {"action": "info"}}
   ```

2. **Use bulk loading:**
   ```json
   {
     "name": "load_hubspot_entities_to_cache",
     "arguments": {"entity_type": "contacts", "max_entities": 5000}
   }
   ```

3. **Limit result sizes:**
   - Use `limit` parameter (default 100, max 1000)
   - Start with smaller limits (10-50) for testing

### 3. Search & Filtering Issues

#### Error: "No results found" with valid data
**Symptoms:**
- Search returns empty results
- Know data exists in HubSpot

**Solutions:**
1. **Check filter syntax:**
   ```json
   // Correct
   {"filters": {"email": "@company.com"}}

   // Incorrect
   {"filters": {"email": {"contains": "@company.com"}}}
   ```

2. **Use correct field names:**
   - Contacts: `firstname`, `lastname`, `email`
   - Companies: `name`, `domain`, `industry`
   - Deals: `dealname`, `amount`, `dealstage`

### 4. Deal Management Issues

#### Error: "Deal creation failed"
**Symptoms:**
- `create_deal` returns validation errors
- Required field missing errors

**Solutions:**
1. **Check required fields:**
   ```json
   {
     "name": "create_deal",
     "arguments": {
       "dealname": "Required - Deal Name",
       "amount": "1000",
       "pipeline": "default",
       "dealstage": "appointment"
     }
   }
   ```

2. **Get valid pipeline/stage values:**
   ```json
   {"name": "get_hubspot_deal_properties", "arguments": {}}
   ```

## 🔍 Diagnostic Tools

### Check System Status
```json
// Cache status
{"name": "manage_hubspot_cache", "arguments": {"action": "info"}}

// AI index status
{"name": "manage_hubspot_embeddings", "arguments": {"action": "info"}}
```

### Test Basic Connectivity
```json
// Test API connection
{"name": "list_hubspot_contacts", "arguments": {"limit": 1}}

// Test permissions
{"name": "get_hubspot_contact_properties", "arguments": {}}
```

Remember: Most issues are related to authentication, permissions, or data formatting. Start with basic connectivity tests and work up to complex operations.
"""
        return guide

    @staticmethod
    def _generate_api_reference() -> str:
        """Generate condensed API reference."""
        reference = """# HubSpot API Quick Reference

## 🔗 API Endpoints Used by MCP Tools

### Base URL
```
https://api.hubapi.com
```

### Authentication
```
Authorization: Bearer {HUBSPOT_API_KEY}
```

## 📋 Entity Endpoints

### Contacts
**List Contacts:**
```
GET /crm/v3/objects/contacts
```
**MCP Tools:** `list_hubspot_contacts`, `search_hubspot_contacts`

**Parameters:**
- `limit`: 1-1000 (default: 100)
- `after`: Pagination cursor
- `properties`: Comma-separated field list

**Search Contacts:**
```
POST /crm/v3/objects/contacts/search
```
**Body:**
```json
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "email",
      "operator": "CONTAINS_TOKEN",
      "value": "@company.com"
    }]
  }],
  "properties": ["firstname", "lastname", "email"],
  "limit": 100
}
```

### Companies
**List Companies:**
```
GET /crm/v3/objects/companies
```
**MCP Tools:** `list_hubspot_companies`, `search_hubspot_companies`

### Deals
**List Deals:**
```
GET /crm/v3/objects/deals
```
**MCP Tools:** `list_hubspot_deals`, `search_hubspot_deals`

**Create Deal:**
```
POST /crm/v3/objects/deals
```
**MCP Tool:** `create_deal`

**Update Deal:**
```
PATCH /crm/v3/objects/deals/{dealId}
```
**MCP Tool:** `update_deal`

## 📊 Standard Properties

### Contacts
```json
{
  "firstname": "string",
  "lastname": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "jobtitle": "string",
  "lifecyclestage": "enum",
  "hubspot_owner_id": "string"
}
```

### Companies
```json
{
  "name": "string",
  "domain": "string",
  "industry": "enum",
  "city": "string",
  "state": "string",
  "country": "string",
  "phone": "string",
  "numberofemployees": "number"
}
```

### Deals
```json
{
  "dealname": "string",
  "amount": "number",
  "dealstage": "enum",
  "pipeline": "enum",
  "closedate": "date",
  "hubspot_owner_id": "string"
}
```

## 🎯 Filter Operators

### Text Fields
- `CONTAINS_TOKEN`: Partial match
- `EQ`: Exact match
- `NEQ`: Not equal

### Numeric Fields
- `GT`: Greater than
- `LT`: Less than
- `GTE`: Greater than or equal
- `LTE`: Less than or equal

## 🚨 Error Codes

### Authentication Errors
- `401 Unauthorized`: Invalid API key
- `403 Forbidden`: Insufficient permissions

### Request Errors
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

### Rate Limiting
- `429 Too Many Requests`: Rate limit exceeded

## 🔐 Required Scopes

### Read Operations
- `crm.objects.contacts.read`
- `crm.objects.companies.read`
- `crm.objects.deals.read`
- `crm.objects.engagements.read`

### Write Operations
- `crm.objects.deals.write`

### Schema Access
- `crm.schemas.contacts.read`
- `crm.schemas.companies.read`
- `crm.schemas.deals.read`

## 🔄 MCP Tool → API Mapping

All MCP tools use identical parameters to HubSpot API:

**MCP Tool Call:**
```json
{
  "name": "search_hubspot_contacts",
  "arguments": {
    "filters": {"email": "@company.com"},
    "limit": 50
  }
}
```

**Equivalent API Call:**
```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "filterGroups": [{
      "filters": [{"propertyName": "email", "operator": "CONTAINS_TOKEN", "value": "@company.com"}]
    }],
    "limit": 50
  }'
```

This ensures perfect compatibility between MCP tools and direct HubSpot API usage.
"""
        return reference
