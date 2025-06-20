# MCP Tools

This MCP server exposes 11 tools to interact with the HubSpot API.

## list_hubspot_contacts

Retrieves the list of HubSpot contacts with pagination support.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of contacts to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

### Usage Example

```json
{
  "name": "list_hubspot_contacts",
  "arguments": {
    "limit": 10,
    "after": "cursor123"
  }
}
```

### Response

```
📋 **HubSpot Contacts** (10 found)

**Jean Dupont**
  📧 Email: jean.dupont@example.com
  🏢 Company: Acme Corp
  📞 Phone: +33123456789
  🆔 ID: 12345
```

## list_hubspot_companies

Retrieves the list of HubSpot companies with pagination support.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of companies to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

### Usage Example

```json
{
  "name": "list_hubspot_companies",
  "arguments": {
    "limit": 5,
    "after": "cursor456"
  }
}
```

### Response

```
🏢 **HubSpot Companies** (5 found)

**TechCorp Solutions**
  🌐 Domain: techcorp.com
  🏭 Industry: Technology
  👥 Employees: 150
  🆔 ID: 67890
```

## list_hubspot_deals

Retrieves the list of HubSpot deals with pagination support.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of deals to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

### Usage Example

```json
{
  "name": "list_hubspot_deals",
  "arguments": {
    "limit": 20,
    "after": "cursor123"
  }
}
```

### Response

```
💰 **HubSpot Deals** (20 found)

**Premium Contract 2024**
  💰 Amount: €45,000.00
  📊 Stage: proposal
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 789012
```

## search_hubspot_deals

Search HubSpot deals using the CRM Search API with advanced filtering.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of deals to return (1 – 100) | 100 |
| `filters` | object | No | Search filters object | `{}` |

The `filters` object can include:

| Filter Key | Type | Description |
|------------|------|-------------|
| `dealname` | string | Partial match on deal name (contains token) |
| `owner_id` | string | Exact match on HubSpot owner ID |
| `dealstage` | string | Exact match on deal stage |
| `pipeline` | string | Exact match on pipeline ID |

### Usage Example

```json
{
  "name": "search_hubspot_deals",
  "arguments": {
    "limit": 10,
    "filters": {
      "dealname": "renewal",
      "owner_id": "123"
    }
  }
}
```

### Response

```
💰 **HubSpot Deals** (1 found)

**Enterprise Renewal**
  💰 Amount: $250,000.00
  📊 Stage: contractsigned
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 9001
```

## create_deal

Creates a new deal in HubSpot.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dealname` | string | **Yes** | Name of the deal |
| `amount` | string | No | Deal amount |
| `dealstage` | string | No | Deal stage |
| `pipeline` | string | No | Deal pipeline |
| `closedate` | string | No | Expected close date (YYYY-MM-DD) |
| `hubspot_owner_id` | string | No | Deal owner ID |
| `description` | string | No | Deal description |

### Usage Example

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

### Response

```
✅ **Deal Created Successfully**

**New Enterprise Contract**
  💰 Amount: $75,000.00
  📊 Stage: appointmentscheduled
  🔄 Pipeline: default
  📅 Close Date: 2024-12-31
  📝 Description: Large enterprise deal for Q4
  🆔 ID: 987654
```

## get_deal_by_name

Retrieves a specific deal by its exact name.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deal_name` | string | **Yes** | Exact name of the deal to search for |

### Usage Example

```json
{
    "name": "get_deal_by_name",
    "arguments": {
        "deal_name": "Premium Contract 2024"
    }
}
```

### Response - Deal Found

```
💰 **HubSpot Deal**

**Premium Contract 2024**
  💰 Amount: €45,000.00
  📊 Stage: proposal
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 789012
```

### Response - Deal Not Found

```
❌ **Deal Not Found**

No deal found with the name: "Non-existent Contract"
```

## get_hubspot_contact_properties

Retrieves the list of available properties for HubSpot contacts with their types and descriptions.

### Parameters

No parameters required.

### Usage Example

