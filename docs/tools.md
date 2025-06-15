# Tools Documentation

This MCP server exposes **18 tools** to interact with the HubSpot API, organized by functionality for comprehensive CRM integration.

## 📋 Entity Listing

Core tools for listing and browsing HubSpot entities with pagination support.

### list_hubspot_contacts

Retrieves the list of HubSpot contacts with pagination support.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of contacts to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

#### Usage Example

```json
{
  "name": "list_hubspot_contacts",
  "arguments": {
    "limit": 10,
    "after": "cursor123"
  }
}
```

#### Response

```text
📋 **HubSpot Contacts** (10 found)

**Jean Dupont**
  📧 Email: jean.dupont@example.com
  🏢 Company: Acme Corp
  📞 Phone: +33123456789
  🆔 ID: 12345
```

### list_hubspot_companies

Retrieves the list of HubSpot companies with pagination support.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of companies to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

#### Usage Example

```json
{
  "name": "list_hubspot_companies",
  "arguments": {
    "limit": 5,
    "after": "cursor456"
  }
}
```

#### Response

```text
🏢 **HubSpot Companies** (5 found)

**TechCorp Solutions**
  🌐 Domain: techcorp.com
  🏭 Industry: Technology
  👥 Employees: 150
  🆔 ID: 67890
```

### list_hubspot_deals

Retrieves the list of HubSpot deals with pagination support.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of deals to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

#### Usage Example

```json
{
  "name": "list_hubspot_deals",
  "arguments": {
    "limit": 20,
    "after": "cursor123"
  }
}
```

#### Response

```text
💰 **HubSpot Deals** (20 found)

**Premium Contract 2024**
  💰 Amount: €45,000.00
  📊 Stage: proposal
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 789012
```

### list_hubspot_engagements

Retrieves the list of HubSpot engagements (calls, emails, tasks, etc.) with pagination support.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of engagements to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

#### Usage Example

```json
{
  "name": "list_hubspot_engagements",
  "arguments": {
    "limit": 15,
    "after": "cursor789"
  }
}
```

#### Response

```text
📞 **HubSpot Engagements** (15 found)

**Follow-up call with ACME Corp**
  🔖 Type: CALL
  ️ Created: 2024-01-01T09:00:00Z
  🔄 Updated: 2024-01-01T10:00:00Z
  �� ID: 123456
```

## 🔧 Properties

Tools for retrieving field properties and schemas for each entity type.

### get_hubspot_contact_properties

Retrieves the list of available properties for HubSpot contacts with their types and descriptions.

#### Parameters

No parameters required.

#### Usage Example

```json
{
  "name": "get_hubspot_contact_properties",
  "arguments": {}
}
```

#### Response

```text
🔧 **HubSpot Contact Properties** (405 properties)

## 📁 contactinformation

**📧 Email Address**
  🏷️ Name: `email`
  🔧 Type: string (text)
  📝 Description: The contact's email address

**📝 First Name**
  🏷️ Name: `firstname`
  🔧 Type: string (text)
  📝 Description: The contact's first name

**📝 Last Name**
  🏷️ Name: `lastname`
  🔧 Type: string (text)
  📝 Description: The contact's last name

**📞 Phone Number**
  🏷️ Name: `phone`
  🔧 Type: string (text)
  📝 Description: The contact's primary phone number
```

### get_hubspot_company_properties

Retrieves the list of available properties for HubSpot companies with their types and descriptions.

#### Parameters

No parameters required.

#### Usage Example

```json
{
  "name": "get_hubspot_company_properties",
  "arguments": {}
}
```

#### Response

