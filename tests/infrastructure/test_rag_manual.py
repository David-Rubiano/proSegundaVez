import os
import sys
from dotenv import load_dotenv

# Cargamos las variables de entorno ANTES de importar nada
load_dotenv()

raiz_proyecto = os.path.abspath(os.path.join(os.getcwd()))

if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

# Importamos tu adaptador de la capa de Infraestructura
from src.infrastructure.azure_rag_repository import AzureRAGRepository

def probar_rag_manualmente():
    print("Iniciando prueba manual de conexión a Azure RAG...")
    
    try:
        # 1. Instanciamos el adaptador
        rag_repo = AzureRAGRepository()
        print("✅ Adaptador RAG instanciado correctamente.")

        # 2. Definimos una pregunta de prueba
        pregunta_usuario = "¿Mejores empleos de IA en Colombia?"
        print(f"Buscando contexto para: '{pregunta_usuario}'")

        # 3. Llamamos al método que busca en Azure AI Search
        # limit=2 le dice que solo traiga los 2 fragmentos más relevantes
        resultados = rag_repo.retrieve(query=pregunta_usuario, limit=2)

        # 4. Evaluamos los resultados
        if not resultados:
            print("⚠️ No se encontraron resultados. Verifica si tu índice tiene datos o si la búsqueda falló.")
        else:
            print("\n✅ Documentos recuperados con éxito:")
            for i, fragmento in enumerate(resultados, 1):
                print(f"\n--- Resultado {i} ---")
                print(fragmento)
                
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    probar_rag_manualmente()