import os
import sys
from dotenv import load_dotenv

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.infrastructure.blob_storage_adapter import AzureBlobStorageAdapter

load_dotenv()

adapter = AzureBlobStorageAdapter()

# Subimos un archivo PDF de prueba a Azure Blob Storage

url = adapter.upload_pdf(
    file_path="documents/empleosAI.pdf",
    blob_name="empleosAI.pdf"
)

print(url)