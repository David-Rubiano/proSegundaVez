import os
import sys
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.api.routers.chat import router as chat_router
from src.api import dependencies
from src.infrastructure.openai_adapter import OpenAIAdapter
from src.infrastructure.azure_rag_repository import AzureRAGRepository
from src.use_cases.agent_orchestrator_use_case import AgentOrchestratorUseCase
from src.graph.graph_builder import GraphBuilder

load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import dependencies
from src.infrastructure.openai_adapter import OpenAIAdapter
from src.infrastructure.azure_rag_repository import AzureRAGRepository
from src.use_cases.agent_orchestrator_use_case import AgentOrchestratorUseCase


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Inicializando Agente...")

    llm = OpenAIAdapter()
    await llm.initialize()

    rag = AzureRAGRepository()

    dependencies.orchestrator = AgentOrchestratorUseCase(
        llm_service=llm,
        rag_repository=rag
    )
    print("Agente listo.")

    builder = GraphBuilder(
        dependencies.orchestrator
    )

    dependencies.graph = builder.compile_graph()

    print("Grafo compilado")

    yield

    print("🛑 Cerrando aplicación...")

app = FastAPI(
    title="Agente IA",
    lifespan=lifespan
)

app.include_router(chat_router)