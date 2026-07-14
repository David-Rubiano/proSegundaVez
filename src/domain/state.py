from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# Nucleo de datos
class AgentState(BaseModel):
    """
    Estado global que viajará por todos los nodos de nuestro grafo en LangGraph.
    Garantiza el tipado y la validación en cada transición.
    """
    
    # Historial de conversación
    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)
    
    # Almacenará los documentos recuperados de Azure Blob Storage (Capa RAG)
    rag_context: str = Field(default="")
    
    # Datos estructurados o banderas provenientes de tu servidor MCP
    mcp_tool_result: str = Field(default="")