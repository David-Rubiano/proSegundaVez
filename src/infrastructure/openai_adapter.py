import os
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

#print(f"Raíz del proyecto: {raiz_proyecto}")

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.domain.ports import ILLMService
from src.domain.state import AgentState

class OpenAIAdapter(ILLMService):
    """
    Adaptador concreto para OpenAI. 
    Implementa el 'enchufe' (ILLMService) definido en nuestra capa de Dominio.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        # Inicializamos el cliente de OpenAI. 
        # La API Key se lee automáticamente de las variables de entorno.
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.0 # Usamos 0.0 para que el agente sea determinista y lógico, no creativo
        )


    def generate_response(self, state: AgentState) -> dict:

        messages = list(state.messages)

        # Si existe contexto RAG, lo agregamos como contexto del sistema
        if state.rag_context:
            messages.insert(
                0,
                SystemMessage(
                    content=f"""
                    Utiliza el siguiente contexto para responder la pregunta del usuario.
                    Si el contexto contiene la respuesta, priorízalo.
                    Si no es suficiente, indícalo.

                    Contexto:

                    {state.rag_context}
                    """
                                )
                            )

        response = self.llm.invoke(messages)

        return {
            "messages": [response]
        }