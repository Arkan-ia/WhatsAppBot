import logging
import tiktoken
from typing import List, Optional
from src.data.sources.firebase.config import db
from src.data.models.message import ChatMessage
from src.data.repositories.message_repository import MessageRepository
from firebase_admin.firestore import firestore


class MessageFirebaseRepository(MessageRepository):
    def validate_phone_number(self, phone_number):
        """Valida el número de teléfono."""
        if len(phone_number) != 12:
            raise ValueError(
                "El número debe incluir el código de país y tener 12 dígitos."
            )

    def create_message(
        self,
        conversation_ref,
        contact_ref,
        ws_id,
        wa_id,
        phone_number,
        message,
        role,
        **kwargs,
    ):
        """Añade un mensaje a la conversación."""
        try:
            # Validar el número de teléfono
            self.validate_phone_number(phone_number)
            # Puede que esto demore
            enc = tiktoken.encoding_for_model("gpt-4o")
            tokens = enc.encode(message)
            # Medir tiempo

            message_ref = conversation_ref.collection("messages").document()
            message_ref.set(
                {
                    "contact_ref": contact_ref,
                    "content": message,
                    "role": role,
                    "ws_id": ws_id,
                    "wa_id": wa_id,
                    "tokens": len(tokens),
                    "phone_number": phone_number,
                    "platform": "whatsapp",
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    **kwargs,
                }
            )
            logging.info(
                f"Mensaje {'del usuario' if role else 'del bot'} añadido para {phone_number} "
                f"del usuario con ws_id {ws_id}, id mensaje: {wa_id}."
            )

        except ValueError as ve:
            logging.error(f"Error de validación: {ve}")
            raise
        except Exception as e:
            logging.error(f"Error al añadir mensaje para usuario {ws_id}: {e}")
            raise

    def get_message(self, msj_id) -> Optional[firestore.DocumentReference]:
        try:
            messages_snapshots = (
                db.collection_group("messages").where("wa_id", "==", msj_id).get()
            )

            if not messages_snapshots:
                print(f"No se encontró ningún mensaje con el id {msj_id}")
                return None

            return messages_snapshots[0].reference
        except Exception as e:
            print(f"Error al obtener mensaje con el id {msj_id}: {str(e)}")
            raise

    def update_message(self, user_id, phone_number, message, role, **kwargs):
        pass

    def delete_message(self, user_id, phone_number, message, role, **kwargs):
        pass

    def get_messages(self, ws_id, phone_number) -> List:
        """Obtiene la conversación de un usuario con un contacto específico."""
        try:
            messages_query = (
                db.collection_group("messages")
                .where("phone_number", "==", phone_number)
                .where("ws_id", "==", ws_id)
                .order_by("timestamp")
            )

            messages_snapshots = messages_query.get()

            return [
                ChatMessage(**message.to_dict()).to_dict()
                for message in messages_snapshots
            ]

        except Exception as e:
            print(
                f"Error al obtener conversación para usuario {phone_number}: {str(e)}"
            )
            raise

    def store_tool_call_responses(
        self, from_id, response, number, contact_ref, conversation_ref
    ):
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

        super().create_chat_message(
            conversation_ref=conversation_ref,
            contact_ref=contact_ref,
            ws_id=from_id,
            phone_number=number,
            message="",
            wa_id="",
            tool_calls=tool_call_responses,
        )
