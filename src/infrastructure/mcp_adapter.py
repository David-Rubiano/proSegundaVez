import os
import sys
from mcp import ClientSession

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.domain.ports import IMcpToolClient

from mcp.client.streamable_http import streamable_http_client

class AzureMcpAdapter(IMcpToolClient):

    def __init__(self):
        self.server_url = os.getenv("MCP_SERVER_URL")
        self.tools = []

    async def list_tools(self):

        async with streamable_http_client(self.server_url) as (
            read_stream,
            write_stream,
            _,
        ):

            async with ClientSession(read_stream, write_stream) as session:

                await session.initialize()

                tools = await session.list_tools()

                return tools.tools
            
    async def initialize(self):

        self.tools = await self.list_tools()

        print("\nHerramientas MCP encontradas:\n")

        for tool in self.tools:
            print(tool.name)

    async def execute_tool(self, tool_name: str, parameters: dict) -> str:

        async with streamable_http_client(self.server_url) as (
            read_stream,
            write_stream,
            _
        ):
            async with ClientSession(read_stream, write_stream) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments=parameters
                )

                if result.content:
                    return result.content[0].text

                return ""