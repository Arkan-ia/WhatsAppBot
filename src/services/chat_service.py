import json
import logging
from typing import Any, Dict

from src.common.utils.openai_utils import add_context_to_chatbot, generate_answer
from src.data.models.chatbot import ChatbotModel
from src.data.sources.firebase.contact_impl import ContactFirebaseRepository
from src.data.sources.firebase.message_impl import MessageFirebaseRepository


class ChatbotService:
    def __init__(self, chatbot_model: ChatbotModel):
        self.chatbot_model = chatbot_model

    def answer_conversation(self, from_whatsapp_id, to_number):
        messages = MessageFirebaseRepository().get_messages(
            from_whatsapp_id, to_number
        )[-10:]
        user_data = ContactFirebaseRepository().get_contact(from_whatsapp_id, to_number)

        return self.generate_answer_from_text_with_vector_db(
            user_data, messages, self.chatbot_model.tools
        )

    def generate_answer_from_text_with_vector_db(
        self, user_data: Dict[str, Any], messages: list, tools, image=None
    ):
        """Procesa mensajes de texto"""
        user_query = messages[-1]

        relevant_sections = self.chatbot_model.vectorstore.retrieve_relevant_sections(
            user_query["content"]
        )

        if image:
            image_message = {"type": "image_url", "image_url": {"url": image}}
            user_query = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "¿Cuál es la pregunta?"},
                        image_message,
                    ],
                }
            ]

        try:
            context = " ".join(relevant_sections)
            system_prompt = add_context_to_chatbot(
                self.chatbot_model.system_prompt, context, user_data
            )

            messages = [{"role": "system", "content": system_prompt}, *messages]
            response = generate_answer(messages, tools)
            logging.info(
                f"Respuesta: {response}"
            )  # Cambiado de error a info para reflejar el éxito
            return response

        except Exception as e:
            logging.error(f"Error al generar la respuesta: {e}")
            raise
