# FastAgent HubSpot Example

This example demonstrates how to use the HubSpot MCP server with FastAgent to create an interactive chat agent.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set up your HubSpot API key:
```bash
export HUBSPOT_API_KEY="your_hubspot_api_key_here"
```

3. Run the agent:
```bash
cd examples/fastagent/
uv run agent.py
```

## Usage

Once started, you can interact with the agent using natural language to:

- List HubSpot contacts, companies, deals, and engagements
- Search for specific deals using advanced filters
- Create new deals
- Get property information for HubSpot objects

Example queries:
- "Show me the top 5 contacts"
- "Find deals related to Cardiologs"
- "Create a new deal for Acme Corp worth $50,000"
- "List all companies in the CRM"

## Configuration

The agent uses the configuration in `fastagent.config.yaml` which references the HubSpot MCP server. Make sure your API key is set in the environment variable `HUBSPOT_API_KEY`. 