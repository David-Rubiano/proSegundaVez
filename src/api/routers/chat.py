import os
import sys
from fastapi import APIRouter, Depends
from  langchain_core.messages import HumanMessage

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.api.models import ChatRequest, ChatResponse
from src.api.dependencies import get_orchestrator, get_graph
from src.use_cases.agent_orchestrator_use_case import AgentOrchestratorUseCase
from src.domain.state import AgentState

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    # "message": "Endpoint funcionando" uso para prueba del endpoint
    request: ChatRequest,
    graph = Depends(get_graph)
):    
    state = AgentState(
        messages=[
            HumanMessage(content=request.question)
        ]
    )    

    result = await graph.ainvoke(state)

    answer = result["messages"][-1].content

    return ChatResponse (
        answer=answer
    )