from src.common.utils.vector_store_creator import VectorStoreCreator

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print(
            "Uso: python create_vector_store.py <pdf_url> <save_path> <openai_api_key>"
        )
        sys.exit(1)

    pdf_url = sys.argv[1]
    save_path = sys.argv[2]
    openai_api_key = sys.argv[3]

    VectorStoreCreator.create_from_pdf(
        pdf_url=pdf_url, save_path=save_path, openai_api_key=openai_api_key
    )