```json
{
  "name": "get_hubspot_contact_properties",
  "arguments": {}
}
```

### Response

```
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

## get_hubspot_company_properties

Retrieves the list of available properties for HubSpot companies with their types and descriptions.

### Parameters

No parameters required.

### Usage Example

```json
{
  "name": "get_hubspot_company_properties",
  "arguments": {}
}
```

### Response

```
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

## get_hubspot_deal_properties

Retrieves the list of available properties for HubSpot deals with their types and descriptions.

### Parameters

No parameters required.

### Usage Example

```json
{
  "name": "get_hubspot_deal_properties",
  "arguments": {}
}
```

### Response

```
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

## update_deal

Updates an existing deal in HubSpot.

### Parameters

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

### Usage Example

```json
{
  "name": "update_deal",
  "arguments": {
    "deal_id": "12345",
    "properties": {
      "dealname": "Updated Enterprise Contract",
      "amount": "85000",
      "dealstage": "contractsent",
      "pipeline": "enterprise",
      "closedate": "2024-12-31",
      "description": "Updated enterprise deal for Q4"
    }
  }
}
```

### Response

```
💰 **HubSpot Deal Updated**

**Updated Enterprise Contract**
  💰 Amount: $85,000.00
  📊 Stage: contractsent
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  📝 Description: Updated enterprise deal for Q4
  🆔 ID: 12345
```

## Error Handling

All tools handle errors consistently:

### Authentication Errors

```
❌ HubSpot authentication error. Check your API key.
```

### Network Errors

```
❌ Connection error to HubSpot API. Check your internet connection.
```

### Parameter Errors

```
❌ Missing parameter: deal_name is required for get_deal_by_name
```

### Validation Errors

```
❌ Invalid parameter: dealname cannot be empty
```

## Search Filters

Filters support the following properties:

### For Contacts

- `search`: Text search in name, email, company
- `email`: Filter by exact email
- `company`: Filter by company name

### For Companies

- `search`: Text search in name, domain, industry
- `domain`: Filter by exact domain
- `industry`: Filter by industry sector

### For Deals

- `search`: Text search in name, stage, pipeline
- `stage`: Filter by sales stage
- `pipeline`: Filter by sales pipeline
- `amount_gte`: Minimum amount
- `amount_lte`: Maximum amount

## Usefulness

These tools are particularly useful for:

- **Discovering available fields** in HubSpot
- **Understanding data types** (text, date, select, etc.)
- **Viewing available options** for selection fields
- **Planning integration** with other systems
- **Creating and managing deals** programmatically
- **Debugging issues** with data synchronization
- **Building custom workflows** with HubSpot data

## list_hubspot_engagements

Retrieves the list of HubSpot engagements (calls, emails, tasks, etc.) with pagination support.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of engagements to retrieve (max 100) | 100 |
| `after` | string | No | Pagination cursor to get the next set of results | - |

### Usage Example

```json
{
  "name": "list_hubspot_engagements",
  "arguments": {
    "limit": 15,
    "after": "cursor789"
  }
}
```

### Response

```
📞 **HubSpot Engagements** (15 found)

**Follow-up call with ACME Corp**
  🔖 Type: CALL
  ️ Created: 2024-01-01T09:00:00Z
  🔄 Updated: 2024-01-01T10:00:00Z
  🆔 ID: 123456
```

## Response format

Every tool returns **two complementary payloads**:

1. **Human-friendly Markdown** – formatted summary like the examples below.
2. **Raw JSON** – full data from HubSpot, embedded in a fenced `json` block directly after the Markdown.

Example:

```text
💰 **HubSpot Deals** (1 found)

**Premium Contract 2024**
  💰 Amount: €45,000.00
  📊 Stage: proposal
  🆔 ID: 789012

```json
[
  {
    "id": "789012",
    "properties": {
      "dealname": "Premium Contract 2024",
      "amount": "45000",
      "dealstage": "proposal",
      ...
    }
  }
]
```

This dual output lets you scan results quickly while still having the complete record for programmatic use.
