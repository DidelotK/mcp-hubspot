import asyncio

from mcp_agent.core.fastagent import FastAgent

# Create the application
fast = FastAgent("Sales Agent")


# Define the agent
@fast.agent(
    name="agent",
    instruction="You are a helpful AI Agent",
    model="gpt-4.1",
    use_history=True,
    servers=["hubspot-agent"],  # Name of an MCP Server defined in fastagent.config.yaml
    human_input=True,
)
async def main():
    # use the --model command line switch or agent arguments to change model
    async with fast.run() as agent:
        await agent.interactive()


if __name__ == "__main__":
    asyncio.run(main())
