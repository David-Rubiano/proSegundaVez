import os
from azure.storage.blob import BlobServiceClient
from typing import List

class AzureBlobStorageAdapter:
    """
    Adaptador de Infraestructura para interactuar con Azure Blob Storage.
    Maneja la subida y descarga de los archivos PDF crudos.
    """
    
    def __init__(self):
        # La cadena de conexión la sacas del portal de Azure (Security -> Access keys)
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documentos-rag")
        
        if not self.connection_string:
            raise ValueError("Falta la variable de entorno AZURE_STORAGE_CONNECTION_STRING")
            
        # Inicializamos el cliente principal
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        
        # Nos aseguramos de que el contenedor (carpeta) exista, si no, lo creamos
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        if not self.container_client.exists():
            self.container_client.create_container()

    def upload_pdf(self, file_path: str, blob_name: str) -> str:
        """
        Sube un archivo PDF local hacia Azure Blob Storage.
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        print(f"✅ Archivo '{blob_name}' subido con éxito a Blob Storage.")
        return blob_client.url

    def download_pdf_content(self, blob_name: str) -> bytes:
        """
        Descarga el contenido de un PDF directamente a la memoria (bytes) 
        para que nuestro script pueda extraerle el texto más adelante.
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        return blob_client.download_blob().readall()