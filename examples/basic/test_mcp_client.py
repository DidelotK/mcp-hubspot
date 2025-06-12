#!/usr/bin/env python3
"""
Test script for the HubSpot MCP server.

This script demonstrates how to use an MCP client to connect
to the HubSpot MCP server and test the available tools.
"""

import asyncio
import os
from typing import Any, Dict

# Dependencies: pip install httpx mcp

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPTestClient:
    """Simple test client for the HubSpot MCP server."""
    
    def __init__(self):
        self.session = None
    
    async def connect(self):
        """Connect to the MCP server."""
        # Configure server parameters
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run", 
                "python", 
                "../../main.py",  # Path to main server script
                "--mode", 
                "stdio"
            ],
            env={
                "HUBSPOT_API_KEY": os.getenv("HUBSPOT_API_KEY", "")
            }
        )
        
        # Create session
        self.session = await stdio_client(server_params).__aenter__()
        
        # Initialize session
        await self.session.initialize()
        
        print("✅ Successfully connected to HubSpot MCP server")
    
    async def list_tools(self):
        """List available tools."""
        if not self.session:
            raise Exception("Not connected to server")
        
        response = await self.session.list_tools()
        return response.tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
        """Call a specific tool."""
        if not self.session:
            raise Exception("Not connected to server")
        
        if arguments is None:
            arguments = {}
        
        response = await self.session.call_tool(tool_name, arguments)
        return response
    
    async def disconnect(self):
        """Disconnect from the server."""
        if self.session:
            await self.session.__aexit__(None, None, None)


async def main():
    """Main test function."""
    print("🚀 Starting HubSpot MCP server tests...\n")
    
    # Check API key
    if not os.getenv("HUBSPOT_API_KEY"):
        print("❌ HUBSPOT_API_KEY environment variable not found!")
        print("Please set your HubSpot API key:")
        print("export HUBSPOT_API_KEY='your_api_key_here'")
        return
    
    client = MCPTestClient()
    
    try:
        # Connect to server
        await client.connect()
        
        # List available tools
        print("📋 Retrieving list of tools...")
        tools = await client.list_tools()
        
        print(f"✅ Found {len(tools)} available tools:\n")
        for tool in tools:
            description = getattr(tool, 'description', 'No description')
            print(f"- {tool.name}: {description}")
        
        print("\n" + "="*60 + "\n")
        
        # Test 1: List contacts (basic)
        print("🧪 Test 1: List contacts (basic)...")
        try:
            result = await client.call_tool("list_hubspot_contacts", {"limit": 5})
            if result.content:
                print("✅ Contacts retrieved successfully:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
            else:
                print("⚠️ No results found")
        except Exception as e:
            print(f"❌ Error retrieving contacts: {e}")
        
        # Test 2: Search contacts with filter
        print("\n🧪 Test 2: Search contacts with filter...")
        try:
            result = await client.call_tool("list_hubspot_contacts", {
                "limit": 3,
                "filters": {"search": "test"}
            })
            if result.content:
                print("✅ Search performed successfully:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:300] + "..." if len(content.text) > 300 else content.text)
            else:
                print("⚠️ No results found for search")
        except Exception as e:
            print(f"❌ Error during search: {e}")
        
        # Test 3: List companies
        print("\n🧪 Test 3: List companies...")
        try:
            result = await client.call_tool("list_hubspot_companies", {"limit": 3})
            if result.content:
                print("✅ Companies retrieved successfully:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:300] + "..." if len(content.text) > 300 else content.text)
            else:
                print("⚠️ No companies found")
        except Exception as e:
            print(f"❌ Error retrieving companies: {e}")
        
        # Test 4: List deals
        print("\n🧪 Test 4: List deals...")
        try:
            result = await client.call_tool("list_hubspot_deals", {"limit": 3})
            if result.content:
                print("✅ Deals retrieved successfully:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text[:300] + "..." if len(content.text) > 300 else content.text)
            else:
                print("⚠️ No deals found")
        except Exception as e:
            print(f"❌ Error retrieving deals: {e}")
        
        # Test 5: Get contact properties
        print("\n🧪 Test 5: Get contact properties...")
        try:
            result = await client.call_tool("get_hubspot_contact_properties", {})
            if result.content:
                print("✅ Contact properties retrieved successfully:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        # Show only first part of properties (can be very long)
                        text = content.text
                        lines = text.split('\n')[:10]  # First 10 lines only
                        print('\n'.join(lines))
                        if len(text.split('\n')) > 10:
                            print(f"... (showing first 10 lines of {len(text.split('\n'))} total)")
            else:
                print("⚠️ No properties found")
        except Exception as e:
            print(f"❌ Error retrieving properties: {e}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    finally:
        # Disconnect
        await client.disconnect()
        print("\n🔌 Disconnected from server")
        print("✅ Tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 