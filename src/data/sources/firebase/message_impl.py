from typing import List
from src.data.sources.firebase.config import db
from src.data.models.message import ChatMessage
from src.data.repositories.message_repository import MessageRepository
from firebase_admin.firestore import firestore

from src.data.sources.firebase.utils import get_contact_ref

class MessageFirebaseRepository(MessageRepository):
    def create_message(self, user_id, phone_number, message, role, **kwargs):
        """Añade un mensaje a la conversación."""
        try:
            contact_ref = get_contact_ref(user_id, phone_number)
            if not contact_ref:
                return

            user_ref = db.collection("users").where("ws_id", "==", user_id).limit(1).get()
            if not user_ref:
                print(
                    f"No se encontró ningún usuario al añadir mensaje para {phone_number} para {user_id}"
                )
                return
            user_doc = user_ref[0].reference

            message_ref = user_doc.collection("messages").document()
            message_ref.set(
                {
                    "contact_ref": contact_ref,
                    "content": message,
                    "role": role,
                    "platform": "whatsapp",
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    **kwargs,
                }
            )
            print(
                f"Mensaje {'del usuario' if role else 'del bot'} añadido para el contacto {phone_number} del usuario con ws_id {user_id}"
            )
        except Exception as e:
            print(f"Error al añadir mensaje para usuario {user_id}: {str(e)}")
            raise

    def get_message(self, user_id, phone_number, message, role, **kwargs):
        pass

    def update_message(self, user_id, phone_number, message, role, **kwargs):
        pass

    def delete_message(self, user_id, phone_number, message, role, **kwargs):
        pass

    def get_messages(self, user_id, phone_number) -> List:
        """Obtiene la conversación de un usuario con un contacto específico."""
        try:
            contact_ref = get_contact_ref(user_id, phone_number)
            if not contact_ref:
                return None

            user_ref = db.collection("users").where("ws_id", "==", user_id).limit(1).get()
            if not user_ref:
                print(
                    f"No se encontró ningún usuario al obtener conversación para {phone_number} para {user_id}"
                )
                return None
            user_doc = user_ref[0].reference

            mensajes_ref = (
                user_doc.collection("messages")
                .where("contact_ref", "==", contact_ref)
                .order_by("timestamp")
            )

            return [ChatMessage(**message.to_dict()).to_dict() for message in mensajes_ref.get()]
        
        except Exception as e:
            print(f"Error al obtener conversación para usuario {user_id}: {str(e)}")
            raise
    
    def store_tool_call_responses(self, from_id, response, number):
        tool_call_responses = []

        for tool_call in response.tool_calls:
            tool_call_responses.append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "arguments": tool_call.function.arguments,
                        "name": tool_call.function.name,
                    },
                }
            )

        super().create_chat_message(from_id, number, "", tool_calls=tool_call_responses)


    
