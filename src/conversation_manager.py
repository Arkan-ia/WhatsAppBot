
import logging
import os
import random
from typing import Any, Dict, List

import prompts

import openai
from utils.pdf_manager import PDFManager
from src.whatsappbot import WhatsAppBot

MODEL = 'gpt-4o-mini'
NAME = 'Brayan'
COMPANY = 'La Rejana Callejera'
LOCATION = 'Pasto - Boyacá - Colombia'
TEMA = 'Restaurante - Comida'

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