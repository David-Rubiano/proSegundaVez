import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = "https://sqlserver-mcp.blackbush-1592a005.southcentralus.azurecontainerapps.io/mcp"


async def main():

    async with streamable_http_client(URL) as (
        read_stream,
        write_stream,
        _,
    ):

        async with ClientSession(read_stream, write_stream) as session:

            print("Inicializando...")

            await session.initialize()

            print("OK")

            tools = await session.list_tools()

            print("\nHerramientas:")

            for tool in tools.tools:
                print(tool.name)

            print("\nListar tablas")

            result = await session.call_tool(
                "list_tables",
                arguments={}
            )

            print(result.content)

            print("\nDescribir tabla")

            result = await session.call_tool(
                "execute_query",
                arguments={
                    "query": "SELECT TOP 5 * FROM SalesLT.Customer"
                }
            )

            print(result.content)


asyncio.run(main())