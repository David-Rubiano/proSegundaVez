import os
import sys
from dotenv import load_dotenv

# Cargamos variables de entorno antes de importar las clases
load_dotenv()

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

#print(f"Raíz del proyecto: {raiz_proyecto}")

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

from src.infrastructure.blob_storage_adapter import AzureBlobStorageAdapter
from src.use_cases.process_documents_use_case import ProcessDocumentsUseCase


def probar_ingesta_pdf():
    print("🚀 Iniciando prueba manual de Ingesta (ETL)...")

    # 1. Definimos el nombre del archivo local y cómo se llamará en la nube
    ruta_pdf_local = "documents/empleosAI.pdf"
    nombre_blob = "empleosAI.pdf"

    # Verificamos de forma segura que el archivo exista localmente
    if not os.path.exists(ruta_pdf_local):
        print(f"❌ Error: No se encontró el archivo '{ruta_pdf_local}' en tu computadora.")
        print("Por favor, coloca un archivo PDF en la raíz del proyecto con ese nombre.")
        return

    try:
        # 2. Instanciamos el adaptador de infraestructura (Nuestras "manos")
        print("\n🔌 Conectando con Azure Blob Storage...")
        blob_adapter = AzureBlobStorageAdapter()

        # 3. Subimos el PDF local a la nube (Simulando lo que haría un usuario)
        print(f"\n📤 Verificando si '{nombre_blob}' existe en Blob Storage...")

        blob_client = blob_adapter.container_client.get_blob_client(nombre_blob)

        if blob_client.exists():
            print("ℹ️ El archivo ya existe en Blob Storage. Se omite la subida.")
        else:
            print(f"📤 Subiendo '{ruta_pdf_local}' a Blob Storage...")
            blob_adapter.upload_pdf(file_path=ruta_pdf_local, blob_name=nombre_blob)

        # 4. Inyección de Dependencias: Instanciamos el Caso de Uso pasándole el adaptador
        print("\n⚙️ Inicializando el orquestador ETL...")
        etl_use_case = ProcessDocumentsUseCase(blob_adapter=blob_adapter)

        # 5. Ejecutamos el flujo de extracción, chunking, vectorización y carga
        print("\n🧠 Ejecutando procesamiento y vectorización (OpenAI + Azure AI Search)...")
        etl_use_case.execute(blob_name=nombre_blob)

        print("\n🎉 ¡Prueba de ingesta completada con éxito! Tus datos ya viven en la base vectorial.")

    except Exception as e:
        print(f"\n❌ Error de infraestructura durante la prueba: {e}")


if __name__ == "__main__":
    probar_ingesta_pdf()