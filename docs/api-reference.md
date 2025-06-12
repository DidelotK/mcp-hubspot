# API Reference - MCP Tools

This MCP server exposes 5 tools to interact with the HubSpot API.

## list_hubspot_contacts

Retrieves the list of HubSpot contacts.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of contacts to retrieve | 100 |
| `filters` | object | No | Search filters | {} |

### Usage Example

```json
{
  "name": "list_hubspot_contacts",
  "arguments": {
    "limit": 10,
    "filters": {
      "search": "jean"
    }
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

Retrieves the list of HubSpot companies.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of companies to retrieve | 100 |
| `filters` | object | No | Search filters | {} |

### Usage Example

```json
{
  "name": "list_hubspot_companies",
  "arguments": {
    "limit": 5,
    "filters": {
      "search": "technology"
    }
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

Retrieves the list of HubSpot deals.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `limit` | integer | No | Maximum number of deals to retrieve | 100 |
| `filters` | object | No | Search filters | {} |

### Usage Example

```json
{
  "name": "list_hubspot_deals",
  "arguments": {
    "limit": 20,
    "filters": {
      "search": "premium"
    }
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

## 📁 demographic_information

**📅 Date of Birth**
  🏷️ Name: `date_of_birth`
  🔧 Type: date (date)
  📝 Description: The contact's date of birth

## 📁 company_information

**📋 Industry**
  🏷️ Name: `industry`
  🔧 Type: enumeration (select)
  📝 Description: The company's industry sector
  📋 Options: Technology, Finance, Healthcare, ... and 25 others
```

### Usefulness

This tool is particularly useful for:
- **Discovering available fields** in HubSpot
- **Understanding data types** (text, date, select, etc.)
- **Viewing available options** for selection fields
- **Planning integration** with other systems
- **Debugging issues** with data synchronization

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