"""HubSpot MCP Server prompts for client guidance."""

from typing import Any, Dict, List

import mcp.types as types


class HubSpotPrompts:
    """Collection of prompts to guide MCP clients on using HubSpot tools effectively."""

    @staticmethod
    def get_prompt_definitions() -> List[types.Prompt]:
        """Get all available prompt definitions.

        Returns:
            List[types.Prompt]: List of all prompt definitions
        """
        return [
            HubSpotPrompts._get_hubspot_basics_prompt(),
            HubSpotPrompts._get_hubspot_search_guide_prompt(),
            HubSpotPrompts._get_hubspot_ai_search_prompt(),
            HubSpotPrompts._get_hubspot_performance_prompt(),
            HubSpotPrompts._get_hubspot_api_compatibility_prompt(),
        ]

    @staticmethod
    def _get_hubspot_basics_prompt() -> types.Prompt:
        """Prompt explaining HubSpot MCP server basics."""
        return types.Prompt(
            name="hubspot_basics_guide",
            description="Comprehensive guide for getting started with the HubSpot MCP server",
            arguments=[
                types.PromptArgument(
                    name="entity_type",
                    description="Focus on specific entity type (contacts, companies, deals, engagements)",
                    required=False,
                )
            ],
        )

    @staticmethod
    def _get_hubspot_search_guide_prompt() -> types.Prompt:
        """Prompt explaining advanced search capabilities."""
        return types.Prompt(
            name="hubspot_search_guide",
            description="Advanced guide for searching and filtering HubSpot entities with API compatibility",
            arguments=[
                types.PromptArgument(
                    name="search_type",
                    description="Type of search: 'basic', 'advanced', or 'api_params'",
                    required=False,
                ),
                types.PromptArgument(
                    name="entity_type",
                    description="Entity type to focus on (contacts, companies, deals)",
                    required=False,
                ),
            ],
        )

    @staticmethod
    def _get_hubspot_ai_search_prompt() -> types.Prompt:
        """Prompt explaining AI-powered semantic search."""
        return types.Prompt(
            name="hubspot_ai_search_guide",
            description="Guide for using AI-powered semantic search and embeddings with HubSpot data",
            arguments=[
                types.PromptArgument(
                    name="use_case",
                    description="Specific use case: 'setup', 'search', 'troubleshooting'",
                    required=False,
                ),
            ],
        )

    @staticmethod
    def _get_hubspot_performance_prompt() -> types.Prompt:
        """Prompt explaining performance optimization."""
        return types.Prompt(
            name="hubspot_performance_guide",
            description="Guide for optimizing performance with caching and bulk operations",
            arguments=[
                types.PromptArgument(
                    name="optimization_focus",
                    description="Focus area: 'caching', 'bulk_loading', 'embeddings'",
                    required=False,
                ),
            ],
        )

    @staticmethod
    def _get_hubspot_api_compatibility_prompt() -> types.Prompt:
        """Prompt explaining HubSpot API compatibility and parameters."""
        return types.Prompt(
            name="hubspot_api_compatibility",
            description="Comprehensive guide on HubSpot API compatibility and parameter usage",
            arguments=[
                types.PromptArgument(
                    name="api_endpoint",
                    description="Specific HubSpot API endpoint to focus on",
                    required=False,
                ),
                types.PromptArgument(
                    name="parameter_type",
                    description="Type of parameters: 'filters', 'properties', 'pagination'",
                    required=False,
                ),
            ],
        )

    @staticmethod
    def generate_prompt_content(prompt_name: str, arguments: Dict[str, Any]) -> str:
        """Generate the actual prompt content based on name and arguments.

        Args:
            prompt_name: Name of the prompt to generate
            arguments: Arguments provided by the client

        Returns:
            str: Generated prompt content
        """
        if prompt_name == "hubspot_basics_guide":
            return HubSpotPrompts._generate_basics_content(arguments)
        elif prompt_name == "hubspot_search_guide":
            return HubSpotPrompts._generate_search_guide_content(arguments)
        elif prompt_name == "hubspot_ai_search_guide":
            return HubSpotPrompts._generate_ai_search_content(arguments)
        elif prompt_name == "hubspot_performance_guide":
            return HubSpotPrompts._generate_performance_content(arguments)
        elif prompt_name == "hubspot_api_compatibility":
            return HubSpotPrompts._generate_api_compatibility_content(arguments)
        else:
            return f"Unknown prompt: {prompt_name}"

    @staticmethod
    def _generate_basics_content(arguments: Dict[str, Any]) -> str:
        """Generate content for the basics guide prompt."""
        entity_type = arguments.get("entity_type", "")

        base_content = """# HubSpot MCP Server - Getting Started Guide

## 🚀 Introduction

Welcome to the HubSpot MCP Server! This server provides 18 tools organized into 6 categories:

### 📋 Entity Listing (4 tools)
- `list_hubspot_contacts` - List contacts with pagination
- `list_hubspot_companies` - List companies with pagination
- `list_hubspot_deals` - List deals with pagination
- `list_hubspot_engagements` - List engagements with pagination

### 🔧 Properties (3 tools)
- `get_hubspot_contact_properties` - Get contact field definitions
- `get_hubspot_company_properties` - Get company field definitions
- `get_hubspot_deal_properties` - Get deal field definitions

### 🔍 Search & Filtering (3 tools)
- `search_hubspot_contacts` - Advanced contact search
- `search_hubspot_companies` - Advanced company search
- `search_hubspot_deals` - Advanced deal search

### 💼 Deal Management (3 tools)
- `get_deal_by_name` - Find deal by exact name
- `create_deal` - Create new deals
- `update_deal` - Modify existing deals

### 🤖 AI-Powered Search (3 tools)
- `semantic_search_hubspot` - Natural language search
- `manage_hubspot_embeddings` - Build AI search indexes
- `browse_hubspot_indexed_data` - Explore indexed content

### ⚡ Cache & Performance (2 tools)
- `load_hubspot_entities_to_cache` - Bulk load entities
- `manage_hubspot_cache` - Cache management

## 🎯 Quick Start Workflow

1. **Start with properties**: Use `get_hubspot_*_properties` to understand available fields
2. **List entities**: Use `list_hubspot_*` for basic browsing
3. **Search precisely**: Use `search_hubspot_*` for filtered results
4. **Optimize performance**: Use bulk loading and caching for large datasets
5. **Enable AI search**: Use embedding tools for natural language queries

## ⚠️ Important: API Compatibility

**CRITICAL**: All `get_*` and `search_*` tools use the same parameters as the HubSpot REST API.
📚 **Always refer to the official HubSpot API documentation**: https://developers.hubspot.com/docs/api/overview

## 📖 Best Practices

1. **Authentication**: Ensure your `HUBSPOT_API_KEY` environment variable is set
2. **Rate Limits**: Use pagination and caching to respect API limits
3. **Performance**: Use bulk loading for initial data import
4. **Search Strategy**: Start with basic listing, then use search tools for precision
"""

        if entity_type:
            entity_specific = f"""

## 🎯 Focused Guide: {entity_type.title()}

### Available Tools for {entity_type.title()}:
- `list_hubspot_{entity_type}` - Basic listing with pagination
- `get_hubspot_{entity_type.rstrip('s')}_properties` - Field definitions
- `search_hubspot_{entity_type}` - Advanced search (if available)

### Quick Example:
```
1. Get properties: get_hubspot_{entity_type.rstrip('s')}_properties
2. List entities: list_hubspot_{entity_type} with limit=10
3. Search: search_hubspot_{entity_type} with specific filters
```

### HubSpot API Reference:
- API Docs: https://developers.hubspot.com/docs/api/{entity_type}
- Search API: https://developers.hubspot.com/docs/api/crm/search
"""
            base_content += entity_specific

        return base_content

    @staticmethod
    def _generate_search_guide_content(arguments: Dict[str, Any]) -> str:
        """Generate content for the search guide prompt."""
        search_type = arguments.get("search_type", "basic")
        entity_type = arguments.get("entity_type", "")

        content = """# HubSpot Search & Filtering Guide

## ⚠️ CRITICAL: HubSpot API Compatibility

**ALL search tools use identical parameters to the HubSpot REST API.**

🔗 **Always reference the official HubSpot documentation**:
- Main Search API: https://developers.hubspot.com/docs/api/crm/search
- Contact Search: https://developers.hubspot.com/docs/api/crm/contacts
- Company Search: https://developers.hubspot.com/docs/api/crm/companies
- Deal Search: https://developers.hubspot.com/docs/api/crm/deals

## 🔍 Search Tool Types

### Basic Listing Tools
- `list_hubspot_contacts` - Pagination only
- `list_hubspot_companies` - Pagination only
- `list_hubspot_deals` - Pagination only
- `list_hubspot_engagements` - Pagination only

### Advanced Search Tools
- `search_hubspot_contacts` - Filters + pagination
- `search_hubspot_companies` - Filters + pagination
- `search_hubspot_deals` - Filters + pagination

## 📋 Common Filter Patterns

### Contacts Filters
```json
{
  "filters": {
    "email": "example.com",           // Contains match
    "firstname": "John",              // Contains match
    "lastname": "Smith",              // Contains match
    "company": "TechCorp"             // Contains match
  }
}
```

### Companies Filters
```json
{
  "filters": {
    "name": "Technology",             // Contains match
    "domain": "techcorp.com",         // Contains match
    "industry": "TECHNOLOGY",         // Exact match
    "country": "France"               // Contains match
  }
}
```

### Deals Filters
```json
{
  "filters": {
    "dealname": "Enterprise",         // Contains match
    "dealstage": "presentation",      // Exact match
    "pipeline": "default",            // Exact match
    "owner_id": "12345"              // Exact match
  }
}
```
"""

        if search_type == "api_params":
            content += """

## 🔧 Advanced API Parameters

### Exact HubSpot API Mapping
Our tools map directly to HubSpot's Search API endpoints:

#### POST /crm/v3/objects/{objectType}/search
- `filters` → `filterGroups[0].filters`
- `limit` → `limit` (max 100)
- `after` → `after` (pagination cursor)

#### Example HubSpot API Call:
```json
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "email",
      "operator": "CONTAINS_TOKEN",
      "value": "@techcorp.com"
    }]
  }],
  "limit": 50
}
```

#### Our MCP Tool Equivalent:
```json
{
  "name": "search_hubspot_contacts",
  "arguments": {
    "filters": {
      "email": "@techcorp.com"
    },
    "limit": 50
  }
}
```

### 📚 Parameter Documentation
For complete parameter reference, see:
- https://developers.hubspot.com/docs/api/crm/search#filter-search-results
- https://knowledge.hubspot.com/reports/operators-for-filtering-data
"""

        if entity_type:
            content += f"""

## 🎯 {entity_type.title()}-Specific Search

### HubSpot API Reference:
- https://developers.hubspot.com/docs/api/crm/{entity_type}
- https://developers.hubspot.com/docs/api/crm/{entity_type}#filter-{entity_type}

### Available Filters:
Check the HubSpot documentation for the complete list of filterable properties for {entity_type}.

### Tool Usage:
```json
{{
  "name": "search_hubspot_{entity_type}",
  "arguments": {{
    "filters": {{
      // Add filters based on HubSpot API docs
    }},
    "limit": 100
  }}
}}
```
"""

        return content

    @staticmethod
    def _generate_ai_search_content(arguments: Dict[str, Any]) -> str:
        """Generate content for the AI search guide prompt."""
        use_case = arguments.get("use_case", "setup")

        base_content = """# HubSpot AI-Powered Search Guide

## 🤖 Overview

The HubSpot MCP server includes advanced AI capabilities using FAISS vector search for semantic understanding of your CRM data.

## 🛠️ AI Tools Available

### 1. `semantic_search_hubspot`
Natural language search across all entities
- Query: "software engineers in Paris"
- Finds: Contacts with titles like "Developer", "Programmer", etc.

### 2. `manage_hubspot_embeddings`
Build and manage AI search indexes
- Actions: info, build, rebuild, clear
- Supports: contacts, companies, deals, engagements

### 3. `browse_hubspot_indexed_data`
Explore what data is indexed for AI search
- Actions: stats, list, search
- Helpful for debugging and validation

## 🚀 Quick Setup Workflow

1. **Load data**: `load_hubspot_entities_to_cache` with `build_embeddings: true`
2. **Verify index**: `manage_hubspot_embeddings` with `action: "info"`
3. **Test search**: `semantic_search_hubspot` with a simple query
4. **Browse data**: `browse_hubspot_indexed_data` with `action: "stats"`
"""

        if use_case == "setup":
            base_content += """

## 🔧 Initial Setup Guide

### Step 1: Bulk Load Data with Embeddings
```json
{
  "name": "load_hubspot_entities_to_cache",
  "arguments": {
    "entity_type": "contacts",
    "build_embeddings": true,
    "max_entities": 5000
  }
}
```

### Step 2: Verify Embedding Index
```json
{
  "name": "manage_hubspot_embeddings",
  "arguments": {
    "action": "info"
  }
}
```

### Step 3: Test Basic Search
```json
{
  "name": "semantic_search_hubspot",
  "arguments": {
    "query": "sales managers",
    "limit": 5
  }
}
```

### Expected Results
- Entities loaded and indexed
- FAISS index status: "ready"
- Search returns relevant results
"""

        elif use_case == "search":
            base_content += """

## 🔍 Advanced Search Techniques

### Natural Language Queries
- "Find software engineers" → Matches "Developer", "Programmer"
- "Technology companies in France" → Contextual location + industry
- "Enterprise clients" → Large companies without exact keywords

### Search Modes
- `semantic`: Pure AI similarity search
- `hybrid`: Combines AI + API results
- `auto`: Automatically chooses best mode

### Fine-tuning Results
```json
{
  "name": "semantic_search_hubspot",
  "arguments": {
    "query": "marketing directors in technology companies",
    "entity_types": ["contacts", "companies"],
    "limit": 10,
    "search_mode": "hybrid",
    "semantic_weight": 0.8
  }
}
```

### Performance Tips
- Use specific entity types to narrow scope
- Start with small limits (5-10) for testing
- Use hybrid mode for best of both worlds
"""

        elif use_case == "troubleshooting":
            base_content += """

## 🔧 Troubleshooting AI Search

### Common Issues

#### 1. "No embedding manager available"
**Solution**: Check if embeddings are enabled and initialized
```json
{
  "name": "manage_hubspot_embeddings",
  "arguments": {"action": "info"}
}
```

#### 2. "Index not ready"
**Solution**: Build the embedding index
```json
{
  "name": "manage_hubspot_embeddings",
  "arguments": {
    "action": "build",
    "entity_types": ["contacts", "companies"],
    "index_type": "flat"
  }
}
```

#### 3. Poor search results
**Solutions**:
- Check indexed data: `browse_hubspot_indexed_data`
- Try hybrid mode instead of pure semantic
- Verify data quality and completeness
- Rebuild embeddings with fresh data

#### 4. Performance issues
**Solutions**:
- Use smaller result limits
- Filter by specific entity types
- Use IVF index type for large datasets
- Monitor cache performance

### Diagnostic Tools
1. **Index stats**: `browse_hubspot_indexed_data` → action: "stats"
2. **Data inspection**: `browse_hubspot_indexed_data` → action: "list"
3. **Search testing**: `browse_hubspot_indexed_data` → action: "search"
"""

        return base_content

    @staticmethod
    def _generate_performance_content(arguments: Dict[str, Any]) -> str:
        """Generate content for the performance optimization prompt."""
        focus = arguments.get("optimization_focus", "")

        content = """# HubSpot Performance Optimization Guide

## ⚡ Performance Tools

### `load_hubspot_entities_to_cache`
Bulk load entities with complete property data
- Supports: contacts, companies, deals
- Features: Automatic embedding building
- Best for: Initial data import

### `manage_hubspot_cache`
Monitor and manage response cache
- Actions: info, clear
- TTL: 1 hour default
- Benefits: Faster response times

### `manage_hubspot_embeddings`
Build AI search indexes efficiently
- Index types: flat (small datasets), ivf (large datasets)
- Batch processing for large entities
- Memory optimization

## 🚀 Optimization Strategies

### 1. Cache Strategy
- Use caching for frequently accessed data
- Monitor hit rates with `manage_hubspot_cache`
- Clear cache when data updates significantly

### 2. Bulk Loading Strategy
- Load entities in batches of 5,000-10,000
- Enable embeddings during bulk loading
- Use appropriate entity type filtering

### 3. Search Optimization
- Use specific entity types vs. searching all
- Implement pagination for large result sets
- Choose appropriate search modes
"""

        if focus == "caching":
            content += """

## 🗃️ Cache Optimization Deep Dive

### Cache Configuration
- **TTL**: 3600 seconds (1 hour)
- **Driver**: In-memory with LRU eviction
- **Isolation**: Per API key for security

### Monitoring Cache Performance
```json
{
  "name": "manage_hubspot_cache",
  "arguments": {"action": "info"}
}
```

### Key Metrics to Monitor
- Hit rate > 70% is good
- Memory usage should be reasonable
- API calls avoided indicates cache effectiveness

### Cache Strategy Recommendations
1. **High-frequency data**: Contacts, companies (cache aggressively)
2. **Dynamic data**: Deals, recent engagements (shorter TTL)
3. **Properties**: Cache indefinitely (rarely change)
"""

        elif focus == "bulk_loading":
            content += """

## 📥 Bulk Loading Best Practices

### Optimal Loading Pattern
```json
{
  "name": "load_hubspot_entities_to_cache",
  "arguments": {
    "entity_type": "contacts",
    "build_embeddings": true,
    "max_entities": 10000
  }
}
```

### Loading Strategy by Entity Count
- **< 1,000 entities**: Load all at once
- **1,000 - 10,000**: Single bulk load
- **> 10,000**: Consider multiple smaller loads

### Performance Metrics
- **Contacts**: ~500-1000 entities/minute
- **Companies**: ~300-500 entities/minute
- **Deals**: ~200-400 entities/minute

### Post-Loading Optimization
1. Verify cache population
2. Test search performance
3. Monitor embedding index quality
"""

        elif focus == "embeddings":
            content += """

## 🧠 Embedding Performance Optimization

### Index Type Selection
- **Flat**: < 5,000 entities (exact search)
- **IVF**: > 5,000 entities (approximate but faster)

### Building Strategy
```json
{
  "name": "manage_hubspot_embeddings",
  "arguments": {
    "action": "build",
    "entity_types": ["contacts", "companies"],
    "index_type": "ivf"
  }
}
```

### Performance Considerations
- **Build time**: ~1-2 seconds per 100 entities
- **Memory usage**: ~1MB per 1,000 entities
- **Search speed**: Sub-second for most queries

### Optimization Tips
1. Build embeddings during low-traffic periods
2. Use incremental rebuilds for data updates
3. Monitor search relevance and rebuild if quality degrades
4. Use entity type filtering to reduce index size
"""

        return content

    @staticmethod
    def _generate_api_compatibility_content(arguments: Dict[str, Any]) -> str:
        """Generate content for the API compatibility guide."""
        api_endpoint = arguments.get("api_endpoint", "")
        parameter_type = arguments.get("parameter_type", "")

        content = """# HubSpot API Compatibility Guide

## ⚠️ CRITICAL INFORMATION

**The HubSpot MCP server tools are designed to be 100% compatible with the HubSpot REST API.**

This means:
- ✅ Same parameter names and formats
- ✅ Same filter operators and logic
- ✅ Same pagination cursors
- ✅ Same error responses

## 📚 Required Reading

**ALWAYS consult the official HubSpot API documentation before using search and filter tools:**

### Primary Documentation
- **Main API Overview**: https://developers.hubspot.com/docs/api/overview
- **Search API**: https://developers.hubspot.com/docs/api/crm/search
- **Authentication**: https://developers.hubspot.com/docs/api/private-apps

### Entity-Specific Documentation
- **Contacts**: https://developers.hubspot.com/docs/api/crm/contacts
- **Companies**: https://developers.hubspot.com/docs/api/crm/companies
- **Deals**: https://developers.hubspot.com/docs/api/crm/deals
- **Engagements**: https://developers.hubspot.com/docs/api/crm/engagements

## 🔄 Direct API Mapping

### List Tools → GET /crm/v3/objects/{object}
```
MCP Tool: list_hubspot_contacts
HubSpot API: GET /crm/v3/objects/contacts
Parameters: limit, after, properties
```

### Search Tools → POST /crm/v3/objects/{object}/search
```
MCP Tool: search_hubspot_contacts
HubSpot API: POST /crm/v3/objects/contacts/search
Parameters: filterGroups, limit, after, properties
```

### Properties Tools → GET /crm/v3/properties/{object}
```
MCP Tool: get_hubspot_contact_properties
HubSpot API: GET /crm/v3/properties/contacts
```

## 🎯 Parameter Compatibility Examples

### MCP Tool Call
```json
{
  "name": "search_hubspot_deals",
  "arguments": {
    "filters": {
      "dealname": "Enterprise",
      "dealstage": "presentation",
      "pipeline": "default"
    },
    "limit": 50
  }
}
```

### Equivalent HubSpot API Call
```bash
curl -X POST \\
  https://api.hubapi.com/crm/v3/objects/deals/search \\
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "filterGroups": [{
      "filters": [
        {
          "propertyName": "dealname",
          "operator": "CONTAINS_TOKEN",
          "value": "Enterprise"
        },
        {
          "propertyName": "dealstage",
          "operator": "EQ",
          "value": "presentation"
        },
        {
          "propertyName": "pipeline",
          "operator": "EQ",
          "value": "default"
        }
      ]
    }],
    "limit": 50
  }'
```

## 🔍 Filter Operators

The MCP tools automatically select appropriate operators based on the field type:

### String Fields (CONTAINS_TOKEN)
- Contact email, name fields
- Company name, domain
- Deal name

### Exact Match Fields (EQ)
- Deal stage, pipeline
- Contact/Company owner ID
- Enumeration properties

### Numeric Fields (EQ, GT, LT)
- Deal amount
- Company employee count
- Numeric custom properties

## 📖 Learning Path

1. **Start here**: Read HubSpot API basics
2. **Understand objects**: Learn about contacts, companies, deals
3. **Master search**: Study the search API thoroughly
4. **Practice filters**: Test different filter combinations
5. **Use MCP tools**: Apply your API knowledge to our tools

## 🚨 Important Notes

- **Rate limits**: HubSpot API limits apply (100 requests/10 seconds for most endpoints)
- **Authentication**: Ensure your API key has appropriate scopes
- **Property names**: Use exact property names from HubSpot (case-sensitive)
- **Data types**: Match the expected data types for each property
"""

        if api_endpoint:
            content += f"""

## 🎯 Focused Guide: {api_endpoint}

### Specific Documentation
- HubSpot Docs: https://developers.hubspot.com/docs/api/crm/{api_endpoint}
- Search endpoint: https://developers.hubspot.com/docs/api/crm/{api_endpoint}#search-{api_endpoint}

### MCP Tool Equivalent
- List: `list_hubspot_{api_endpoint}`
- Search: `search_hubspot_{api_endpoint}` (if available)
- Properties: `get_hubspot_{api_endpoint.rstrip('s')}_properties`

### Parameter Reference
Refer to the HubSpot documentation above for the complete list of:
- Available properties for filtering
- Search operators supported
- Required vs optional fields
- Data format requirements
"""

        if parameter_type == "filters":
            content += """

## 🔧 Filter Parameter Deep Dive

### Filter Structure in HubSpot API
```json
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "string",
      "operator": "ENUM_VALUE",
      "value": "string"
    }]
  }]
}
```

### MCP Tool Simplified Format
```json
{
  "filters": {
    "propertyName": "value"
  }
}
```

### Automatic Operator Selection
- **Text fields**: CONTAINS_TOKEN (partial match)
- **ID fields**: EQ (exact match)
- **Enum fields**: EQ (exact match)
- **Date fields**: EQ (exact match)

### Complex Filters
For advanced filtering beyond our simplified format, use the HubSpot API directly or request specific filter support.
"""

        elif parameter_type == "properties":
            content += """

## 🏷️ Properties Parameter Guide

### Default Properties
Each entity type has standard properties automatically included:
- **Contacts**: firstname, lastname, email, company, phone
- **Companies**: name, domain, industry, city, country
- **Deals**: dealname, amount, dealstage, pipeline, closedate

### Custom Properties
Use the properties tools to discover available custom properties:
```json
{
  "name": "get_hubspot_contact_properties",
  "arguments": {}
}
```

### Extra Properties in Tools
Some tools support additional properties via `extra_properties` parameter (check tool documentation).
"""

        elif parameter_type == "pagination":
            content += """

## 📄 Pagination Parameter Guide

### Standard Pagination
- **limit**: Maximum results per page (1-100, default 100)
- **after**: Cursor for next page (returned in previous response)

### Example Pagination Workflow
1. First call: `{"limit": 50}`
2. Response includes: `"paging": {"next": {"after": "cursor123"}}`
3. Next call: `{"limit": 50, "after": "cursor123"}`
4. Continue until no `next` cursor returned

### Best Practices
- Start with small limits (10-50) for testing
- Use appropriate page sizes for your use case
- Store cursors for resuming pagination
- Handle pagination errors gracefully
"""

        return content
