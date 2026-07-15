import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    HnswParameters,
    VectorSearchAlgorithmMetric,
)

def create_rag_search_index(endpoint: str, admin_key: str, index_name: str):
    """
    Crea el índice en Azure AI Search optimizado para búsquedas híbridas (Texto + Vectorial).
    """
    credential = AzureKeyCredential(admin_key)
    client = SearchIndexClient(endpoint=endpoint, credential=credential)
    
    # 1. Configurar la Búsqueda Vectorial
    # Usamos HNSW (Hierarchical Navigable Small World) que es el estándar rápido para búsqueda vectorial.
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="my-hnsw-config",
                parameters=HnswParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE  # Compara la dirección de los vectores
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="my-vector-profile",
                algorithm_configuration_name="my-hnsw-config"
            )
        ]
    )
    
    # 2. Definir los campos (el Esquema del Índice)
    fields = [
        # id es la llave primaria (Key) obligatoria.
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        
        # content guarda el texto del chunk. Ponemos es.microsoft para soporte óptimo en español.
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="es.microsoft"),
        
        # metadata guarda información útil de rastreo (origen del pdf, página, etc.)
        SimpleField(name="metadata", type=SearchFieldDataType.String, retrievable=True),
        
        # content_vector guarda la representación vectorial de 1536 dimensiones de OpenAI.
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,  # Tamaño de salida de text-embedding-3-small
            vector_search_profile_name="my-vector-profile"
        )
    ]
    
    # 3. Empaquetar todo e invocar el servicio de Azure
    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
    
    try:
        client.create_or_update_index(index)
        print(f"✅ Índice '{index_name}' creado/actualizado con éxito en Azure AI Search.")
    except Exception as e:
        print(f"❌ Error creando el índice: {e}")




load_dotenv()

if __name__ == "__main__":
    create_rag_search_index(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        admin_key=os.getenv("AZURE_SEARCH_API_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME")
    )