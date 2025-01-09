import logging
from typing import List
from src.data.sources.firebase.config import db
from src.data.models.message import ChatMessage
from src.data.repositories.message_repository import MessageRepository
from firebase_admin.firestore import firestore

from src.data.sources.firebase.utils import get_contact_ref



class MessageFirebaseRepository(MessageRepository):
    def validate_phone_number(self, phone_number):
        """Valida el número de teléfono."""
        if len(phone_number) != 12:
            raise ValueError("El número debe incluir el código de país y tener 12 dígitos.")

    # No me gusta esta función
    def get_or_create_user_and_contact(self, user_id, phone_number):
        """Obtiene el usuario y contacto en una sola operación."""
        user_ref = db.collection("users").where("ws_id", "==", user_id).limit(1).get()
        if not user_ref:
            logging.warning(f"No se encontró ningún usuario con ws_id {user_id}.")
            return None, None

        user_doc = user_ref[0].reference

        # Intentar obtener el contacto directamente como documento
        contact_ref = user_doc.collection("contacts").document(phone_number)
        contact_snapshot = contact_ref.get()

        if not contact_snapshot.exists:
            logging.info(f"Creando nuevo contacto con número {phone_number}.")
            contact_ref.set({"phone_number": phone_number})

        return user_doc, contact_ref

    def create_message(self, user_id, phone_number, message, role, **kwargs):
        """Añade un mensaje a la conversación."""
        try:
            # Validar el número de teléfono
            self.validate_phone_number(phone_number)

            # Obtener o crear usuario y contacto
            user_doc, contact_ref = self.get_or_create_user_and_contact(user_id, phone_number)
            if not user_doc or not contact_ref:
                return

            # Crear el mensaje
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
            logging.info(
                f"Mensaje {'del usuario' if role else 'del bot'} añadido para {phone_number} "
                f"del usuario con ws_id {user_id}, id mensaje: {kwargs.get('message_id', 'None')}."
            )
        except ValueError as ve:
            logging.error(f"Error de validación: {ve}")
            raise
        except Exception as e:
            logging.error(f"Error al añadir mensaje para usuario {user_id}: {e}")
            raise

    def get_message(self, msj_id):
        try:
            mensajes_ref = db.collection_group("messages").where("message_id", "==", msj_id).get()
            if not mensajes_ref:
                print(f"No se encontró ningún mensaje con el id {msj_id}")
                return None

            return mensajes_ref[0].reference
        except Exception as e:
            print(f"Error al obtener mensaje con el id {msj_id}: {str(e)}")
            raise

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

            user_ref = (
                db.collection("users").where("ws_id", "==", user_id).limit(1).get()
            )
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

            return [
                ChatMessage(**message.to_dict()).to_dict()
                for message in mensajes_ref.get()
            ]

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
