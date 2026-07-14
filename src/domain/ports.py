from abc import ABC, abstractmethod
from typing import List
from .state import AgentState # Importamos nuestro estado tipado

class ILLMService(ABC): # ENCHUFE (Interfaz) para cualquier Modelo de Lenguaje
    """
    Puerto (Interfaz) para cualquier Modelo de Lenguaje.
    El agente usará esto sin importar si debajo hay OpenAI, Anthropic o Llama.
    """
    @abstractmethod
    def generate_response(self, state: AgentState) -> AgentState:
        """
        Toma el estado actual del agente, procesa el razonamiento y 
        devuelve el estado actualizado con la nueva respuesta.
        """
        pass

class IRagRepository(ABC):
    """
    Puerto (Interfaz) para el acceso a documentos vectoriales (Azure Blob/AI Search).
    """
    @abstractmethod
    def retrieve_context(self, query: str) -> str:
        """
        Recibe una consulta de búsqueda y devuelve un string con el 
        contexto estructurado de los documentos más relevantes.
        """
        pass

class IMcpToolClient(ABC):
    """
    Puerto (Interfaz) para la comunicación con tu servidor MCP en Azure Web App.
    """
    @abstractmethod
    def execute_tool(self, tool_name: str, parameters: dict) -> str:
        """
        Ejecuta una herramienta remota y devuelve el resultado.
        """
        pass