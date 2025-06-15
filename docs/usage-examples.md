# Usage Examples

## Example Conversations

### Example 1: List Contacts

**User:** *"Can you list the first 10 HubSpot contacts for me?"*

**MCP Server:** *I'll retrieve the first 10 contacts from your HubSpot.*

*[MCP Server automatically uses the `list_hubspot_contacts` tool with limit: 10]*

**Displayed Result:**
```
📋 **HubSpot Contacts** (10 found)

**Jean Dupont**
  📧 Email: jean.dupont@example.com
  🏢 Company: Acme Corp
  📞 Phone: +33123456789
  🆔 ID: 12345

**Marie Martin**
  📧 Email: marie.martin@techcorp.com
  🏢 Company: TechCorp Solutions
  📞 Phone: +33987654321
  🆔 ID: 12346
...
```

### Example 2: Search for a Deal

**User:** *"Find me the deal 'Premium Contract 2024'"*

**MCP Server:** *I'm searching for this specific deal in your HubSpot.*

*[MCP Server uses the `get_deal_by_name` tool with deal_name: "Premium Contract 2024"]*

**Displayed Result:**
```
💰 **HubSpot Deal**

**Premium Contract 2024**
  💰 Amount: €45,000.00
  📊 Stage: proposal
  🔄 Pipeline: enterprise
  📅 Close Date: 2024-12-31
  🆔 ID: 789012
```

### Example 3: Filter Companies

**User:** *"Show me the companies in the 'technology' sector"*

**MCP Server:** *I'm searching for companies in the technology sector.*

*[MCP Server uses the `list_hubspot_companies` tool with filters: {"search": "technology"}]*

**Displayed Result:**
```
🏢 **HubSpot Companies** (3 found)

**TechCorp Solutions**
  🌐 Domain: techcorp.com
  🏭 Industry: Technology
  👥 Employees: 150
  🆔 ID: 67890

**InnovateTech**
  🌐 Domain: innovatetech.fr
  🏭 Industry: Software Technology
  👥 Employees: 75
  🆔 ID: 67891
```

### Example 4: Analyze Deals

**User:** *"What are the deals worth more than €10,000?"*

**MCP Server:** *I'll search for the significant deals in your pipeline.*

*[MCP Server uses the `list_hubspot_deals` tool with filters: {"amount_gte": 10000}]*

---

**User:** *"What are the available properties for HubSpot contacts?"*

**MCP Server:** *I'll retrieve the list of contact properties with their types and descriptions.*

*[MCP Server uses the `get_hubspot_contact_properties` tool]*

**Displayed Result:**
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

**📞 Phone Number**
  🏷️ Name: `phone`
  🔧 Type: string (text)
  📝 Description: The contact's primary phone number

## 📁 demographic_information

**📅 Date of Birth**
  🏷️ Name: `date_of_birth`
  🔧 Type: date (date)
  📝 Description: The contact's date of birth
...
```

## Useful Commands for MCP Server

### Contact Search
- *"List all my HubSpot contacts"*
- *"Find contacts from Acme company"*
- *"Search for the contact jean.dupont@example.com"*
- *"Show the last 20 contacts"*

### Company Management
- *"Show me all companies"*
- *"Find French companies"*
- *"Search for companies in the automotive sector"*
- *"List companies with more than 100 employees"*

### Deal Analysis
- *"Show all deals"*
- *"What are the current deals?"*
- *"Find deals in the 'enterprise' pipeline"*
- *"Search for the deal 'Project X'"*
- *"Show deals closed this month"*

### Data Exploration
- *"What are the available properties for contacts?"*
- *"Show me the HubSpot contact fields"*
- *"List the contact data types"*

### Combined Searches
- *"Find all TechCorp contacts and their deals"*
- *"Analyze the technology sector performance"*
- *"What are the biggest deals in progress?"*

## Business Use Cases

### 1. Daily Sales Follow-up

**Scenario:** A salesperson wants to review their prospects

**Commands:**
1. *"List my last 10 contacts"*
2. *"What deals are in negotiation phase?"*
3. *"Show me deals closing this week"*

### 2. Sector Analysis

**Scenario:** Analyze opportunities in a sector

**Commands:**
1. *"Find all companies in the 'fintech' sector"*
2. *"What are their current deals?"*
3. *"What's the total amount of fintech deals?"*

### 3. Client Meeting Preparation

**Scenario:** Prepare for a client meeting

**Commands:**
1. *"Find the company 'Acme Corp'"*
2. *"List all contacts from this company"*
3. *"What are their active deals?"*

### 4. Weekly Reporting

**Scenario:** Generate activity report

**Commands:**
1. *"List all deals created this week"*
2. *"How many new contacts do we have?"*
3. *"What are the most promising deals?"*

## Advanced Filter Examples

### Search by Amount
```
"Find deals between €5,000 and €50,000"
→ filters: {"amount_gte": 5000, "amount_lte": 50000}
```

### Search by Stage
```
"Show deals in proposal phase"
→ filters: {"stage": "proposal"}
```

### Text Search
```
"Search for contacts with 'manager' in their title"
→ filters: {"search": "manager"}
```

### Combined Filters
```
"Find tech companies with more than 50 employees"
→ filters: {"search": "tech", "employees_gte": 50}
```

## Running the FastAgent interactive example

An interactive conversational agent powered by the **FastAgent** SDK is included in
`examples/fastagent-stdio/agent.py`.  It embeds the HubSpot MCP server declared in
`fastagent.config.yaml` and lets you chat with your CRM from the console.

### Prerequisites

```bash
# Install project dependencies (if not done yet)
uv sync

# Ensure your HubSpot credentials are set
export HUBSPOT_API_KEY="<your_key>"
```

### Start the agent

```bash
uv run examples/fastagent/agent.py
```

When the script starts you will see a prompt like:

```
🤖  Sales Agent ready! Type your questions.
> 
```

Try something like:

```
> List the top 5 HubSpot deals over €10 000
```

The agent will internally call `search_hubspot_deals` (or other appropriate tools)
and stream back a nicely formatted answer enriched with emojis *plus* a collapsible
raw-JSON block for advanced inspection.

Press <kbd>Ctrl+C</kbd> to exit the chat.

--- 