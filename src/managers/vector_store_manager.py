from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from openai import OpenAI
import logging

class VectorStoreManager:
    def __init__(self, faiss_index_path: str):
        try:
            # Ahora cargamos una base de datos FAISS existente en lugar de crearla
            self.vectorstore = FAISS.load_local(faiss_index_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
            self.client = OpenAI()
        except Exception as e:
            logging.error(f"Error initializing VectorStoreManager: {str(e)}")
            raise

    def retrieve_relevant_sections(self, query: str) -> List[str]:
        try:
            docs = self.vectorstore.similarity_search(query, k=10)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logging.error(f"Error retrieving relevant sections: {str(e)}")
            raise