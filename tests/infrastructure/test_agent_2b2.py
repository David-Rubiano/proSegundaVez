import asyncio
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))
print(f"Esta es la raiz : {raiz_proyecto}")

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

# 1. Importamos la Infraestructura (Adaptadores)
from src.infrastructure.openai_adapter import OpenAIAdapter
from src.infrastructure.azure_rag_repository import AzureRAGRepository
from src.infrastructure.mcp_adapter import AzureMcpAdapter

# 2. Importamos los Casos de Uso y el Dominio
from src.use_cases.agent_orchestrator_use_case import AgentOrchestratorUseCase
from src.domain.state import AgentState

async def run_agent_test():
    print("🚀 Iniciando prueba End-to-End del Agente de IA...")
    load_dotenv()

    try:
        # Paso A: Inicializar Infraestructura
        print("🔌 Conectando adaptadores (OpenAI, RAG, MCP)...")
        llm_adapter = OpenAIAdapter()
        await llm_adapter.initialize()
        rag_adapter = AzureRAGRepository()        
        

        # Paso B: Inyección de Dependencias
        print("🧠 Ensamblando el cerebro (LangGraph)...")
        orchestrator = AgentOrchestratorUseCase(
            llm_service=llm_adapter,
            rag_repository=rag_adapter            
        )

        
        # Asumimos que dentro de tu orquestador creaste el StateGraph y lo compilaste.
        # Si tienes el código del grafo en un método, llámalo aquí. Por ejemplo:
        # app = orchestrator.build_graph() 
        # (Asegúrate de devolver el grafo compilado desde tu clase)
        app = orchestrator.compile_graph()

        # Paso C: Crear el Estado Inicial (El vehículo de datos)
        # Haremos una pregunta que obligue al agente a pensar, buscar y actuar
        pregunta_usuario = "¿Consulta 1 SalesLT.Customer de la base de datos?"
        
        estado_inicial = AgentState(
            messages=[HumanMessage(content=pregunta_usuario)]
        )

        # Paso D: Ejecutar el Grafo
        print(f"\n👤 Usuario: {pregunta_usuario}")
        print("\n🤖 El Agente está pensando (observa los logs de los nodos)...")
        
        # Usamos ainvoke porque nuestro mcp_tool_node es asíncrono
        resultado_final = await app.ainvoke(estado_inicial)

        # Paso E: Mostrar el resultado final
        # LangGraph devuelve el estado completo actualizado. Extraemos el último mensaje.
        respuesta_agente = resultado_final["messages"][-1].content
        
        print("\n=========================================")
        print(f"✅ Respuesta Final del Agente:\n{respuesta_agente}")
        print("=========================================\n")

    except Exception as e:
        print(f"\n❌ Ocurrió un error en la ejecución: {e}")

if __name__ == "__main__":
    # Ejecutamos el ciclo de eventos asíncrono de Python
    asyncio.run(run_agent_test())