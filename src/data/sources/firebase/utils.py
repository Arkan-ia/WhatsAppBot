import io
import logging
import firebase_admin
from firebase_admin import storage
import firebase_admin.firestore
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
    if len(phone_number) != 12:
        raise Exception(
            "Los números a consultar deben tener su respectivo codigo de país"
        )

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
        business_snapshots = (
            db.collection("business").where("ws_id", "==", ws_id).limit(1).get()
        )
        if not business_snapshots:
            print(
                f"No se encontró ningún negocio al obtener token de WhatsApp para {ws_id}"
            )
            return
        token = business_snapshots[0].get("ws_token")
        return token

    except Exception as e:
        logging.exception("Error al obtener token de WhatsApp: %s", str(e))
        raise


# COSOS QUE TOCA CAMBIAR DE LADO
def get_or_create_contact(
    phone_number: str, from_whatsapp_id: str
) -> firebase_admin.firestore.firestore.DocumentReference:
    """
    Obtiene o crea un contacto en la base de datos.

    Args:
        phone_number (str): El número de teléfono del contacto.

    Returns:
        firebase_admin.firestore.DocumentReference: La referencia del contacto.
    """
    contacts_query = (
        db.collection_group("contacts")
        .where("phone_number", "==", phone_number)
        .where("ws_id", "==", from_whatsapp_id)
    )
    contacts_snapshots = contacts_query.get()

    if not contacts_snapshots:
        business_query = db.collection("business").where(
            "ws_id", "==", from_whatsapp_id
        )
        business_snapshots = business_query.get()

        if not business_snapshots:
            raise Exception(
                f"No hay ningún negocio en Venya vinculado a este número {from_whatsapp_id}"
            )

        business_ref = business_snapshots[0].reference
        contact_ref = business_ref.collection("contacts").document()

        contact_ref.set({"phone_number": phone_number, "ws_id": from_whatsapp_id})

    else:
        contact_ref = contacts_snapshots[0].reference

    return contact_ref


def get_or_create_conversation(
    contact_ref: firebase_admin.firestore.firestore.DocumentReference,
) -> firebase_admin.firestore.firestore.DocumentReference:
    """
    Obtiene o crea una conversación en la base de datos.

    Args:
        contact_ref (firebase_admin.firestore.DocumentReference): La referencia del contacto.

    Returns:
        firebase_admin.firestore.DocumentReference: La referencia de la conversación.
    """
    conversations_query = (
        db.collection("conversations")
        .where("status", "==", "ongoing")
        .where("contact_ref", "==", contact_ref)
    )
    conversations_snapshots = conversations_query.get()

    if not conversations_snapshots:
        conversation_ref = db.collection("conversations").document()
        conversation_ref.set(
            {
                "contact_ref": contact_ref,
                "start_time": firebase_admin.firestore.firestore.SERVER_TIMESTAMP,
                "platform": "whatsapp",
                "status": "ongoing",
                "intention": "comertial",  # TODO: Replace with gpt interpretation
            }
        )

    else:
        conversation_ref = conversations_snapshots[0].reference

    return conversation_ref


import json
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
from google.oauth2 import service_account


def create_task(url, payload=None):
    # Ruta a tu archivo JSON de credenciales
    credentials_path = "./key.json"

    # Carga las credenciales
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )

    # Crear cliente con las credenciales
    client = tasks_v2.CloudTasksClient(credentials=credentials)

    parent = client.queue_path(
        "innate-tempo-448214-e5", "northamerica-northeast1", "continueConversation"
    )

    # Configurar la solicitud HTTP
    task = {
        "http_request": {
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "url": url,
        }
    }

    if payload:
        task["http_request"]["body"] = payload.encode("utf-8")

    d = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(d)
    task["schedule_time"] = timestamp

    response = client.create_task(request={"parent": parent, "task": task})
    print(f"Tarea creada: {response.name}")
    return response.name  # Retorna el identificador de la tarea creada


def delete_task(task_name):
    # Ruta a tu archivo JSON de credenciales
    credentials_path = "./key.json"

    # Carga las credenciales
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )

    # Crear cliente con las credenciales
    client = tasks_v2.CloudTasksClient(credentials=credentials)

    # Eliminar la tarea
    client.delete_task(request={"name": task_name})
    print(f"Tarea eliminada: {task_name}")
