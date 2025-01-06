from src.data.models.message import ChatMessage
from src.data.sources.firebase.message_impl import MessageFirebaseRepository
from src.data.sources.firebase.utils import get_contact_ref
from src.data.sources.firebase.config import db


def delete_messages(user_id, phone_number):
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

        print(contact_ref)

        messages = mensajes_ref.get()
        print("messajes", messages)
        # Eliminar los mensajes encontrados
        deleted_count = 0
        for message in messages:
            message.reference.delete()
            deleted_count += 1

        print(f"{deleted_count} mensajes eliminados para {phone_number} y {user_id}")

        return [
            ChatMessage(**message.to_dict()).to_dict() for message in messages
        ]

    except Exception as e:
        print(f"Error al obtener conversación para usuario {user_id}: {str(e)}")
        raise



deleted_messages = delete_messages("450361964838178", "573142968931")
deleted_messages

messages = MessageFirebaseRepository().get_messages("450361964838178", "573142968931")[-10:]
for message in messages:
    print(message)