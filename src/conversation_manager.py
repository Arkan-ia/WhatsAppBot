
import json
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

    def is_requesting_pdf(self, user_message: str) -> bool:
        """
        Determines if the user is requesting a PDF (menu, prices, catalog) using GPT-4.

        Args:
            user_message (str): The user's message.

        Returns:
            bool: True if the user is requesting a PDF, False otherwise.
        """
        system_prompt = (
            "Eres un asistente que determina si el usuario está solicitando explícitamente ver el menú o el PDF del menú. "
            "Responde solo con 'TRUE' o 'FALSE'. No agregues ningún texto adicional. "
            "Responde 'TRUE' solo si el usuario está pidiendo explícitamente ver el menú, la carta, los productos o el PDF del menú. "
            "Ejemplos de 'TRUE': 'Envíame el menú', 'Quiero ver el menú', 'Me puedes enviar el menú en PDF?'. "
            "Ejemplos de 'FALSE': '¿Qué ingredientes tiene la Montañera?', '¿Cuánto cuesta la hamburguesa clásica?'."
        )
        prompt = f"El usuario ha dicho: '{user_message}'.\n¿Está el usuario solicitando explícitamente ver el menú o el PDF del menú? Responde 'TRUE' o 'FALSE'."

        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3,
                temperature=0
            )
            response_text = response['choices'][0]['message']['content'].strip().lower()
            logging.info(f"User message: '{user_message}'")
            logging.info(f"GPT-4 response: '{response_text}'")
            is_requesting = response_text == 'true'
            return is_requesting
        except Exception as e:
            logging.exception(f"Error with OpenAI API during PDF request validation: {e}")
            return False


    def handle_incoming_message(self, message: Dict[str, Any]):
        message_type = message["type"]
        
        if message_type == "image":
            id = message["image"]["id"]
            image = self.bot.get_media(id)
            self.answer_image("", image)
            
            
        text = self.bot.get_whatsapp_message(message)
        number = message['from']
        message_id = message.get('id', None)
        logging.info(f"User message from {number}: {text}")

        list_messages = []
        mark_read = self.bot.mark_read_message(message_id)
        list_messages.append(mark_read)

        current_state = self.bot.get_conversation_state(number)
        user_data = self.bot.get_user_data(number)

        if self.is_requesting_pdf(text):
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
    
    
    def interpret_user_message(self, user_message: str) -> tuple:
        """
        Uses GPT-4 to interpret the user's message and determine their intent.
        Returns a tuple (intent, entity), where 'intent' can be 'affirmative', 'negative', 'provide_entity', or 'other'.
        If 'intent' is 'provide_entity', 'entity' will contain the name of the entity; otherwise, it will be None.
        """
        system_prompt = (
            "Eres un asistente que interpreta mensajes de usuarios para determinar su intención. "
            "Las posibles intenciones son: 'affirmative' si el usuario está diciendo que sí o afirmando; "
            "'negative' si el usuario está diciendo que no o negando; "
            "'provide_entity' si el usuario está mencionando una nueva entidad que necesita; "
            "o 'other' si el mensaje no encaja en las anteriores. "
            "Responde únicamente con un JSON en el siguiente formato:\n"
            '{"intent": "intention", "entity": "entity_name_or_null"}\n'
            "Si la intención es 'provide_entity', incluye la 'entity' mencionada; de lo contrario, 'entity' debe ser null."
        )
        prompt = f"El usuario ha dicho: '{user_message}'.\nDetermina su intención y responde en el formato indicado."

        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.0
            )
            response_text = response['choices'][0]['message']['content'].strip()
            print(f"Interpretation of user message: '{response_text}'")  

            # Parse the JSON response
            result = json.loads(response_text)
            intent = result.get('intent', 'other')
            entity = result.get('entity', None)
            if entity == 'null':
                entity = None
            return intent, entity
        except Exception as e:
            print(f"Error interpreting user message: {e}")
            return 'other', None
    
    def answer_image(self, question, image_url):
        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                "type": "image_url",
                "image_url": {
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
        
        return response
