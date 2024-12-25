import io
import logging
from typing import List
import firebase_admin
from firebase_admin import credentials, firestore, storage

try:
    # Inicialización de Firebase
    cred = credentials.Certificate("src/db/firebase.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error al inicializar Firebase: {str(e)}")
    raise


def create_project(nombre_proyecto):
    """Crea un nuevo proyecto en Firestore."""
    try:
        proyecto_ref = db.collection("proyectos").document(nombre_proyecto)
        proyecto_ref.set(
            {
                "nombre": nombre_proyecto,
                "timestamp_creacion": firestore.SERVER_TIMESTAMP,
            }
        )
        print(f"Proyecto creado: {nombre_proyecto}")
    except Exception as e:
        print(f"Error al crear proyecto {nombre_proyecto}: {str(e)}")
        raise


def get_project(nombre_proyecto):
    """Obtiene un proyecto de Firestore."""
    try:
        proyecto_ref = db.collection("proyectos").document(nombre_proyecto)
        proyecto = proyecto_ref.get()
        if proyecto.exists:
            return proyecto.to_dict()
        else:
            print(f"El proyecto {nombre_proyecto} no existe")
            return None
    except Exception as e:
        print(f"Error al obtener proyecto {nombre_proyecto}: {str(e)}")
        raise


def add_contact(ws_id, phone_number, display_name):
    """Añade un contacto a un usuario en Firestore."""
    try:
        user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
        if not user_ref:
            print(
                f"No se encontró ningún usuario al añadir contacto {phone_number} para {ws_id}"
            )
            return
        user_doc = user_ref[0].reference
        contact_ref = user_doc.collection("contacts").document()
        contact_ref.set({"nombre": display_name, "phone_number": phone_number})
        print(f"Contacto añadido para el usuario con ws_id {ws_id}: {display_name}")
    except Exception as e:
        print(f"Error al añadir contacto para usuario {ws_id}: {str(e)}")
        raise


def get_contact_ref(ws_id, phone_number):
    """Obtiene la referencia de un contacto."""
    try:
        user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
        if not user_ref:
            print(
                f"No se encontró ningún usuario al obtener contacto {phone_number} para {ws_id}"
            )
            return None
        user_doc = user_ref[0].reference
        contact_query = (
            user_doc.collection("contacts")
            .where("phone_number", "==", phone_number)
            .limit(1)
        )
        contact_docs = contact_query.get()
        if not contact_docs:
            print(
                f"No se encontró ningún contacto con el número {phone_number} para el usuario con ws_id {ws_id}"
            )
            print("Creando nuevo contacto...")
            nuevo_contacto_ref = user_doc.collection("contacts").document()
            nuevo_contacto_ref.set({"phone_number": phone_number})
            return nuevo_contacto_ref
        
        return contact_docs[0].reference
    
    except Exception as e:
        print(f"Error al obtener referencia de contacto para usuario {ws_id}: {str(e)}")
        raise


def add_message(ws_id, phone_number, message, role, **kwargs):
    """Añade un mensaje a la conversación."""
    try:
        contact_ref = get_contact_ref(ws_id, phone_number)
        if not contact_ref:
            return

        user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
        if not user_ref:
            print(
                f"No se encontró ningún usuario al añadir mensaje para {phone_number} para {ws_id}"
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
            f"Mensaje {'del usuario' if role else 'del bot'} añadido para el contacto {phone_number} del usuario con ws_id {ws_id}"
        )
    except Exception as e:
        print(f"Error al añadir mensaje para usuario {ws_id}: {str(e)}")
        raise


def add_contact_message(ws_id, phone_number, message):
    """Añade un mensaje del bot a la conversación."""
    try:
        add_message(ws_id, phone_number, message, "user")
    except Exception as e:
        print(f"Error al añadir mensaje del bot para usuario {ws_id}: {str(e)}")
        raise


def add_chat_message(ws_id, phone_number, message, tool_calls=None):
    """Añade un mensaje del usuario a la conversación."""
    try:
        add_message(ws_id, phone_number, message, "assistant", tool_calls=tool_calls)
    except Exception as e:
        print(f"Error al añadir mensaje del usuario {ws_id}: {str(e)}")
        raise


def add_tool_message(
    ws_id, phone_number, message, tool_call_id, function_name, function_response
):
    """Añade un mensaje de herramienta a la conversación."""
    try:
        add_message(
            ws_id,
            phone_number,
            message,
            "tool",
            tool_call_id=tool_call_id,
            name=function_name,
            content=function_response,
        )
    except Exception as e:
        print(f"Error al añadir mensaje de herramienta {ws_id}: {str(e)}")
        raise


def get_conversation(ws_id, phone_number) -> List:
    """Obtiene la conversación de un usuario con un contacto específico."""
    try:
        contact_ref = get_contact_ref(ws_id, phone_number)
        if not contact_ref:
            return None

        user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
        if not user_ref:
            print(
                f"No se encontró ningún usuario al obtener conversación para {phone_number} para {ws_id}"
            )
            return None
        user_doc = user_ref[0].reference

        mensajes_ref = (
            user_doc.collection("messages")
            .where("contact_ref", "==", contact_ref)
            .order_by("timestamp")
        )
        return mensajes_ref.get()
    except Exception as e:
        print(f"Error al obtener conversación para usuario {ws_id}: {str(e)}")
        raise


def get_contact_data(ws_id, phone_number):
    """Obtiene los datos del usuario."""
    try:
        contact_ref = get_contact_ref(ws_id, phone_number)
        return contact_ref.get().to_dict()
    
    except Exception as e:
        print(f"Error al obtener datos del usuario {ws_id}: {str(e)}")
        raise


def upload_media_to_storage(image, path):
    """Uploads media to Firebase Storage."""
    try:
        storage_path = f"media/{path}"
        bucket = storage.bucket("arcania-c4669.appspot.com")
        blob = bucket.blob(storage_path)
        blob.upload_from_string(
            image.content, content_type=image.headers["content-type"]
        )
        print("Image uploaded to:", blob.public_url)
        return blob.generate_signed_url(expiration=60 * 60)
    except Exception as e:
        print(f"Error al subir archivo multimedia: {str(e)}")
        raise


def upload_audio_to_storage(audio_media_response, file_name):
    """Uploads audio to Firebase Storage."""
    try:
        bucket = storage.bucket("arcania-c4669.appspot.com")
        blob = bucket.blob(file_name)

        file_stream = io.BytesIO(audio_media_response.content)

        blob.upload_from_file(file_stream, content_type="audio/mpeg")
        blob.make_public()

        return blob.public_url
    except Exception as e:
        print(f"Error al subir archivo multimedia [AUDIO]: {str(e)}")
        raise


def get_whatsapp_token(ws_id: str) -> str:
    try:
        user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
        if not user_ref:
            print(
                f"No se encontró ningún usuario al obtener token de WhatsApp para {ws_id}"
            )
            return
        token = user_ref[0].get("whatsapp_token")
        return token

    except Exception as e:
        logging.exception("Error al obtener token de WhatsApp: %s", str(e))
        raise


def update_contact_data(ws_id, phone_number, data):
    """Actualiza los datos de un contacto."""
    try:
        contact_ref = get_contact_ref(ws_id, phone_number)
        contact_ref.update(data)
    except Exception as e:
        print(
            f"Error al actualizar datos del contacto {phone_number} para {ws_id}: {str(e)}"
        )
        raise