```text
🏢 **HubSpot Company Properties** (156 properties)

## 📁 companyinformation

**🏢 Company Name**
  🏷️ Name: `name`
  🔧 Type: string (text)
  📝 Description: The company name

**🌐 Website Domain**
  🏷️ Name: `domain`
  🔧 Type: string (text)
  📝 Description: The company website domain

**🏭 Industry**
  🏷️ Name: `industry`
  🔧 Type: enumeration (select)
  📝 Description: The company's industry sector
  📋 Options: Technology, Finance, Healthcare, ... and 25 others

**👥 Number of Employees**
  🏷️ Name: `numberofemployees`
  🔧 Type: number (number)
  📝 Description: Total number of employees
```

### get_hubspot_deal_properties

Retrieves the list of available properties for HubSpot deals with their types and descriptions.

#### Parameters

No parameters required.

#### Usage Example

```json
{
  "name": "get_hubspot_deal_properties",
  "arguments": {}
}
```

#### Response

```text
💰 **HubSpot Deal Properties** (89 properties)

## 📁 dealinformation

**🏷️ Deal Name**
  🏷️ Name: `dealname`
  🔧 Type: string (text)
  📝 Description: The name of the deal

**💰 Deal Amount**
  🏷️ Name: `amount`
  🔧 Type: number (number)
  📝 Description: The deal amount

**📊 Deal Stage**
  🏷️ Name: `dealstage`
  🔧 Type: enumeration (select)
  📝 Description: The current stage of the deal
  📋 Options: appointmentscheduled, qualifiedtobuy, presentationscheduled, ... and 5 others

**🔄 Pipeline**
  🏷️ Name: `pipeline`
  🔧 Type: enumeration (select)
  📝 Description: The sales pipeline
  📋 Options: default, enterprise, ... and 2 others

**📅 Close Date**
  🏷️ Name: `closedate`
  🔧 Type: date (date)
  📝 Description: Expected close date
```

## 🔍 Search & Filtering

Advanced search tools with filters for each entity type.

### search_hubspot_contacts

Search HubSpot contacts using the CRM Search API with advanced filtering.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of contacts to return (1-100) | 100 |
| `filters` | object | No | Search filters object | `{}` |

The `filters` object can include:

| Filter Key | Type | Description |
|------------|------|-------------|
| `email` | string | Partial match on email address (contains token) |
| `firstname` | string | Partial match on first name (contains token) |
| `lastname` | string | Partial match on last name (contains token) |
| `company` | string | Partial match on company name (contains token) |

#### Usage Example

```json
{
  "name": "search_hubspot_contacts",
  "arguments": {
    "limit": 10,
    "filters": {
      "company": "TechCorp",
      "email": "john"
    }
  }
}
```

### search_hubspot_companies

Search HubSpot companies using the CRM Search API with advanced filtering.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of companies to return (1-100) | 100 |
| `filters` | object | No | Search filters object | `{}` |

The `filters` object can include:

| Filter Key | Type | Description |
|------------|------|-------------|
| `name` | string | Partial match on company name (contains token) |
| `domain` | string | Partial match on website domain (contains token) |
| `industry` | string | Partial match on industry (contains token) |
| `country` | string | Partial match on country (contains token) |

#### Usage Example

```json
{
  "name": "search_hubspot_companies",
  "arguments": {
    "limit": 5,
    "filters": {
      "industry": "Technology",
      "country": "France"
    }
  }
}
```

### search_hubspot_deals

Search HubSpot deals using the CRM Search API with advanced filtering.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of deals to return (1-100) | 100 |
| `filters` | object | No | Search filters object | `{}` |

The `filters` object can include:

| Filter Key | Type | Description |
|------------|------|-------------|
| `dealname` | string | Partial match on deal name (contains token) |
| `owner_id` | string | Exact match on HubSpot owner ID |
| `dealstage` | string | Exact match on deal stage |
| `pipeline` | string | Exact match on pipeline ID |

#### Usage Example

```json
{
  "name": "search_hubspot_deals",
  "arguments": {
    "limit": 10,
    "filters": {
      "dealname": "renewal",
      "dealstage": "presentation"
    }
  }
}
```

