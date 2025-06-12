# Basic Test Example

## Description

The `test_mcp_client.py` script demonstrates how to:
- Connect to the HubSpot MCP server
- Test the available tools
- Handle errors and display results

## Prerequisites

```bash
# Install dependencies
pip install httpx mcp

# Set HubSpot API key
export HUBSPOT_API_KEY="your_api_key_here"
```

## Usage

```bash
# Run the test script
python test_mcp_client.py
```

## Expected Output

### Test 1: Basic Contact Retrieval
```
🧪 Test 1: List contacts (basic)...
✅ Contacts retrieved successfully:
📋 **HubSpot Contacts** (5 found)

**John Doe**
  📧 Email: john.doe@example.com
  🏢 Company: Acme Corp
  📞 Phone: +33123456789
  🆔 ID: 12345
```

### Test 2: Search with Filter
```
🧪 Test 2: Search contacts with filter...
✅ Search performed successfully:
📋 **HubSpot Contacts** (2 found)

**Test Contact**
  📧 Email: test@example.com
  🏢 Company: Test Corp
  🆔 ID: 67890
```

## Example Complete Output

```
🚀 Starting HubSpot MCP server tests...

✅ Successfully connected to HubSpot MCP server
📋 Retrieving list of tools...
✅ Found 5 available tools:

- list_hubspot_contacts: Lists HubSpot contacts with filtering capability
- list_hubspot_companies: Lists HubSpot companies with filtering capability 
- list_hubspot_deals: Lists HubSpot deals with filtering capability
- get_deal_by_name: Retrieves a HubSpot deal by its exact name
- get_hubspot_contact_properties: Retrieves contact field properties with types and descriptions

============================================================

🧪 Test 1: List contacts (basic)...
✅ Contacts retrieved successfully:
📋 **HubSpot Contacts** (5 found)

**John Doe**
  📧 Email: john.doe@example.com
  🏢 Company: Acme Corp
  📞 Phone: +33123456789
  🆔 ID: 12345

🧪 Test 2: Search contacts with filter...
✅ Search performed successfully:
📋 **HubSpot Contacts** (1 found)

**Test User**
  📧 Email: test@company.com
  🏢 Company: Test Company
  🆔 ID: 54321

🧪 Test 3: List companies...
✅ Companies retrieved successfully:
🏢 **HubSpot Companies** (3 found)

**TechCorp Solutions**
  🌐 Domain: techcorp.com
  🏭 Industry: Technology
  👥 Employees: 150
  🆔 ID: 67890

🧪 Test 4: List deals...
✅ Deals retrieved successfully:
💰 **HubSpot Deals** (2 found)

**Premium Contract 2024**
  💰 Amount: €45,000.00
  📊 Stage: proposal
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 789012

🧪 Test 5: Get contact properties...
✅ Contact properties retrieved successfully:
🔧 **HubSpot Contact Properties** (405 properties)

## 📁 contactinformation

**📧 Email Address**
  🏷️ Name: `email`
  🔧 Type: string (text)
  📝 Description: The contact's email address
... (showing first 10 lines of 50+ total)

🔌 Disconnected from server
✅ Tests completed!
```

## Error Handling

The script automatically handles:
- Missing API key configuration
- Server connection errors
- Individual tool call failures
- Response formatting issues

## Troubleshooting

1. **API Key Error**: Ensure `HUBSPOT_API_KEY` is set
2. **Connection Error**: Check that the main server script is accessible
3. **Permission Error**: Verify your HubSpot API key has the necessary permissions 