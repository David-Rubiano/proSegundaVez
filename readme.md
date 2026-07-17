Sí. Por todo lo que hemos construido durante estas semanas, el proyecto ya tiene una arquitectura bastante sólida. Yo la documentaría de la siguiente manera.

---

# Arquitectura de Software

Se implementó una **Arquitectura Hexagonal (Ports and Adapters)**, cuyo objetivo es desacoplar la lógica de negocio de las tecnologías externas.

```
                    ┌──────────────────────────────┐
                    │      Presentación            │
                    │        Streamlit             │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │       Casos de Uso           │
                    │ AgentOrchestratorUseCase     │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       ILLMService          IRagRepository      IMcpToolClient
              │                    │                    │
      ┌───────▼──────┐    ┌────────▼────────┐   ┌──────▼─────────┐
      │OpenAIAdapter │    │AzureRAGRepository│  │AzureMcpAdapter │
      └──────────────┘    └─────────────────┘   └────────────────┘
```

---

# Patrón Arquitectónico

## Arquitectura Hexagonal (Ports & Adapters)

El núcleo del sistema no conoce ninguna tecnología externa.

Se comunica mediante interfaces (Ports).

Los adaptadores implementan dichas interfaces.

Ejemplos:

```
ILLMService
      │
      ▼
OpenAIAdapter
```

```
IRagRepository
      │
      ▼
AzureRAGRepository
```

```
IMcpToolClient
      │
      ▼
AzureMcpAdapter
```

Esto permite cambiar OpenAI por Anthropic o Azure OpenAI sin modificar el dominio.

---

# Patrones de Diseño utilizados

## 1. Dependency Injection (Inyección de Dependencias)

En lugar de crear los objetos dentro del orquestador, estos se inyectan desde el exterior.

```python
orchestrator = AgentOrchestratorUseCase(
    llm_service=llm_adapter,
    rag_repository=rag_adapter,
    mcp_client=mcp_adapter
)
```

Beneficios

* Bajo acoplamiento
* Fácil testing
* Fácil reemplazo de implementaciones

---

## 2. Adapter Pattern

Cada servicio externo posee un adaptador.

Ejemplos

```
OpenAI
     │
OpenAIAdapter
```

```
Azure AI Search
        │
AzureRAGRepository
```

```
Servidor MCP
        │
AzureMcpAdapter
```

El dominio nunca conoce la API real.

---

## 3. Repository Pattern

Toda la lógica de acceso al índice vectorial quedó encapsulada.

```
IRagRepository

retrieve(...)
```

Implementación

```
AzureRAGRepository
```

Así el dominio nunca sabe que existe Azure AI Search.

---

## 4. Strategy Pattern

El puerto

```
ILLMService
```

permite cambiar el motor de IA.

Actualmente

```
OpenAIAdapter
```

Pero podría ser

```
AnthropicAdapter

AzureOpenAIAdapter

LlamaAdapter
```

Sin modificar el caso de uso.

---

## 5. State Machine Pattern

LangGraph implementa una Máquina de Estados.

```
Reasoning

↓

RAG

↓

Reasoning

↓

END
```

Cada nodo representa un estado del agente.

---

## 6. ReAct Pattern (Reason + Act)

El agente implementa el patrón ReAct.

```
Usuario

↓

Razonar

↓

Elegir herramienta

↓

Ejecutar herramienta

↓

Observar resultado

↓

Responder
```

Las herramientas pueden ser

* execute_query
* list_tables
* describe_table
* próximamente search_documents

---

## 7. Tool Pattern

Las capacidades del agente fueron encapsuladas como herramientas.

Ejemplos

```
ExecuteQueryTool

DescribeTableTool

ListTablesTool
```

El LLM decide cuál ejecutar.

---

# Principios SOLID utilizados

## S — Single Responsibility Principle

Cada clase tiene una única responsabilidad.

Ejemplos

```
OpenAIAdapter
```

Solo conversa con OpenAI.

```
AzureRAGRepository
```

Solo consulta Azure AI Search.

```
AzureMcpAdapter
```

Solo conversa con el servidor MCP.

```
AgentOrchestratorUseCase
```

Solo coordina el flujo del agente.

---

## O — Open/Closed Principle

El sistema está abierto a extenderse y cerrado a modificarse.

Por ejemplo

```
ILLMService
```

Hoy

```
OpenAIAdapter
```

Mañana

```
AnthropicAdapter
```

No hay que modificar el orquestador.

---

## L — Liskov Substitution Principle

Cualquier implementación puede sustituir a otra.

```
ILLMService

↓

OpenAIAdapter
```

o

```
ILLMService

↓

AzureOpenAIAdapter
```

Lo mismo ocurre con

```
IRagRepository

IMcpToolClient
```

---

## I — Interface Segregation Principle

Cada interfaz tiene una responsabilidad específica.

```
ILLMService
```

No conoce RAG.

```
IRagRepository
```

No conoce OpenAI.

```
IMcpToolClient
```

No conoce Azure Search.

---

## D — Dependency Inversion Principle

El dominio depende de abstracciones.

Nunca depende de

```
ChatOpenAI

SearchClient

ClientSession
```

Depende únicamente de

```
ILLMService

IRagRepository

IMcpToolClient
```

---

# Arquitectura del Agente

Finalmente el flujo quedó así

```
                Usuario
                    │
                    ▼
          AgentOrchestratorUseCase
                    │
                    ▼
             LangGraph Workflow
                    │
                    ▼
            reasoning_node
                    │
                    ▼
         LangChain create_agent()
                    │
     ┌──────────────┼─────────────────┐
     │              │                 │
     ▼              ▼                 ▼
 execute_query  list_tables   describe_table
     │
     ▼
 Servidor MCP (Azure)
     │
     ▼
 SQL Server
```

Y próximamente evolucionará a:

```
                Usuario
                    │
                    ▼
            create_agent()
                    │
     ┌──────────────┼────────────────────┐
     │              │                    │
     ▼              ▼                    ▼
 execute_query  describe_table   search_documents
                                       │
                                       ▼
                               Azure AI Search
```

En ese punto el agente decidirá de forma autónoma si debe consultar la base de datos SQL, buscar información en el índice RAG o combinar ambas fuentes en una misma respuesta, sin necesidad de reglas manuales basadas en palabras clave. Ese diseño representa una arquitectura de agentes moderna, desacoplada y fácilmente extensible.
