import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.infrastructure.openai_adapter import OpenAIAdapter
from src.domain.state import AgentState

# Usamos el decorador patch para interceptar la clase ChatOpenAI ANTES de que el adaptador la use
@patch("src.infrastructure.openai_adapter.ChatOpenAI")
def test_openai_adapter_generates_response(mock_chat_openai):
    """
    Verifica que el adaptador extrae los mensajes del estado, 
    llama al LLM y devuelve el diccionario con el formato correcto para LangGraph.
    """
    # 1. Configurar el "doble de riesgo" (Mock)
    mock_llm_instance = MagicMock()
    # Le decimos al mock: "Cuando llamen a tu método .invoke(), devuelve este mensaje prefabricado"
    mock_llm_instance.invoke.return_value = AIMessage(content="Respuesta simulada")
    mock_chat_openai.return_value = mock_llm_instance

    # 2. Instanciar nuestro adaptador (creerá que está usando el OpenAI real)
    adapter = OpenAIAdapter(model_name="gpt-4o")

    # 3. Preparar el vehículo de datos (Estado) inicial
    initial_state = AgentState(
        messages=[HumanMessage(content="Hola agente")]
    )

    # 4. Ejecutar el método que queremos probar
    result = adapter.generate_response(initial_state)

    # 5. Validaciones (Asserts)
    # Comprobamos que devuelve un diccionario con la llave "messages"
    assert "messages" in result
    # Comprobamos que el contenido es exactamente el que simulamos
    assert result["messages"][0].content == "Respuesta simulada"
    # Comprobamos que nuestro adaptador efectivamente le pasó el historial al LLM
    mock_llm_instance.invoke.assert_called_once_with(initial_state.messages)