#### Response

```text
💰 **HubSpot Deals** (1 found)

**Enterprise Renewal**
  💰 Amount: $250,000.00
  📊 Stage: presentation
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 9001
```

## 💼 Deal Management

Complete deal lifecycle management tools.

### get_deal_by_name

Retrieves a specific deal by its exact name.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deal_name` | string | **Yes** | Exact name of the deal to search for |

#### Usage Example

```json
{
    "name": "get_deal_by_name",
    "arguments": {
        "deal_name": "Premium Contract 2024"
    }
}
```

#### Response - Deal Found

```text
💰 **HubSpot Deal**

**Premium Contract 2024**
  💰 Amount: €45,000.00
  📊 Stage: proposal
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 789012
```

#### Response - Deal Not Found

```text
❌ **Deal Not Found**

No deal found with the name: "Non-existent Contract"
```

### create_deal

Creates a new deal in HubSpot.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dealname` | string | **Yes** | Name of the deal |
| `amount` | string | No | Deal amount |
| `dealstage` | string | No | Deal stage |
| `pipeline` | string | No | Deal pipeline |
| `closedate` | string | No | Expected close date (YYYY-MM-DD) |
| `hubspot_owner_id` | string | No | Deal owner ID |
| `description` | string | No | Deal description |

#### Usage Example

```json
{
  "name": "create_deal",
  "arguments": {
    "dealname": "New Enterprise Contract",
    "amount": "75000",
    "dealstage": "appointmentscheduled",
    "pipeline": "default",
    "closedate": "2024-12-31",
    "description": "Large enterprise deal for Q4"
  }
}
```

#### Response

```text
✅ **Deal Created Successfully**

**New Enterprise Contract**
  💰 Amount: $75,000.00
  📊 Stage: appointmentscheduled
  🔄 Pipeline: default
  📅 Close Date: 2024-12-31
  📝 Description: Large enterprise deal for Q4
  🆔 ID: 987654
```

### update_deal

Updates an existing deal in HubSpot.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deal_id` | string | **Yes** | ID of the deal to update |
| `properties` | object | **Yes** | Properties to update |

The `properties` object can contain any of the following fields:

| Property | Type | Description |
|----------|------|-------------|
| `dealname` | string | Name of the deal |
| `amount` | string | Deal amount |
| `dealstage` | string | Deal stage |
| `pipeline` | string | Deal pipeline |
| `closedate` | string | Expected close date (YYYY-MM-DD) |
| `hubspot_owner_id` | string | Deal owner ID |
| `description` | string | Deal description |

#### Usage Example

```json
{
  "name": "update_deal",
  "arguments": {
    "deal_id": "12345",
    "properties": {
      "dealname": "Updated Enterprise Contract",
      "amount": "85000",
      "dealstage": "contractsent"
    }
  }
}
```

#### Response

```text
💰 **HubSpot Deal Updated**

**Updated Enterprise Contract**
  💰 Amount: $85,000.00
  📊 Stage: contractsent
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 12345
```

## 🤖 AI-Powered Search

Semantic search using natural language with FAISS vector database.

### semantic_search_hubspot

Perform AI-powered semantic search across HubSpot entities using natural language queries.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `query` | string | **Yes** | Natural language search query | - |
| `entity_types` | array | No | Limit search to specific entity types | All types |
| `limit` | integer | No | Maximum number of results to return (1-50) | 10 |
| `search_mode` | string | No | Search mode: "semantic", "hybrid", or "auto" | "auto" |
| `semantic_weight` | number | No | Weight for semantic vs API results (0.0-1.0) | 0.7 |

#### Usage Example

```json
{
  "name": "semantic_search_hubspot",
  "arguments": {
    "query": "software engineers in Paris",
    "entity_types": ["contacts", "companies"],
    "limit": 5,
    "search_mode": "semantic"
  }
}
```

#### Response

```text
🔍 **Semantic Search Results** for "software engineers in Paris"

