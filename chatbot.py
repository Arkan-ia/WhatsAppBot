# chatbot.py
import time
import logging
import os
import openai
from whatsappbot import WhatsAppBot
import prompts
import PyPDF2
import requests
import io
import random
from typing import Dict, Any, List


MODEL = 'gpt-4o-mini'
NAME = 'Brayan'
COMPANY = 'La Rejana Callejera'
LOCATION = 'Pasto - Boyacá - Colombia'
TEMA = 'Restaurante - Comida'

bot = WhatsAppBot(
    api_url=os.getenv('WHATSAPP_URL'),
    token=os.getenv('WHATSAPP_TOKEN')
)

class PDFManager:
    def __init__(self, pdf_url: str):
        self.pdf_url = pdf_url
        self.content = self._extract_pdf_content()
        self.indexed_content = self._index_content()

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
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return response['data'][0]['embedding']

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

class ConversationManager:
    def __init__(self, bot: WhatsAppBot, pdf_manager: PDFManager):
        self.bot = bot
        self.pdf_manager = pdf_manager
        self.boyaco_expressions = [
            "qué más, pues?",
            "cómo le va?",
            "hágale, pues.",
            "qué se cuenta?",
            "eso es",
            "de una",
            "listo, pues",
            "claro, mijo",
            "a la orden",
            "con gusto"
        ]

    def handle_incoming_message(self, message: Dict[str, Any]):
        text = self.bot.get_whatsapp_message(message)
        number = message['from']
        message_id = message.get('id', None)
        logging.info(f"User message from {number}: {text}")

        list_messages = []
        mark_read = self.bot.mark_read_message(message_id)
        list_messages.append(mark_read)

        current_state = self.bot.get_conversation_state(number)
        user_data = self.bot.get_user_data(number)

        if self.bot.is_requesting_pdf(text):
            self._send_menu_pdf(number)
            response = "Te he enviado nuestro menú en PDF. ¿Qué te gustaría saber sobre algún plato en particular?"
        else:
            relevant_sections = self.pdf_manager.retrieve_relevant_sections(text)
            response = self._generate_response_from_sections(text, relevant_sections, user_data)

        text_message = self.bot.text_message(number, response)
        list_messages.append(text_message)

        for item in list_messages:
            self.bot.send_whatsapp_message(item)
            logging.info("Message sent.")

    def _send_menu_pdf(self, number: str):
        pdf_url = os.getenv('DOCUMENT_URL')
        caption = 'Aquí está nuestro menú en PDF.'
        filename = 'Menu.pdf'
        document = self.bot.document_message(number, pdf_url, caption, filename)
        self.bot.send_whatsapp_message(document)
        logging.info(f"Menu PDF sent to {number}")

    def _generate_response_from_sections(self, query: str, sections: List[str], user_data: Dict[str, Any]) -> str:
        context = " ".join(sections)
        prompt = f"Contexto: {context}\nPregunta: {query}\nRespuesta:"
        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(user_data)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            logging.exception(f"Error with OpenAI API: {e}")
            return "Lo siento, parece que hubo un problema en el sistema. Por favor, escribe tu mensaje de nuevo."

    def _get_system_prompt(self, user_data: Dict[str, Any]) -> str:
        expression = random.choice(self.boyaco_expressions)
        return (
            f"Eres {NAME}, un asistente de {COMPANY} que interactúa con los usuarios de manera informal, amigable y directa. "
            f"Eres de nacionalidad de {LOCATION}, así que heredas sus costumbres y formas de hablar. "
            "Tus respuestas son breves y van al grano. "
            f"Usa expresiones típicas de un boyaco, como '{expression}'. "
            "Al hacer preguntas, NO usas el signo de interrogación al inicio y evitas ser demasiado extenso. Por ejemplo: hola, cómo estás?; cómo te llamas?; "
            "Haces la conversación fluida sin ser formal, y siempre mantienes un tono amigable y directo. "
            f"NO uses signos de admiración/exclamación, que son poco comunes en mensajes de WhatsApp en {LOCATION}. "
            "Si el usuario te pregunta si eres una IA o intenta cambiar el tema a algo que no sea sobre el restaurante, redirige educadamente la conversación de vuelta al menú o servicios que ofrecemos. "
            "No admitas ser una IA, simplemente enfócate en ayudar al usuario con lo que necesite relacionado al restaurante. "
            "Tu conocimiento se limita únicamente a información sobre el restaurante, su menú, servicios y ubicación. "
            f"Restricciones: {prompts.RESTRICTIONS}"
            "Información del menú: " + self.pdf_manager.content + " "
        )

# Initialize the PDFManager and ConversationManager
pdf_manager = PDFManager("https://cdn.glitch.global/1e6c16f0-cf67-4f9c-b4af-433d3336cf2f/Menu.pdf?v=1729527777028")
conversation_manager = ConversationManager(bot, pdf_manager)

# In your main loop or webhook handler:
def handle_incoming_message(message):
    conversation_manager.handle_incoming_message(message)
