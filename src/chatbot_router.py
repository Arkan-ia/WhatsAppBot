
from models.chatbot import ChatbotModel
from src.conversation_manager import ConversationManager
from src.data_management import get_whatsapp_token
from src.whatsapp_api_handler import WhatsAppAPIHandler
from utils.pdf_manager import PDFManager


def get_chatbot_from_number(from_id: str):
    token = get_whatsapp_token(from_id)
    whatsapp_api_handler = WhatsAppAPIHandler(api_url=f"https://graph.facebook.com/v21.0/{from_id}/messages", token=token)

    if (from_id == "541794965673706"):
        # Zalee bot
        personalization_data = {
            "name": 'Johan',
            "company": 'Zalee',
            "location": 'Bogotá - Colombia',
            "description": 'Plataforma donde puedes encontrar las mejores ofertas y beneficios para la vida nocturna en Bogotá, ya sea en pubs, clubes, discotecas o eventos.'
            'En cuanto a sitios puedes explorar los mejores descuentos en sus productos y conocer Bogotá, y en eventos, obtienes descuentos por cantidad de personas.'
            'Si eres un sitio o un organizador de eventos, automatizamos y mejoramos tu proceso de compra de entradas y puedes publicar tus productos y eventos para promocionarlos.',
            "personality": "Un joven de 19 años fiestero, carismático y con una personalidad muy alegre.",
            "expressions": ["Ey fiestero!", "Listo parcero"]
        }

        chatbot = ChatbotModel(**personalization_data)

        pdf_manager = PDFManager("https://firebasestorage.googleapis.com/v0/b/arcania-c4669.appspot.com/o/media%2FBrochure%20de%20Marca.pdf?alt=media&token=12437f44-6c25-41a2-b41e-f1d9402339cf")
        conversation_manager = ConversationManager(whatsapp_api_handler, pdf_manager, chatbot)
        return conversation_manager
    
    elif (from_id == "DONREJUANONUMBER"):
        # Don Rejuano bot
        personalization_data = {
            "name": 'Brayan',
            "company": 'La Rejana Callejera',
            "location": 'Pasto - Boyacá - Colombia',
            "description": 'Restaurante - Comida',
            "personality": "Un joven campesino de 20 años que trabaja en el restaurante de su familia.",
            "expressions": ["qué más, pues?", "cómo le va?", "hágale, pues.", "qué se cuenta?", "eso es", "de una", "listo, pues", "claro, mijo", "a la orden", "con gusto"]
        }

        chatbot = ChatbotModel(**personalization_data)

        pdf_manager = PDFManager("https://cdn.glitch.global/1e6c16f0-cf67-4f9c-b4af-433d3336cf2f/Menu.pdf?v=1729527777028")
        conversation_manager = ConversationManager(whatsapp_api_handler, pdf_manager, chatbot)
        return conversation_manager
