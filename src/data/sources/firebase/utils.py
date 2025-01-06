import io
import logging
from firebase_admin import storage
from src.data.sources.firebase.config import db


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



def get_contact_ref(ws_id, phone_number: str):
    """Obtiene la referencia de un contacto."""
    if len(phone_number) != 12: raise Exception("Los números a consultar deben tener su respectivo codigo de país")
    
    try:
        user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
        if not user_ref:
            print(
                f"No se encontró ningún usuario al obtener contacto {phone_number} para {ws_id}"
            )
            return None
        user_doc = user_ref[0].reference
        # TODO: A veces separa a un contacto de otro debido al 57. Hacer que sean iguales.
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

