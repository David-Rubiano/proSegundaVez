import os
from mcp import ClientSession
from mcp.client.sse import sse_client
from src.domain.ports import IMcpToolClient

class AzureMcpAdapter(IMcpToolClient):
    """
    Adaptador concreto para comunicarse con tu servidor MCP en Azure Web App.
    Implementa el puerto IMcpToolClient de la capa de Dominio.
    """
    
    def __init__(self):
        # La URL del endpoint SSE de tu Web App en Azure
        # Ejemplo: https://mi-servidor-mcp.azurewebsites.net/sse
        self.server_url = os.getenv("MCP_SERVER_URL")
        
        if not self.server_url:
            raise ValueError("Falta la variable de entorno MCP_SERVER_URL para el servidor MCP")

    async def execute_tool(self, tool_name: str, parameters: dict) -> str:
        """
        Se conecta dinámicamente al servidor remoto, ejecuta la herramienta 
        y devuelve el texto resultante.
        """
        try:
            # 1. Establecemos la conexión HTTP/SSE con Azure Web App
            async with sse_client(url=self.server_url) as streams:
                # 2. Iniciamos la sesión del protocolo MCP
                async with ClientSession(streams[0], streams[1]) as session:
                    await session.initialize()

                    # 3. Invocamos la herramienta usando el nombre y los argumentos que el LLM decidió
                    result = await session.call_tool(tool_name, arguments=parameters)

                    # 4. Extraemos el texto de la respuesta del servidor
                    if result.content:
                        return result.content[0].text
                        
                    return f"Herramienta '{tool_name}' ejecutada con éxito, pero sin contenido de retorno."
                    
        except Exception as e:
            # En un entorno de producción, aquí usaríamos el logger estructurado
            print(f"[Error AzureMcpAdapter] Fallo al ejecutar la herramienta '{tool_name}': {e}")
            return f"Error de infraestructura ejecutando herramienta: {str(e)}"