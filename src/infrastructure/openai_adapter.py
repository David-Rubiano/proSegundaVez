import os
from langchain_openai import ChatOpenAI
from src.domain.ports import ILLMService
from src.domain.state import AgentState

class OpenAIAdapter(ILLMService):
    """
    Adaptador concreto para OpenAI. 
    Implementa el 'enchufe' (ILLMService) definido en nuestra capa de Dominio.
    """
    
    def __init__(self, model_name: str = "gpt-4o"):
        # Inicializamos el cliente de OpenAI. 
        # La API Key se lee automáticamente de las variables de entorno.
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.0 # Usamos 0.0 para que el agente sea determinista y lógico, no creativo
        )

    def generate_response(self, state: AgentState) -> dict:
        """
        Cumple con el contrato del puerto.
        """
        # 1. Extraemos el historial de mensajes de nuestro vehículo de datos
        messages = state.messages
        
        # 2. Pasamos los mensajes al modelo real de OpenAI
        response = self.llm.invoke(messages)
        
        # 3. Retornamos la actualización del estado.
        # LangGraph tomará este diccionario y usará el reducer (add_messages) 
        # para añadir la nueva respuesta al historial global.
        return {"messages": [response]}