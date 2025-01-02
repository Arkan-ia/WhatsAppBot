import json
import logging
from typing import Any, Dict, Optional

from src.common.utils.openai_utils import get_media_from_id
from src.common.utils.whatsapp_utils import get_whatsapp_message, send_whatsapp_message
from src.common.whatsapp.models.models import MarkReadMessage, TextMessage

from openai import OpenAI

from src.data.sources.firebase.message_impl import MessageFirebaseRepository
from src.services.chat_service import ChatbotService

client = OpenAI()


class ConversationManager:
    def __init__(self, from_whatsapp_id: str, token: str, chatbot: ChatbotService):
        self.chatbot = chatbot
        self.from_whatsapp_id = from_whatsapp_id
        self.token = token
        self.message_repository = MessageFirebaseRepository()

    def manage_incoming_message(self, message: Dict[str, Any]):
        """
        Procesa y maneja los mensajes entrantes de WhatsApp.

        Args:
            message (Dict[str, Any]): El mensaje entrante con toda su información
        """
        try:
            self.message_repository.create_contact_message(
                self.from_whatsapp_id,
                message["from"],
                get_whatsapp_message(message),
            )
            self.mark_read_message(message.get("id", None))

            self.handle_message_type(message)

            response = self.chatbot.answer_conversation(
                self.from_whatsapp_id, message["from"], get_whatsapp_message(message)
            )

            self.message_repository.create_chat_message(
                self.from_whatsapp_id, message["from"], response
            )

            text_message = TextMessage(message["from"], response)
            send_whatsapp_message(self.from_whatsapp_id, self.token, text_message)

        except Exception as e:
            logging.exception("Error al procesar mensaje entrante: %s", str(e))
            raise

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
            image_url = get_media_from_id(message["image"]["id"])
            response = self.chatbot.generate_answer_from_image("", image_url)

            return self.handle_tool_calls(response, message["from"])

        else:
            response = self.chatbot.answer_conversation(
                self.from_whatsapp_id, message["from"], get_whatsapp_message(message)
            )

            return self.handle_tool_calls(response, message["from"])

    def execute_tool(self, tool_call, options, number) -> str:
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        response = options[function_name](args)

        self.message_repository.create_tool_message(
            self.from_whatsapp_id,
            number,
            response,
            tool_call_id=tool_call.get("id"),
            function_name=tool_call.get("function", {}).get("name"),
            function_response=response,
        )

        return response

    def handle_tool_calls(self, response, number):
        """Maneja y registra las llamadas a funciones"""
        if isinstance(response, str) or not response.tool_calls:
            return response

        self.message_repository.store_tool_call_responses(
            from_id=self.from_whatsapp_id, response=response, number=number
        )

        for tool_call in response.tool_calls:
            self.execute_tool(tool_call, self.tools, number)
