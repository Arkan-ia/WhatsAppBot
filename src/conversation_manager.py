import json
import logging
from typing import Any, Dict, List, Optional

from src.db.firebase import add_chat_message, add_contact_message, get_conversation
from src.models.chatbot import ChatbotModel
from src.data_management import get_user_data
from openai import OpenAI
from src.models.message import ChatMessage
from src.whatsapp_api_handler import WhatsAppAPIHandler

client = OpenAI()


class ConversationManager:
    def __init__(
        self,
        whatsapp_api_handler: WhatsAppAPIHandler,
        chatbot: ChatbotModel,
    ):
        try:
            self.whatsapp_api_handler = whatsapp_api_handler
            self.MODEL = "gpt-4o-mini"
            self.estados_conversacion = {}
            self.chatbot = chatbot
        except Exception as e:
            logging.exception("Error al inicializar ConversationManager: %s", str(e))
            raise

    def is_requesting_pdf(self, user_message: str) -> bool:
        """
        Determines if the user is requesting a PDF (menu, prices, catalog) using GPT-4.

        Args:
            user_message (str): The user's message.

        Returns:
            bool: True if the user is requesting a PDF, False otherwise.
        """
        try:
            system_prompt = (
                "Eres un asistente que determina si el usuario está solicitando explícitamente ver el menú o el PDF del menú. "
                "Responde solo con 'TRUE' o 'FALSE'. No agregues ningún texto adicional. "
                "Responde 'TRUE' solo si el usuario está pidiendo explícitamente ver el menú, la carta, los productos o el PDF del menú. "
                "Ejemplos de 'TRUE': 'Envíame el menú', 'Quiero ver el menú', 'Me puedes enviar el menú en PDF? que productos venden?'. "
                "Ejemplos de 'FALSE': '¿Qué ingredientes tiene la Montañera?', '¿Cuánto cuesta la hamburguesa clásica?'."
            )
            prompt = f"El usuario ha dicho: '{user_message}'.\n¿Está el usuario solicitando explícitamente información de los productos? Responde 'TRUE' o 'FALSE'."

            try:
                response = client.chat.completions.create(
                    model=self.MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=3,
                    temperature=0,
                )
                response_text = response.choices[0].message.content.strip().lower()
                print(f"User message: '{user_message}'")
                print(f"GPT-4 response: '{response_text}'")
                is_requesting = response_text == "true"
                return is_requesting
            except Exception as e:
                logging.exception(
                    f"Error al validar solicitud de PDF con OpenAI API: {e}"
                )
                return False

        except Exception as e:
            logging.exception("Error general en is_requesting_pdf: %s", str(e))
            return False

    def update_conversation_state(self, number: str, state: str) -> None:
        """
        Update the conversation state for a user.

        Args:
            number (str): The user's phone number.
            state (str): The new conversation state.
        """
        try:
            self.estados_conversacion[number] = state
            print(f"Conversation state updated for {number}: {state}")
        except Exception as e:
            logging.exception(
                "Error al actualizar el estado de la conversación: %s", str(e)
            )
            raise

    def get_conversation_state(self, number: str) -> Optional[str]:
        """
        Get the current conversation state for a user.

        Args:
            number (str): The user's phone number.

        Returns:
            Optional[str]: The current conversation state.
        """
        try:
            return self.estados_conversacion.get(number)
        except Exception as e:
            logging.exception(
                "Error al obtener el estado de la conversación: %s", str(e)
            )
            return None


    def manage_incoming_message(self, message: Dict[str, Any]):
        """
        Procesa y maneja los mensajes entrantes de WhatsApp.
        
        Args:
            message (Dict[str, Any]): El mensaje entrante con toda su información
        """
        print("Starting conversation manager processing...")
        try:
            # Extraer información básica del mensaje
            message_type = message["type"]
            text = self.whatsapp_api_handler.get_whatsapp_message(message)
            number = message["from"]
            message_id = message.get("id", None)
            print(f"User message from {number}: {text}")

            #current_messages = get_messages_for_openai(self.whatsapp_api_handler.from_whatsapp_id, number)
            #print("current_messages: ", current_messages)

            # Registrar mensaje y marcar como leído
            self._register_message(number, text, message_id)

            # Manejar estado de la conversación
            self._handle_conversation_state(number)

            # Obtener datos del usuario
            user_data = get_user_data(number)

            # Procesar mensaje según su tipo y generar respuesta
            response = self._process_message_by_type(message_type, text, message, user_data)

            # Enviar respuesta
            self._send_response(number, response)

        except Exception as e:
            logging.exception("Error al procesar mensaje entrante: %s", str(e))
            raise

    def _register_message(self, number: str, text: str, message_id: Optional[str]) -> None:
        """Registra el mensaje y lo marca como leído"""
        add_contact_message(self.whatsapp_api_handler.from_whatsapp_id, number, text)
        
        if message_id:
            mark_read_data = self.whatsapp_api_handler.mark_read_message(message_id)
            self.whatsapp_api_handler.send_whatsapp_message(mark_read_data)
            print("Message marked as read.")

    def _handle_conversation_state(self, number: str) -> None:
        """Maneja el estado de la conversación"""
        current_state = self.get_conversation_state(number)
        if not current_state:  # Primera interacción
            self.update_conversation_state(number, "initial")
        
        if current_state == "initial":
            self.update_conversation_state(number, "menu")

    def _process_message_by_type(
        self, 
        message_type: str, 
        text: str, 
        message: Dict[str, Any],
        user_data: Dict[str, Any]
    ) -> str:
        """Procesa el mensaje según su tipo y genera una respuesta"""
        if message_type == "image":
            return self._handle_image_message(message)
        else:
            return self._handle_text_message(text, message["from"], user_data)

    def _handle_image_message(self, message: Dict[str, Any]) -> str:
        """Procesa mensajes de tipo imagen"""
        print("Processing image message")
        image_id = message["image"]["id"]
        image_url = self.whatsapp_api_handler.get_media(image_id)
        response = self.answer_image("", image_url)
        print(response)
        return response

    def _handle_text_message(self, text: str, number: str, user_data: Dict[str, Any]) -> str:
        """Procesa mensajes de texto"""
        if self.is_requesting_pdf(text):
            self.chatbot.add_message("user", text)
            self._send_menu_pdf(number)
            return "Te he enviado nuestro menú en PDF. ¿Qué te gustaría saber sobre algún plato en particular?"
        
        print("Generating response from sections...")
        relevant_sections = self.chatbot.vectorstore.retrieve_relevant_sections(text)

        messages = get_conversation(self.whatsapp_api_handler.from_whatsapp_id, number)
        messages = [ChatMessage(**x.to_dict()).to_dict() for x in messages]

        return self._generate_response_from_sections(text, relevant_sections, user_data, messages)

    def _send_response(self, number: str, response: str) -> None:
        """Envía la respuesta al usuario"""
        self.chatbot.add_message("assistant", response)
        add_chat_message(self.whatsapp_api_handler.from_whatsapp_id, number, response)

        print("Sending response to WhatsApp...")
        text_message = self.whatsapp_api_handler.text_message(number, response)
        self.whatsapp_api_handler.send_whatsapp_message(text_message)
        print("Message sent.")

    def _send_menu_pdf(self, number: str):
        try:
            pdf_url = self.chatbot.vectorstore.pdf_url
            caption = "Aquí está nuestro menú en PDF."
            filename = "Menu.pdf"
            document = self.whatsapp_api_handler.document_message(
                number, pdf_url, caption, filename
            )
            self.whatsapp_api_handler.send_whatsapp_message(document)
            print(f"Menu PDF sent to {number}")
        except Exception as e:
            logging.exception("Error al enviar el PDF del menú: %s", str(e))
            raise

    def _generate_response_from_sections(
        self, query: str, sections: List[str], user_data: Dict[str, Any], messages: List[Dict[str, Any]]
    ) -> str:
        try:
            context = " ".join(sections)
            # print("context: ", context)
            prompt = f"Contexto: {context}\nPregunta: {query}\nRespuesta:"

            # print("prompt: ", prompt)
            try:
                print("current_messages: ", messages)

                response = client.chat.completions.create(
                    model=self.MODEL,
                    messages=[{"role": "system", "content": self.chatbot.system_prompt}, *messages],
                    max_tokens=150,
                    temperature=0.1,
                )
                print("Chat history: ", self.chatbot.chat_history)

                print(
                    "Chat history after adding user message: ",
                    self.chatbot.chat_history,
                )

                return response.choices[0].message.content.strip()
            except Exception as e:
                logging.exception(f"Error con OpenAI API: {e}")
                return "Lo siento, parece que hubo un problema en el sistema. Por favor, escribe tu mensaje de nuevo."
        except Exception as e:
            logging.exception("Error al generar respuesta desde secciones: %s", str(e))
            return (
                "Lo siento, ocurrió un error inesperado. Por favor, intenta nuevamente."
            )

    def interpret_user_message(self, user_message: str) -> tuple:
        """
        Uses GPT-4 to interpret the user's message and determine their intent.
        Returns a tuple (intent, entity), where 'intent' can be 'affirmative', 'negative', 'provide_entity', or 'other'.
        If 'intent' is 'provide_entity', 'entity' will contain the name of the entity; otherwise, it will be None.
        """
        try:
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
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=100,
                    temperature=0.0,
                )
                response_text = response.choices[0].message.content.strip()
                print(f"Interpretation of user message: '{response_text}'")

                result = json.loads(response_text)
                intent = result.get("intent", "other")
                entity = result.get("entity", None)
                if entity == "null":
                    entity = None
                return intent, entity
            except Exception as e:
                logging.exception(
                    "Error al interpretar mensaje con OpenAI API: %s", str(e)
                )
                return "other", None
        except Exception as e:
            logging.exception(
                "Error general al interpretar mensaje de usuario: %s", str(e)
            )
            return "other", None

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
            logging.exception("Error al procesar imagen con OpenAI API: %s", str(e))
            return "Lo siento, no pude procesar la imagen correctamente. Por favor, intenta nuevamente."
