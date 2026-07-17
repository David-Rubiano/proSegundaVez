import os
import sys
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage


raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.domain import state
from src.domain.state import AgentState
from src.domain.ports import ILLMService, IRagRepository

class AgentOrchestratorUseCase:
    """
    Caso de Uso Principal: Ensambla y coordina el flujo del Agente ReAct.
    """
    
    def __init__(
        self,
        llm_service: ILLMService,
        rag_repository: IRagRepository
        
    ):
        # Aplicamos Inyección de Dependencias
        self.llm = llm_service
        self.rag = rag_repository        

    # ---------------------------------------------------------
    # DEFINICIÓN DE NODOS (Trabajadores del Grafo)
    # ---------------------------------------------------------

    async def reasoning_node(self, state: AgentState) -> dict:
        """
        NODO 1: El Cerebro Analítico.
        Llama al LLM para razonar sobre el estado actual y decidir el siguiente paso.
        """
        print("🧠 [Nodo: Razonamiento] El LLM está analizando el contexto...")
        
        # Delegamos el trabajo al adaptador LLM, el cual devuelve el dict {"messages": [...]}
        return await self.llm.generate_response(state)

    def rag_node(self, state: AgentState) -> dict:
        """
        NODO 2: El Buscador (Sentido de lectura).
        Si el LLM necesita información de la empresa, este nodo busca en Azure.
        """
        print("🔍 [Nodo: RAG] Buscando documentos en la base vectorial...")
        
        # 1. Extraemos la última interacción del usuario
        # (Asumimos por ahora que el último mensaje es del usuario)
        ultima_pregunta = state.messages[-1].content
        
        # 2. Usamos nuestro puerto RAG para buscar fragmentos
        fragmentos = self.rag.retrieve(query=ultima_pregunta, limit=3)
        
        # 3. Unimos los fragmentos en un gran bloque de texto
        contexto_unido = "\n\n---\n\n".join(fragmentos)
        
        # 4. Actualizamos SOLO la propiedad 'rag_context' del estado
        return {"rag_context": contexto_unido}

    

    # ---------------------------------------------------------
    # DEFINICIÓN DE BORDES (El Semáforo)
    # ---------------------------------------------------------

    def router_node(self, state: AgentState) -> str:
        """
        El Semáforo (Conditional Edge).
        Analiza el último mensaje generado por el LLM para decidir la ruta.
        Decide si ejecutar RAG o terminar.
        El MCP ya es manejado internamente por create_agent().
        """
        print("🚦 [Semáforo] Evaluando el estado para decidir el siguiente paso...")
        
        # Obtenemos el último mensaje del historial

        if state.rag_context:
            print("✅ Ya existe contexto RAG. Finalizando.")
            return END
        

        last_message = None

        for msg in reversed(state.messages):
            if isinstance(msg, HumanMessage):
                last_message = msg
                break        

        if last_message is None:
            return END

        pregunta = last_message.content.lower()
        
        palabra_clave_rag = ["pdf",
                             "empleo",
                             "empleos",
                             "trabajo",
                             "trabajos",
                             "curriculum",
                             "cv",
                             "currículum",
                             "curriculo",
                             "curriculos",
                             "currículos", 
                             "Colombia",
                             "IA",
                             "Trabajo IA", 
                             "Vacantes",
                             "vacante",
                             "vacantes",
                             "vacancia",
                             "vacancias",
                             "oferta laboral",
                             "ofertas laborales",
                             "oferta de trabajo",
                             "ofertas de trabajo",
                             "oferta de empleo",
                             "ofertas de empleo"]

        # (Nota Arquitectónica: En un sistema 100% acoplado, el RAG también sería una herramienta.
        # Si tuviéramos una herramienta 'buscar_documentos', el LLM la invocaría arriba).
        # Si ya ejecutamos el RAG, no volver a hacerlo

        # Si aún no existe contexto, decidir si usar RAG
        if any(palabra.lower() in pregunta for palabra in palabra_clave_rag):
            print("🔍 Se detectó una consulta documental.")
            return "rag_node"
        return END
    
        print("   -> 🛑 El LLM generó una respuesta final. Terminando ciclo.")
        # Si no hay llamadas a herramientas, terminamos el grafo
        return END

    # ---------------------------------------------------------
    # COMPILACIÓN DEL GRAFO (Ensamblaje final)
    # ---------------------------------------------------------

    def compile_graph(self):
        """
        Ensambla los nodos y los bordes para crear la Máquina de Estados.
        Retorna el grafo listo para ejecutarse.
        """
        print("⚙️ Ensamblando el Grafo del Agente...")
        
        # 1. Instanciamos el grafo pasándole nuestro modelo de datos estricto (Pydantic)
        graph = StateGraph(AgentState)

        # 2. Registramos nuestras paradas (Nodos)
        graph.add_node("reasoning_node", self.reasoning_node)        
        graph.add_node("rag_node", self.rag_node)
        # graph.add_node("rag_node", self.rag_node) # Lo comentamos temporalmente si el RAG será tratado como Tool

        # 3. Definimos por dónde empieza a moverse el vehículo
        graph.set_entry_point("reasoning_node")

        # 4. Añadimos el Semáforo (Borde Condicional) después de que el LLM piensa
        graph.add_conditional_edges(
            "reasoning_node", # Nodo de origen
            self.router_node, # La función que decide el camino
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