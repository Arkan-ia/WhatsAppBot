from src.data.models.chatbot import ChatbotModel
from src.data.sources.firebase.utils import get_whatsapp_token
from src.managers.conversation_manager import ConversationManager
import logging
from src.data.sources.firebase.chat_configs import chatbot_configs
from src.services.chat_service import ChatbotService


def get_chatbot_from_number(from_id: str):
    if from_id in chatbot_configs:
        try:
            chatbot_model = ChatbotModel(**chatbot_configs[from_id])
            chat_service = ChatbotService(chatbot_model)
            conversation_manager = ConversationManager(
                chatbot=chat_service,
                from_whatsapp_id=from_id,
                token=get_whatsapp_token(from_id),
            )
            return conversation_manager

        except Exception as e:
            logging.exception(
                f"Error al configurar el chatbot para {from_id}: {str(e)}"
            )
            raise
    else:
        logging.error(f"ID de WhatsApp no reconocido: {from_id}")
        raise ValueError("ID de WhatsApp no reconocido")
