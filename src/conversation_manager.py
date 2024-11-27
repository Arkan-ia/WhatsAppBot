import json
import logging
from typing import Any, Dict, List, Optional

from models.chatbot import ChatbotModel
from src.data_management import get_user_data
import src.prompts as prompts
from openai import OpenAI
from utils.pdf_manager import PDFManager
from src.whatsapp_api_handler import WhatsAppAPIHandler

client = OpenAI()

class ConversationManager:
    def __init__(self, whatsapp_api_handler: WhatsAppAPIHandler, pdf_manager: PDFManager, chatbot: ChatbotModel):
        self.whatsapp_api_handler = whatsapp_api_handler
        self.MODEL = 'gpt-4o-mini'
        self.pdf_manager = pdf_manager
        self.estados_conversacion = {}
        self.chatbot = chatbot

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
            response = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3,
                temperature=0
            )
            response_text = response.choices[0].message.content.strip().lower()
            print(f"User message: '{user_message}'")
            print(f"GPT-4 response: '{response_text}'")
            is_requesting = response_text == 'true'
            return is_requesting
        except Exception as e:
            logging.exception(f"Error with OpenAI API during PDF request validation: {e}")
            return False

        # Conversation State Management Methods

    def update_conversation_state(self, number: str, state: str) -> None:
        """
        Update the conversation state for a user.

        Args:
            number (str): The user's phone number.
            state (str): The new conversation state.
        """
        self.estados_conversacion[number] = state
        logging.debug(f"Conversation state updated for {number}: {state}")

    def get_conversation_state(self, number: str) -> Optional[str]:
        """
        Get the current conversation state for a user.

        Args:
            number (str): The user's phone number.

        Returns:
            Optional[str]: The current conversation state.
        """
        return self.estados_conversacion.get(number)


    def handle_incoming_message(self, message: Dict[str, Any]):
        message_type = message["type"]
                
        text = self.whatsapp_api_handler.get_whatsapp_message(message)
        number = message['from']
        message_id = message.get('id', None)
        print(f"User message from {number}: {text}")

        mark_read = self.whatsapp_api_handler.mark_read_message(message_id)
        
        list_messages = []
        list_messages.append(mark_read)

        current_state = self.get_conversation_state(number)
        user_data = get_user_data(number)

        if message_type == "image":
            print("is image")
            print(message["image"])
            id = message["image"]["id"]
            image_url = self.whatsapp_api_handler.get_media(id)
            #image_url = upload_media_to_storage(image)
            response = self.answer_image("", image_url)
            print(response)

        elif self.is_requesting_pdf(text):
            self._send_menu_pdf(number)
            response = "Te he enviado nuestro menú en PDF. ¿Qué te gustaría saber sobre algún plato en particular?"
        else:
            relevant_sections = self.pdf_manager.retrieve_relevant_sections(text)
            response = self._generate_response_from_sections(text, relevant_sections, user_data)

        text_message = self.whatsapp_api_handler.text_message(number, response)
        list_messages.append(text_message)

        for item in list_messages:
            self.whatsapp_api_handler.send_whatsapp_message(item)
            print("Message sent.")

    def _send_menu_pdf(self, number: str):
        pdf_url = self.pdf_manager.pdf_url
        caption = 'Aquí está nuestro menú en PDF.'
        filename = 'Menu.pdf'
        document = self.whatsapp_api_handler.document_message(number, pdf_url, caption, filename)
        self.whatsapp_api_handler.send_whatsapp_message(document)
        print(f"Menu PDF sent to {number}")

    def _generate_response_from_sections(self, query: str, sections: List[str], user_data: Dict[str, Any]) -> str:
        context = " ".join(sections)
        prompt = f"Contexto: {context}\nPregunta: {query}\nRespuesta:"
        try:
            response = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": self.chatbot.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.exception(f"Error with OpenAI API: {e}")
            return "Lo siento, parece que hubo un problema en el sistema. Por favor, escribe tu mensaje de nuevo."
    
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
            response = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.0
            )
            response_text = response.choices[0].message.content.strip()
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
        try:
            response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise e
