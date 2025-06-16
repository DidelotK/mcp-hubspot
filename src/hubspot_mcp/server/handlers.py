"""MCP server handlers for HubSpot tools, prompts, and resources."""

import logging
from typing import Any, Dict, List, Optional, Sequence

import mcp.types as types

from ..client import HubSpotClient
from ..prompts import HubSpotPrompts
from ..resources import HubSpotResources
from ..tools import AVAILABLE_TOOLS

logger = logging.getLogger(__name__)


class HubSpotHandlers:
    """MCP server handlers for HubSpot operations."""

    def __init__(self, client: HubSpotClient):
        """Initialize handlers with HubSpot client.

        Args:
            client: The HubSpot API client instance
        """
        self.client = client
        self.tools = {
            tool(client).get_tool_definition().name: tool for tool in AVAILABLE_TOOLS
        }
        self.prompts = HubSpotPrompts()
        self.resources = HubSpotResources()

    async def handle_list_tools(self) -> List[types.Tool]:
        """Handle list_tools request.

        Returns:
            List[types.Tool]: List of available tool definitions
        """
        try:
            return [
                tool_class(self.client).get_tool_definition()
                for tool_class in self.tools.values()
            ]
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []

    async def handle_call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Handle call_tool request.

        Args:
            name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            List[types.TextContent]: Tool execution results
        """
        try:
            # Check if client is initialized
            if self.client is None:
                error_msg = "HubSpot client not initialized"
                logger.error(error_msg)
                return [types.TextContent(type="text", text=f"Error: {error_msg}")]

            if name not in self.tools:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                return [types.TextContent(type="text", text=f"Error: {error_msg}")]

            tool_class = self.tools[name]
            tool = tool_class(self.client)
            return await tool.execute(arguments)
        except Exception as e:
            error_msg = f"Error executing tool {name}: {e}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=f"Error: {error_msg}")]

    async def handle_list_prompts(self) -> List[types.Prompt]:
        """Handle list_prompts request.

        Returns:
            List[types.Prompt]: List of available prompt definitions
        """
        try:
            return self.prompts.get_prompt_definitions()
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []

    async def handle_get_prompt(
        self, name: str, arguments: Optional[Dict[str, Any]]
    ) -> types.GetPromptResult:
        """Handle get_prompt request.

        Args:
            name: Name of the prompt to get
            arguments: Arguments for the prompt

        Returns:
            types.GetPromptResult: Prompt content result
        """
        try:
            # Handle None arguments by converting to empty dict
            if arguments is None:
                arguments = {}
            content = self.prompts.generate_prompt_content(name, arguments)
            return types.GetPromptResult(
                description=f"Generated guidance for {name}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=content),
                    )
                ],
            )
        except Exception as e:
            error_msg = f"Error generating prompt {name}: {e}"
            logger.error(error_msg)
            return types.GetPromptResult(
                description=f"Error generating prompt {name}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text", text=f"Error: {error_msg}"
                        ),
                    )
                ],
            )

    async def handle_list_resources(self) -> List[types.Resource]:
        """Handle list_resources request.

        Returns:
            List[types.Resource]: List of available resource definitions
        """
        try:
            return self.resources.get_resource_definitions()
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []

    async def handle_read_resource(self, uri: str) -> types.ReadResourceResult:
        """Handle read_resource request.

        Args:
            uri: URI of the resource to read

        Returns:
            types.ReadResourceResult: Resource content result
        """
        try:
            content = self.resources.read_resource(uri)

            # Determine content type based on resource
            if uri.endswith((".json", "/tools", "/fields", "/template")):
                content_type = "application/json"
            else:
                content_type = "text/markdown"

            return types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(
                        uri=uri, mimeType=content_type, text=content
                    )
                ]
            )
        except Exception as e:
            error_msg = f"Error reading resource {uri}: {e}"
            logger.error(error_msg)
            return types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(
                        uri=uri, mimeType="text/plain", text=f"Error: {error_msg}"
                    )
                ]
            )
