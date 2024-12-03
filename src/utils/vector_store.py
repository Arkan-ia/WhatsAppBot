import io
from typing import Optional
import PyPDF2
import requests
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

class VectorStoreCreator:
    @staticmethod
    def create_from_pdf(pdf_url: str, save_path: str, openai_api_key: str) -> None:
        try:
            # Extraer contenido del PDF
            content = VectorStoreCreator._extract_pdf_content(pdf_url)
            
            # Crear y guardar la base de datos vectorial
            vectorstore = VectorStoreCreator._create_vectorstore(content, openai_api_key)
            vectorstore.save_local(save_path)
            
        except Exception as e:
            logging.error(f"Error creating vector store: {str(e)}")
            raise

    @staticmethod
    def _extract_pdf_content(pdf_url: str) -> str:
        # El mismo método que tenías antes
        try:
            response = requests.get(pdf_url)
            if response.status_code != 200:
                raise Exception(f"Failed to download PDF. Status code: {response.status_code}")
            
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            return ' '.join(page.extract_text() for page in reader.pages)
        except requests.RequestException as e:
            logging.error(f"Error downloading PDF from {pdf_url}: {str(e)}")
            raise
        except PyPDF2.PdfReadError as e:
            logging.error(f"Error reading PDF content: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error extracting PDF content: {str(e)}")
            raise

    @staticmethod
    def _create_vectorstore(content: str, openai_api_key: str) -> FAISS:
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(content)
            
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            return FAISS.from_texts(chunks, embeddings)
        except Exception as e:
            logging.error(f"Error creating vectorstore: {str(e)}")
            raise


