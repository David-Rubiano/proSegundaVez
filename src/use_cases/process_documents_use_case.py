import io
import os
import sys
import uuid
from typing import List
import hashlib
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.core.exceptions import ResourceNotFoundError
from openai import OpenAI

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

# Importamos nuestro adaptador de Blob Storage que construimos antes
from src.infrastructure.blob_storage_adapter import AzureBlobStorageAdapter

class ProcessDocumentsUseCase:
    """
    Caso de Uso: Orquestador ETL para procesar PDFs desde Blob Storage 
    hacia Azure AI Search con Embeddings de OpenAI.
    """
    
    def __init__(self, blob_adapter: AzureBlobStorageAdapter):
        # Inyección de Dependencias: Recibimos el adaptador externo
        self.blob_adapter = blob_adapter
        
        # Inicializamos los clientes directos que necesitamos para la carga
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        # Cliente de escritura para Azure AI Search
        self.search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
        )

        # Configuramos el cortador de texto (Chunking)
        # 1000 caracteres por pedazo, con 150 caracteres de memoria (solapamiento)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def document_exists(self, document_id: str) -> bool:
        """
        Verifica si un documento ya existe en Azure AI Search.
        """
        try:
            self.search_client.get_document(key=document_id)
            return True
        except ResourceNotFoundError:
            return False
        except Exception as e:
            print(f"⚠️ Error verificando documento '{document_id}': {e}")
            return False

    def execute(self, blob_name: str):
        """
        Ejecuta el flujo completo de ETL para un documento específico.
        """
        print(f"📥 1. Descargando '{blob_name}' desde Azure Blob Storage...")
        pdf_bytes = self.blob_adapter.download_pdf_content(blob_name)
        
        print("📄 2. Extrayendo texto del PDF...")
        # Usamos io.BytesIO para leer el archivo desde la RAM, sin guardarlo en disco
        reader = PdfReader(io.BytesIO(pdf_bytes))
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
            
        print("✂️ 3. Cortando el texto en chunks (fragmentos)...")
        chunks = self.text_splitter.split_text(full_text)
        print(f"   -> Se generaron {len(chunks)} fragmentos.")
        
        print("🧠 4. Generando Embeddings y formateando para Azure (con IDs Deterministas)...")
        documents_to_upload = []

        # Contadores para el resumen final
        processed = 0
        skipped = 0

        for i, chunk in enumerate(chunks):
            # 1. Creamos una cadena única basada en el nombre del archivo y el número de chunk
            raw_id = f"{blob_name}_chunk_{i}"

            # 2. Convertimos esa cadena en un Hash MD5 (siempre será el mismo para ese archivo y chunk)
            deterministic_id = hashlib.md5(raw_id.encode('utf-8')).hexdigest()

            # Opcional pero recomendado: Evitar llamar a OpenAI si no es necesario
            # En un sistema super avanzado, aquí consultaríamos a Azure si 'deterministic_id'
            # ya existe antes de gastar en la API de OpenAI. Por ahora, aseguramos no duplicar.

            # Verificamos si el chunk ya existe en Azure AI Search
            if self.document_exists(deterministic_id):
                print(f"⏩ Chunk {i+1} ya existe. Se omite.")
                skipped += 1
                continue

            response = self.openai_client.embeddings.create(
                input=chunk,
                model=self.embedding_model
            )

            embedding_vector = response.data[0].embedding

            doc_azure = {
                "id": deterministic_id,  # ✅ Usamos el ID determinista
                "content": chunk,
                "metadata": f"archivo: {blob_name}, chunk: {i+1}",
                "content_vector": embedding_vector
            }

            documents_to_upload.append(doc_azure)
            processed += 1

        print("☁️ 5. Subiendo fragmentos vectorizados a Azure AI Search...")

        # Azure nos permite subir los fragmentos en lotes (batches)
        if documents_to_upload:
            result = self.search_client.upload_documents(documents=documents_to_upload)

            successful = sum(r.succeeded for r in result)

            print(f"✅ {successful} nuevos fragmentos cargados.")
        else:
            print("ℹ️ Todos los fragmentos ya existían en Azure AI Search.")

        print("\n📊 Resumen")
        print(f"   Total de fragmentos : {len(chunks)}")
        print(f"   Nuevos              : {processed}")
        print(f"   Omitidos            : {skipped}")

        print(f"✅ ¡Proceso completado exitosamente para {blob_name}!")