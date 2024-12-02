
import io
from typing import Any, Dict, List
import PyPDF2
from openai import OpenAI
import requests
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings


class PDFManager:
    def __init__(self, pdf_url: str):
        try:
            self.pdf_url = pdf_url
            self.content = self._extract_pdf_content()
            self.vectorstore = self._create_vectorstore()
            self.client = OpenAI()
        except Exception as e:
            logging.error(f"Error initializing PDFManager: {str(e)}")
            raise

    def _extract_pdf_content(self) -> str:
        try:
            response = requests.get(self.pdf_url)
            if response.status_code != 200:
                raise Exception(f"Failed to download PDF. Status code: {response.status_code}")
            
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            return ' '.join(page.extract_text() for page in reader.pages)
        except requests.RequestException as e:
            logging.error(f"Error downloading PDF from {self.pdf_url}: {str(e)}")
            raise
        except PyPDF2.PdfReadError as e:
            logging.error(f"Error reading PDF content: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error extracting PDF content: {str(e)}")
            raise

    def _create_vectorstore(self):
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(self.content)
            
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_texts(chunks, embeddings)
            
            return vectorstore
        except Exception as e:
            logging.error(f"Error creating vectorstore: {str(e)}")
            raise
    
    def retrieve_relevant_sections(self, query: str) -> List[str]:
        try:
            docs = self.vectorstore.similarity_search(query, k=3)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logging.error(f"Error retrieving relevant sections: {str(e)}")
            raise