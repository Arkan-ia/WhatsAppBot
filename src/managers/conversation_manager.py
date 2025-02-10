from src.common.utils.google_tasks import create_task, delete_task
import json
import logging
from typing import Any, Dict, Optional
import firebase_admin.firestore
from google.api_core.exceptions import NotFound

from src.common.utils.openai_utils import get_media_from_id, get_text_from_audio
from src.common.utils.whatsapp_utils import get_whatsapp_message, send_whatsapp_message
from src.common.whatsapp.models.models import MarkReadMessage, TextMessage

from src.domain.message.port.message_repository import MessageRepository
from src.domain.conversation.port.conversation_repository import ConversationRepository
from src.domain.lead.port.lead_repository import LeadRepository
from src.services.chat_service import ChatbotService


class ConversationManager:
    def __init__(self, from_whatsapp_id: str, token: str, chatbot: ChatbotService):
        self.chatbot = chatbot
        self.from_whatsapp_id = from_whatsapp_id
        self.token = token
        self.message_repository = MessageRepository()
        self.lead_repository = LeadRepository()
        self.conversation_repository = ConversationRepository()

    def manage_incoming_message(self, message: Dict[str, Any]):
        """
        Procesa y maneja los mensajes entrantes de WhatsApp.

        Args:
            message (Dict[str, Any]): El mensaje entrante con toda su información
        """
        try:
            print(f"Mensaje recibido {message}")
            self._handle_contact_and_conversation(message)
            self._handle_task(message)
            self._handle_message_response(message)
        except Exception as e:
            logging.exception("Error al procesar mensaje entrante: %s", str(e))
            raise

    def _handle_contact_and_conversation(self, message: Dict[str, Any]):
        self.contact_ref = self.lead_repository.get_or_create_contact(
            message["from"], self.from_whatsapp_id
        )
        self.conversation_ref = self.conversation_repository.get_or_create_conversation(
            self.contact_ref
        )
        self.message_repository.create_contact_message(
            conversation_ref=self.conversation_ref,
            contact_ref=self.contact_ref,
            phone_number=message["from"],
            message=get_whatsapp_message(message),
            ws_id=self.from_whatsapp_id,
            wa_id=message["id"],
        )

    def _handle_task(self, message: Dict[str, Any]):
        contact_snapshot = self.contact_ref.get()
        current_task = contact_snapshot.to_dict().get("task", None)

        if current_task:
            try:
                delete_task(current_task)
            except NotFound:
                pass

        answer_later_task = create_task(
            "https://us-central1-innate-tempo-448214-e5.cloudfunctions.net/main/send-message",
            json.dumps(
                {
                    "to_number": message["from"],
                    "from_id": self.from_whatsapp_id,
                    "token": self.token,
                    # Crear nuevo endpoint para esto
                    "message": "Hola, aún te interesan los productos?",  # generate answer
                }
            ),
        )

        self.contact_ref.update({"task": answer_later_task})

    def _handle_message_response(self, message: Dict[str, Any]):
        self.mark_read_message(message.get("id", None))
        self.handle_message_type(message)

        response = self.chatbot.answer_conversation(
            self.from_whatsapp_id, message["from"]
        )

        text_message = TextMessage(message["from"], response.content)
        api_response = send_whatsapp_message(
            self.from_whatsapp_id, self.token, text_message
        )

        self.message_repository.create_chat_message(
            conversation_ref=self.conversation_ref,
            contact_ref=self.contact_ref,
            phone_number=message["from"],
            message=response.content,
            ws_id=self.from_whatsapp_id,
            wa_id=api_response["body"]["messages"][0]["id"],
        )

        self.lead_repository.update_last_message(self.contact_ref, response.content)

    def mark_read_message(self, message_id: Optional[str]) -> None:
        """Marca como leído un mensaje"""

        if message_id:
            mark_read_data = MarkReadMessage(message_id)
            send_whatsapp_message(
                from_whatsapp_id=self.from_whatsapp_id,
                token=self.token,
                message=mark_read_data,
            )

    def handle_message_type(self, message):
        """Procesa el mensaje según su tipo y genera una respuesta"""

        if message["type"] == "image":
            image_url = get_media_from_id(message["image"]["id"], self.token)
            # TODO: Get text from message
            question = ""  # message[]
            response = self.chatbot.generate_answer_from_image(question, image_url)

        elif message["type"] == "audio":
            media_id = message["audio"]["id"]
            question = get_text_from_audio(media_id, self.token)

        else:  # Question is just text
            question = get_whatsapp_message(message)
            response = self.chatbot.answer_conversation(
                self.from_whatsapp_id, message["from"]
            )

        self.handle_tool_calls(response, message["from"])

    def execute_tool(self, tool_call, options, number):
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        logging.info(f"Argumens: {args}")
        response = options[function_name](args)

        self.message_repository.create_tool_message(
            conversation_ref=self.conversation_ref,
            ws_id=self.from_whatsapp_id,
            phone_number=number,
            message=response,
            tool_call_id=tool_call.id,
            function_name=tool_call.function.name,
            function_response=response,
            contact_ref=self.contact_ref,
        )

    def mark_read_message(self, message_id: Optional[str]) -> None:
        """Marca como leído un mensaje"""

        if message_id:
            mark_read_data = MarkReadMessage(message_id)
            send_whatsapp_message(
                from_whatsapp_id=self.from_whatsapp_id,
                token=self.token,
                message=mark_read_data,
            )

    def handle_message_type(self, message):
        """Procesa el mensaje según su tipo y genera una respuesta"""

        if message["type"] == "image":
            image_url = get_media_from_id(message["image"]["id"], self.token)
            # TODO: Get text from message
            question = ""  # message[]
            response = self.chatbot.generate_answer_from_image(question, image_url)

        elif message["type"] == "audio":
            media_id = message["audio"]["id"]
            question = get_text_from_audio(media_id, self.token)

        else:  # Question is just text
            question = get_whatsapp_message(message)
            response = self.chatbot.answer_conversation(
                self.from_whatsapp_id, message["from"]
            )

        self.handle_tool_calls(response, message["from"])

    def execute_tool(self, tool_call, options, number):
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        logging.info(f"Argumens: {args}")
        response = options[function_name](args)

        self.message_repository.create_tool_message(
            conversation_ref=self.conversation_ref,
            ws_id=self.from_whatsapp_id,
            phone_number=number,
            message=response,
            tool_call_id=tool_call.id,
            function_name=tool_call.function.name,
            function_response=response,
            contact_ref=self.contact_ref,
        )

    def handle_tool_calls(self, response, number):
        """Maneja y registra las llamadas a funciones"""
        print("----- RESPONSE ------", response)
        if isinstance(response, str) or not response.tool_calls:
            return

        self.message_repository.store_tool_call_responses(
            from_id=self.from_whatsapp_id,
            response=response,
            number=number,
            conversation_ref=self.conversation_ref,
            contact_ref=self.contact_ref,
        )

        for tool_call in response.tool_calls:
            logging.error(f"storing... {tool_call}")
            self.execute_tool(tool_call, self.chatbot.chatbot_model.tool_calls, number)
