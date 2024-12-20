from src.models.chatbot import ChatbotModel
from src.conversation_manager import ConversationManager
from src.db.firebase import get_whatsapp_token
from src.whatsapp_api_handler import WhatsAppAPIHandler
from src.db.chat_configs import chatbot_configs
import logging


def get_chatbot_from_number(from_id: str):
    try:
        print("from_id: ", from_id)
        token = get_whatsapp_token(from_id)
        whatsapp_api_handler = WhatsAppAPIHandler(from_whatsapp_id=from_id, token=token)

        if from_id in chatbot_configs:
            try:
                chatbot = ChatbotModel(**chatbot_configs[from_id])
                conversation_manager = ConversationManager(whatsapp_api_handler, chatbot)
                return conversation_manager
            
            except Exception as e:
                logging.exception(f"Error al configurar el chatbot para {from_id}: {str(e)}")
                raise
        else:
            logging.error(f"ID de WhatsApp no reconocido: {from_id}")
            raise ValueError("ID de WhatsApp no reconocido")

    except Exception as e:
        logging.exception("Error general en get_chatbot_from_number: %s", str(e))
        raise