**Found 5 results** (semantic mode)

**👤 Pierre Martin** (Contact)
  📧 pierre.martin@devstudio.fr
  🏢 DevStudio Paris
  📍 Paris, France
  🎯 Relevance: 0.92
  💡 Match: Senior software engineer with React expertise

**🏢 TechFlow Solutions** (Company)
  🌐 techflow.fr
  🏭 Software Development
  📍 Paris, France
  🎯 Relevance: 0.89
  💡 Match: Software engineering consultancy specializing in web development
```

### manage_hubspot_embeddings

Manage FAISS embeddings for AI-powered search capabilities.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `action` | string | No | Action: "info", "build", "rebuild", or "clear" | "info" |
| `entity_types` | array | No | Entity types for build operations | All types |
| `index_type` | string | No | FAISS index type: "flat" or "ivf" | "flat" |

#### Usage Example

```json
{
  "name": "manage_hubspot_embeddings",
  "arguments": {
    "action": "build",
    "entity_types": ["contacts", "companies", "deals"],
    "index_type": "ivf"
  }
}
```

#### Response

```text
🧠 **Embedding Management**

✅ **Build Complete**

📊 **Results:**
  • contacts: 650 entities indexed
  • companies: 350 entities indexed
  • deals: 200 entities indexed
  • Total: 1,200 entities

🔧 **Index Configuration:**
  • Type: ivf (optimized for large datasets)
  • Dimension: 768
  • Model: sentence-transformers/all-mpnet-base-v2

⚡ **Performance:**
  • Build time: 45.2 seconds
  • Memory usage: 256 MB
  • Ready for semantic search
```

### browse_hubspot_indexed_data

Browse and search HubSpot entities indexed in the FAISS vector database.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `action` | string | No | Action: "list", "stats", or "search" | "list" |
| `entity_type` | string | No | Filter by entity type | - |
| `offset` | integer | No | Number of entities to skip | 0 |
| `limit` | integer | No | Maximum entities to return (1-100) | 20 |
| `search_text` | string | No | Search within indexed content | - |
| `include_content` | boolean | No | Include full entity data | false |

#### Usage Example

```json
{
  "name": "browse_hubspot_indexed_data",
  "arguments": {
    "action": "search",
    "search_text": "technology",
    "entity_type": "companies",
    "limit": 3
  }
}
```

#### Response

```text
🔍 **Search Results for 'technology' in companies**

📊 **Search Info:**
  • Total matches: 15
  • Showing: 1-3 of 15

📄 **Matching Entities:**

**1. TechCorp Solutions**
  🏷️ Type: companies
  🆔 ID: company789
  🎯 Match: ...leading technology solutions provider...

**2. InnovateTech Inc**
  🏷️ Type: companies
  🆔 ID: company321
  🎯 Match: ...cutting-edge technology development...
```

## ⚡ Cache & Performance

Bulk loading, caching, and performance optimization tools.

### load_hubspot_entities_to_cache

Bulk load HubSpot entities (contacts, companies, or deals) into cache with complete property data for optimized FAISS searches.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `entity_type` | string | **Yes** | Type of entities: "contacts", "companies", or "deals" | - |
| `build_embeddings` | boolean | No | Build FAISS embeddings after loading | true |
| `max_entities` | integer | No | Maximum entities to load (0 = no limit) | 10000 |

#### Usage Example

```json
{
  "name": "load_hubspot_entities_to_cache",
  "arguments": {
    "entity_type": "deals",
    "build_embeddings": true,
    "max_entities": 5000
  }
}
```

#### Response

```text
🚀 **Bulk Loading Deals to Cache**

📋 **Step 1**: Retrieving all deals properties...
✅ Found 89 total properties, requesting 25 custom properties

📥 **Step 2**: Loading all deals with complete property data...
✅ Loaded 1,250 deals with complete property data

