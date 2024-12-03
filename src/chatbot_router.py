from src.models.chatbot import ChatbotModel
from src.conversation_manager import ConversationManager
from src.db.firebase import get_whatsapp_token
from src.whatsapp_api_handler import WhatsAppAPIHandler
from src.utils.vector_store_manager import VectorStoreManager
import logging


def get_chatbot_from_number(from_id: str):
    try:
        print("from_id: ", from_id)
        token = get_whatsapp_token(from_id)
        whatsapp_api_handler = WhatsAppAPIHandler(
            api_url=f"https://graph.facebook.com/v21.0/{from_id}/messages", token=token
        )

        if from_id == "541794965673706":
            try:
                # Zalee bot
                personalization_data = {
                    "name": "Johan",
                    "company": "Zalee",
                    "location": "Bogotá - Colombia",
                    "description": "Plataforma donde puedes encontrar las mejores ofertas y beneficios para la vida nocturna en Bogotá, ya sea en pubs, clubes, discotecas o eventos."
                    "En cuanto a sitios puedes explorar los mejores descuentos en sus productos y conocer Bogotá, y en eventos, obtienes descuentos por cantidad de personas."
                    "Si eres un sitio o un organizador de eventos, automatizamos y mejoramos tu proceso de compra de entradas y puedes publicar tus productos y eventos para promocionarlos.",
                    "personality": "Un joven de 19 años fiestero, carismático y con una personalidad muy alegre.",
                    "expressions": ["Ey fiestero!", "Listo parcero"],
                }

                chatbot = ChatbotModel(**personalization_data)

                pdf_manager = VectorStoreManager(
                    "https://firebasestorage.googleapis.com/v0/b/arcania-c4669.appspot.com/o/media%2FBrochure%20de%20Marca.pdf?alt=media&token=12437f44-6c25-41a2-b41e-f1d9402339cf"
                )
                conversation_manager = ConversationManager(
                    whatsapp_api_handler, pdf_manager, chatbot
                )
                return conversation_manager

            except Exception as e:
                logging.exception("Error al configurar el chatbot de Zalee: %s", str(e))
                raise

        elif from_id == "400692489794103":
            try:
                # Jorge bot
                personalization_data = {
                    "name": "Jorge",
                    "company": "Gano Excel",
                    "location": "Bogotá - Colombia",
                    "vectorstore_path": "./src/vectorstores/juan_gano_excel",
                    "description": "En Gano Excel, nos dedicamos a la creación de productos con los más altos estándares de calidad en la búsqueda de tu bienestar. Descubre cómo nuestra gama única de productos, puede transformar tu vida.",
                    "personality": "Un hombre de 30 años, con una personalidad muy tranquila y amable.",
                    "expressions": [""],
                }

                chatbot = ChatbotModel(**personalization_data)

                conversation_manager = ConversationManager(
                    whatsapp_api_handler, chatbot
                )
                return conversation_manager
            except Exception as e:
                logging.exception(
                    "Error al configurar el chatbot de Gano Excel: %s", str(e)
                )
                raise

        elif from_id == "523135820878320":
            try:
                # Don Rejuano bot
                personalization_data = {
                    "name": "Brayan",
                    "company": "La Rejana Callejera",
                    "location": "Pasto - Boyacá - Colombia",
                    "description": "Restaurante - Comida",
                    "personality": "Un joven campesino de 20 años que trabaja en el restaurante de su familia.",
                    "expressions": [
                        "qué más, pues?",
                        "cómo le va?",
                        "hágale, pues.",
                        "qué se cuenta?",
                        "eso es",
                        "de una",
                        "listo, pues",
                        "claro, mijo",
                        "a la orden",
                        "con gusto",
                    ],
                    "specific_prompt": """" 
    Eres un asistente util que sirve para vender mas con mi restaurante asistencia en cualquier pregunta relacionada.

    Solicita una orden cada nueva conversación, algunas preguntas de ejemplo son:
    - "¿Qué quieres comer hoy?"
    - "¿Qué te apetece probar hoy?"
    - "¿Tienes antojo de algo en especial?"
    Al pedir la orden debes hacer lo siguiente: Pedir el nombre, la dirección y el medio de pago.

    Nuestro menú lo puedes ver en el archivo proporcionado, cualquier pregunta del menú respondela en base a esa información. En caso de no tener ningun archivo o no encontrar informacion relevante no inventes y responde que no tienes esa información


    """,
                }

                chatbot = ChatbotModel(**personalization_data)

                pdf_manager = VectorStoreManager(
                    "https://cdn.glitch.global/1e6c16f0-cf67-4f9c-b4af-433d3336cf2f/Menu.pdf?v=1729527777028"
                )
                conversation_manager = ConversationManager(
                    whatsapp_api_handler, pdf_manager, chatbot
                )
                return conversation_manager
            except Exception as e:
                logging.exception(
                    "Error al configurar el chatbot de La Rejana Callejera: %s", str(e)
                )
                raise

    except Exception as e:
        logging.exception("Error general en get_chatbot_from_number: %s", str(e))
        raise
