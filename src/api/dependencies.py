import os
import sys
from functools import lru_cache

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.infrastructure.openai_adapter import OpenAIAdapter
from src.infrastructure.azure_rag_repository import AzureRAGRepository
from src.use_cases.agent_orchestrator_use_case import AgentOrchestratorUseCase

"""
    ¿Por qué @lru_cache?

    Porque FastAPI lo construirá una sola vez.
"""

graph = None

@lru_cache
def get_llm():

    return OpenAIAdapter()

@lru_cache
def get_rag():

    return AzureRAGRepository()

orchestrator: AgentOrchestratorUseCase | None = None

@lru_cache
def get_orchestrator():

    return orchestrator

def get_graph():
    return graph