🧠 **Step 3**: Building FAISS embeddings for semantic search...
✅ Built embeddings for 1,250 deals
  📊 Index stats: 1,250 entities, 768 dimensions, flat index

🎉 **Cache Loading Complete**

📊 **Summary:**
  • Entity Type: Deals
  • Total Loaded: 1,250 entities
  • Properties: 25 custom properties + system properties
  • Embeddings: ✅ Built

💡 **What you can do now:**
  • Use semantic search across ALL deals with full property data
  • FAISS searches will be much faster with complete cached data
  • All 25 custom properties are searchable
```

### manage_hubspot_cache

Manage the HubSpot data cache for improved performance.

#### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `action` | string | No | Action: "info" or "clear" | "info" |

#### Usage Example

```json
{
  "name": "manage_hubspot_cache",
  "arguments": {
    "action": "info"
  }
}
```

#### Response

```text
🗃️ **HubSpot Cache Information**

📊 **Cache Statistics:**
  • Total entries: 1,247
  • Memory usage: ~125 MB
  • Hit rate: 78.5%
  • TTL: 3600 seconds (1 hour)

📋 **Cache Contents:**
  • list_hubspot_contacts: 423 entries
  • list_hubspot_companies: 284 entries
  • list_hubspot_deals: 312 entries
  • get_hubspot_contact_properties: 1 entry
  • search_hubspot_deals: 227 entries

⚡ **Performance Impact:**
  • Average response time: 45ms (vs 850ms uncached)
  • Bandwidth saved: ~2.3 MB per hour
  • API calls avoided: 1,247 in last hour

🔧 **Management:**
  • Use action="clear" to flush cache
  • Cache auto-expires after 1 hour
  • Bulk loading bypasses cache
```

## Error Handling

All tools handle errors consistently:

### Authentication Errors

```text
❌ HubSpot authentication error. Check your API key.
```

### Network Errors

```text
❌ Connection error to HubSpot API. Check your internet connection.
```

### Parameter Errors

```text
❌ Missing parameter: deal_name is required for get_deal_by_name
```

### Validation Errors

```text
❌ Invalid parameter: dealname cannot be empty
```

## Tool Integration

These tools work together to provide comprehensive HubSpot CRM integration:

### Workflow Examples

**1. Complete Deal Analysis:**

1. `list_hubspot_deals` - Get overview of all deals
2. `search_hubspot_deals` - Filter by specific criteria
3. `get_deal_by_name` - Get specific deal details
4. `semantic_search_hubspot` - Find similar deals using AI

**2. Performance Optimization:**

1. `load_hubspot_entities_to_cache` - Bulk load entities
2. `manage_hubspot_embeddings` - Build AI search indexes
3. `manage_hubspot_cache` - Monitor performance
4. `browse_hubspot_indexed_data` - Validate indexing

**3. Data Discovery:**

1. `get_hubspot_contact_properties` - Understand available fields
2. `list_hubspot_contacts` - Browse entity data
3. `semantic_search_hubspot` - Find entities using natural language
4. `browse_hubspot_indexed_data` - Explore indexed content

## Best Practices

### Performance Tips

- Use **bulk loading** tools for initial data import
- Enable **caching** for frequently accessed data
- Build **FAISS embeddings** for AI-powered search
- Use **pagination** for large datasets

### Search Strategy

- Use **list tools** for browsing and exploration
- Use **search tools** for precise filtering
- Use **semantic search** for natural language queries
- Use **browse indexed data** for content analysis

### Error Prevention

- Check **authentication** before starting workflows
- Validate **required parameters** before API calls
- Use **appropriate limits** to avoid timeouts
- Monitor **cache performance** for optimization

## Response Format

Every tool returns formatted Markdown output optimized for readability, with consistent emoji usage and structured information display. Complex tools also include raw JSON data in fenced code blocks for programmatic access.
