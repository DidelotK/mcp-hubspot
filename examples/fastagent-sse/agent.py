"""FastAgent SSE example for HubSpot MCP server integration."""

import asyncio

from mcp_agent.core.fastagent import FastAgent

# Create the application
fast = FastAgent("HubSpot Sales Agent")


# Define the agent
@fast.agent(
    name="hubspot_sse_agent",
    instruction="""You are a helpful HubSpot CRM assistant. You have access to HubSpot data through an MCP server.

    You can help with:
    - Listing and searching contacts, companies, deals, and engagements
    - Creating new deals and updating existing ones
    - Retrieving property information for CRM objects
    - Managing cache and embeddings for better search performance
    - Performing semantic searches across HubSpot data

    Always provide clear, structured responses and suggest relevant follow-up actions when appropriate.""",
    model="gpt-4o-mini",
    use_history=True,
    servers=[
        "hubspot-sse"
    ],  # Name of the SSE MCP Server defined in fastagent.config.yaml
    human_input=True,
)
async def main():
    """Run FastAgent function for HubSpot SSE integration."""
    # Use the --model command line switch or agent arguments to change model
    async with fast.run() as agent:
        print("🚀 HubSpot FastAgent SSE Demo Started!")
        print("💡 You can now interact with your HubSpot CRM using natural language.")
        print("📝 Example commands:")
        print("   - 'Show me the latest 10 contacts'")
        print("   - 'Find deals worth more than $10,000'")
        print("   - 'Create a new deal for Acme Corp worth $25,000'")
        print("   - 'Search for companies in the technology industry'")
        print("   - 'Load contacts into cache and build embeddings'")
        print("   - 'Search semantically for software engineers'")
        print("-" * 60)

        await agent.interactive()


if __name__ == "__main__":
    asyncio.run(main())
