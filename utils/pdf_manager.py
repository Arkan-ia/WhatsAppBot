
import io
from typing import Any, Dict, List
import PyPDF2
from openai import OpenAI
import requests


class PDFManager:
    def __init__(self, pdf_url: str):
        self.pdf_url = pdf_url
        self.content = self._extract_pdf_content()
        self.indexed_content = self._index_content()
        self.client = OpenAI()

    def _extract_pdf_content(self) -> str:
        response = requests.get(self.pdf_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download PDF. Status code: {response.status_code}")
        
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        return ' '.join(page.extract_text() for page in reader.pages)

    def _index_content(self) -> List[Dict[str, Any]]:
        sections = self.content.split('\n\n')
        indexed_content = [{"text": section, "embedding": self._get_embedding(section)} for section in sections]
        return indexed_content

    def _get_embedding(self, text: str) -> List[float]:
        response = OpenAI().embeddings.create(input=text, model="text-embedding-ada-002")
        return response.data[0].embedding
    
    def retrieve_relevant_sections(self, query: str) -> List[str]:
        query_embedding = self._get_embedding(query)
        similarities = [(self._cosine_similarity(query_embedding, section['embedding']), section['text']) for section in self.indexed_content]
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [text for _, text in similarities[:3]]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = sum(a * a for a in vec1) ** 0.5
        norm_b = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm_a * norm_b)