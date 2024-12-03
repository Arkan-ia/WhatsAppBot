from src.utils.vector_store import VectorStoreCreator

def create_vector_store(pdf_url: str, save_path: str, openai_api_key: str):
    """
    Crea un vector store a partir de un PDF.
    
    Args:
        pdf_url (str): URL del archivo PDF
        save_path (str): Ruta donde se guardará el vector store
        openai_api_key (str): API key de OpenAI
    """
    try:
        VectorStoreCreator.create_from_pdf(
            pdf_url=pdf_url,
            save_path=save_path,
            openai_api_key=openai_api_key
        )
        print(f"Vector store creado exitosamente en {save_path}")
    except Exception as e:
        print(f"Error al crear vector store: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Uso: python create_vector_store.py <pdf_url> <save_path> <openai_api_key>")
        sys.exit(1)
        
    pdf_url = sys.argv[1]
    save_path = sys.argv[2] 
    openai_api_key = sys.argv[3]
    
    create_vector_store(pdf_url, save_path, openai_api_key)