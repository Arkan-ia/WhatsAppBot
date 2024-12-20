import json
import logging
from typing import Any, Dict, List, Optional

from src.db.firebase import add_chat_message, add_contact_message, get_conversation
from src.models.chatbot import ChatbotModel
from openai import OpenAI
from src.models.message import ChatMessage
from src.utils.open_ai_tools import get_notify_payment_mail_tool, get_store_user_data_tool, notify_payment_mail, store_user_data
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

            self._register_message(number, text, message_id)
            self._handle_conversation_state(number)
            user_data = {}

            # Procesar mensaje y generar respuesta
            response = self._process_message_by_type(message_type, text, message, user_data)
            print("response: ", response)

            # Manejar llamadas a funciones y registrarlas
            if response.tool_calls:
                self._handle_tool_calls(response, number)
                # Generar una nueva respuesta después de ejecutar las funciones
                response = self._generate_follow_up_response(number)

            # Enviar respuesta final
            self._send_response(number, response.content.strip())

        except Exception as e:
            logging.exception("Error al procesar mensaje entrante: %s", str(e))
            raise

    def _handle_tool_calls(self, response, number):
        """Maneja y registra las llamadas a funciones"""
        conversation_id = f"{self.whatsapp_api_handler.from_whatsapp_id}_{number}"
        
        for tool_call in response.tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Registrar la llamada a la función en el historial
            add_chat_message(
                self.whatsapp_api_handler.from_whatsapp_id,
                number,
                f"FUNCTION_CALL: {function_name}",
                is_function_call=True
            )

            # Ejecutar la función
            if function_name == "notify_payment_mail":
                notify_payment_mail(to="lozanojohan321@gmail.com")
            elif function_name == "store_user_data":
                store_user_data(self.whatsapp_api_handler.from_whatsapp_id, number, args)

    def _generate_follow_up_response(self, number: str):
        """Genera una respuesta de seguimiento después de ejecutar funciones"""
        messages = get_conversation(self.whatsapp_api_handler.from_whatsapp_id, number)
        messages = [ChatMessage(**x.to_dict()).to_dict() for x in messages]
        
        system_prompt = (
            f"{self.chatbot.system_prompt}\n"
            "Las funciones necesarias ya han sido ejecutadas. "
            "Por favor, continúa la conversación normalmente."
        )

        response = client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            max_tokens=150,
            temperature=0.1,
        )

        return response.choices[0].message

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
    ):
        """Procesa el mensaje según su tipo y genera una respuesta"""
        if message_type == "image":
            return self._handle_image_message(message)
        else:
            return self._handle_text_message(text, message["from"], user_data)

    def _handle_image_message(self, message: Dict[str, Any]):
        """Procesa mensajes de tipo imagen"""
        print("Processing image message")
        image_id = message["image"]["id"]
        image_url = self.whatsapp_api_handler.get_media(image_id)
        response = self.answer_image("", image_url)
        print(response)
        return response

    def _handle_text_message(self, text: str, number: str, user_data: Dict[str, Any]):
        """Procesa mensajes de texto"""
        
        print("Generating response from sections...")
        relevant_sections = self.chatbot.vectorstore.retrieve_relevant_sections(text)

        messages = get_conversation(self.whatsapp_api_handler.from_whatsapp_id, number)
        messages = [ChatMessage(**x.to_dict()).to_dict() for x in messages]

        return self._generate_response_from_sections(relevant_sections, user_data, messages)

    def _send_response(self, number: str, response: str) -> None:
        """Envía la respuesta al usuario"""
        self.chatbot.add_message("assistant", response)
        add_chat_message(self.whatsapp_api_handler.from_whatsapp_id, number, response)

        print("Sending response to WhatsApp...")
        text_message = self.whatsapp_api_handler.text_message(number, response)
        self.whatsapp_api_handler.send_whatsapp_message(text_message)
        print("Message sent.")

    
    def _generate_response_from_sections(
        self, sections: List[str], user_data: Dict[str, Any], messages: List[Dict[str, Any]]
    ):
        try:
            context = " ".join(sections)
            system_prompt = f"{self.chatbot.system_prompt}\nContexto relevante: {context}"

            try:
                print("current_messages: ", messages)

                response = client.chat.completions.create(
                    model=self.MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *messages
                    ],
                    tools=[get_store_user_data_tool(user_data), get_notify_payment_mail_tool()],
                    max_tokens=150,
                    temperature=0.1,
                )

                #print("system_prompt: ", system_prompt)

                response = response.choices[0].message
                return response
            
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
                tools=[get_store_user_data_tool(), get_notify_payment_mail_tool()],
                max_tokens=300,
            )
            return response.choices[0].message
        except Exception as e:
            logging.exception("Error al procesar imagen con OpenAI API: %s", str(e))
            return "Lo siento, no pude procesar la imagen correctamente. Por favor, intenta nuevamente."
