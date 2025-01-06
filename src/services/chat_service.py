import json
import logging
from typing import Dict, Any

from src.common.utils.openai_utils import add_context_to_chatbot, generate_answer
from src.data.models.chatbot import ChatbotModel
from src.data.sources.firebase.contact_impl import ContactFirebaseRepository
from src.data.sources.firebase.message_impl import MessageFirebaseRepository


class ChatbotService:
    def __init__(self, chatbot_model: ChatbotModel):
        self.chatbot_model = chatbot_model

    def answer_conversation(self, from_whatsapp_id, to_number, question):
        messages = MessageFirebaseRepository().get_messages(from_whatsapp_id, to_number)[-10:]
        user_data = ContactFirebaseRepository().get_contact(from_whatsapp_id, to_number)
        
        return self.generate_answer_from_text_with_vector_db(question, user_data, messages, self.chatbot_model.tools)

    def generate_answer_from_text_with_vector_db(
        self, text: str, user_data: Dict[str, Any], messages, tools
    ):
        """Procesa mensajes de texto"""
        relevant_sections = self.chatbot_model.vectorstore.retrieve_relevant_sections(
            text
        )

        try:
            context = " ".join(relevant_sections)
            system_prompt = add_context_to_chatbot(
                self.chatbot_model.system_prompt, context, user_data
            )

            messages = [{"role": "system", "content": system_prompt}, *messages]
            response = generate_answer(messages, tools)
            logging.error(f"Response: {response}")
            return response
        
        except Exception as e:
            logging.error(e)
            raise

    def generate_answer_from_image(self, question, image_url, messages, tools):
        image_message = {"type": "image_url", "image_url": {"url": image_url}}

        try:
            response = generate_answer(
                messages.expand(
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": question}, image_message],
                    }
                ),
                tools,
            )

            return response

        except Exception as e:
            print(e)
