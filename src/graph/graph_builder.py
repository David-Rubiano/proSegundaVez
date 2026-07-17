import os
import sys
from langgraph.graph import StateGraph, END

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.domain.state import AgentState
from src.use_cases.agent_orchestrator_use_case import AgentOrchestratorUseCase

# Crear el constructor

class GraphBuilder:

    def __init__(self, orchestrator: AgentOrchestratorUseCase):

        self.orchestrator = orchestrator

    def compile_graph(self):
            """
            Ensambla los nodos y los bordes para crear la Máquina de Estados.
            Retorna el grafo listo para ejecutarse.
            """
            print("⚙️ Ensamblando el Grafo del Agente...")
            
            # 1. Instanciamos el grafo pasándole nuestro modelo de datos estricto (Pydantic)
            graph = StateGraph(AgentState)

            # 2. Registramos nuestras paradas (Nodos)
            graph.add_node("reasoning_node", self.orchestrator.reasoning_node)        
            graph.add_node("rag_node", self.orchestrator.rag_node)
            # graph.add_node("rag_node", self.rag_node) # Lo comentamos temporalmente si el RAG será tratado como Tool

            # 3. Definimos por dónde empieza a moverse el vehículo
            graph.set_entry_point("reasoning_node")

            # 4. Añadimos el Semáforo (Borde Condicional) después de que el LLM piensa
            graph.add_conditional_edges(
                "reasoning_node", # Nodo de origen
                self.orchestrator.router_node, # La función que decide el camino
                {
                    "rag_node": "rag_node", # Si el router devuelve "rag_node", ve allí                
                    END: END # Si el router devuelve END, termina el flujo
                }
            )

            # 5. Añadimos Bordes Estáticos (Ciclo ReAct)
            # ¡Esta es la clave! Después de ejecutar una herramienta, SIEMPRE debemos 
            # devolver el estado al LLM para que lea el resultado de la herramienta.
            graph.add_edge("rag_node", "reasoning_node")        

            # 6. Compilamos el sistema
            return graph.compile()        