import asyncio
import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    load_dotenv()

    # Modelo
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    # Cliente MCP
    client = MultiServerMCPClient(
        {
            "sqlserver": {
                "transport": "http",
                "url": os.getenv("MCP_SERVER_URL")
            }
        }
    )

    print("Conectando al servidor MCP...")

    # Descubre automáticamente las herramientas
    tools = await client.get_tools()

    print("\nHerramientas encontradas:")

    for tool in tools:
        print(f"- {tool.name}")

    # Crear agente ReAct
    agent = create_agent(
        llm,
        tools
    )

    pregunta = """
    Consulta los primeros 5 registros de la tabla SalesLT.Customer.
    Utiliza las herramientas disponibles.
    No escribas SQL manualmente.
    """

    print("\nPregunta:")
    print(pregunta)

    respuesta = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": pregunta
                }
            ]
        }
    )

    print("\nRespuesta:\n")
    print(respuesta)


if __name__ == "__main__":
    asyncio.run(main())