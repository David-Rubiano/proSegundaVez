# src/infrastructure/azure_rag_repository.py
import os
import sys
from typing import List
from openai import OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

#print(f"Raíz del proyecto: {raiz_proyecto}")

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.domain.ports import IRagRepository

class AzureRAGRepository(IRagRepository):
    def __init__(self):
        # 1. Cargamos las variables de entorno para Azure AI Search
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        
        # Validamos configuraciones básicas
        if not all([self.endpoint, self.index_name, self.api_key]):
            raise ValueError("Faltan variables de entorno para Azure AI Search")
        
        # Inicializamos el cliente de Azure AI Search
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.api_key)
        )
        
        # 2. Inicializamos el cliente oficial de OpenAI para generar los embeddings del usuario
        # Usaremos el modelo estándar y económico 'text-embedding-3-small'
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    def _generate_embedding(self, text: str) -> List[float]:
        """Convierte el texto de la consulta en un vector numérico (embedding)."""
        response = self.openai_client.embeddings.create(
            input=[text],
            model=self.embedding_model
        )
        return response.data[0].embedding

    def retrieve(self, query: str, limit: int = 3) -> List[str]:
        """
        Realiza una búsqueda híbrida (Vectorial + Palabras Clave) en Azure AI Search.
        """
        try:
            # Paso 1: Convertir la pregunta de texto en un vector numérico de 1536 dimensiones
            query_vector = self._generate_embedding(query)
            
            # Paso 2: Configurar la consulta vectorial indicando el campo vectorizado del índice
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=limit,
                fields="content_vector"  # Nombre del campo vector en tu índice de Azure
            )
            
            # Paso 3: Lanzar la consulta híbrida
            # - 'search_text' ejecuta la búsqueda tradicional por palabras clave.
            # - 'vector_queries' ejecuta la búsqueda por similitud semántica.
            results = self.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                select=["content"],  # Le pedimos que solo traiga el fragmento de texto legible
                top=limit
            )
            
            # Paso 4: Extraer y limpiar los resultados
            retrieved_chunks = []
            for doc in results:
                content = doc.get("content")
                if content:
                    retrieved_chunks.append(content)
                    
            return retrieved_chunks

        except Exception as e:
            # En un entorno real empresarial, aquí usaríamos un logger estructurado
            print(f"[Error AzureRAGRepository] No se pudo recuperar información: {str(e)}")
            return []