from concurrent.futures import ThreadPoolExecutor
import time
from src.data.sources.firebase.config import db

import firebase_admin
import firebase_admin.firestore
from src.common.config import CORS_HEADERS
from src.common.whatsapp.models.models import (
    TemplateMessage,
    TextMessage,
    WhatsAppMessage,
)
from flask import jsonify, request
import os
import logging
from src.chatbot_router import get_chatbot_from_number
from src.common.utils.whatsapp_utils import (
    is_reaction_whatsapp_message,
    is_valid_whatsapp_message,
    send_whatsapp_message,
)
from src.data.sources.firebase.message_impl import MessageFirebaseRepository
import pandas as pd

from src.data.sources.firebase.utils import (
    get_or_create_contact,
    get_or_create_conversation,
)


def verify():
    try:
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == os.getenv("VERIFY_TOKEN") and challenge != None:
            return challenge
        else:
            return jsonify({"status": "error", "message": "Token incorrecto"}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 403


def process_message():
    body = request.get_json()

    statuses = (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    )
    # Check if it's a WhatsApp status update
    if statuses:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        status = value["statuses"][0]

        if status["status"] == "read":
            message_id = status["id"]

            ### Method ###
            # mark_read_user_message()
            message = MessageFirebaseRepository().get_message(message_id)
            if not message:
                logging.error(f"No se encontró el mensaje {message_id}")

            else:
                message.update({"status": "seen"})
                print(f"Message {message_id} was read.")

            return jsonify({"status": "ok"}), 200

        print("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    entry = body["entry"][0]
    changes = entry["changes"][0]
    value = changes["value"]
    message = value["messages"][0]
    from_id = value["metadata"]["phone_number_id"]

    try:
        if is_valid_whatsapp_message(body):
            print("Starting message processing...")

            if is_reaction_whatsapp_message(message):
                return jsonify({"status": "ok"}), 200

            print("Starting bot creation...")
            chatbot = get_chatbot_from_number(from_id)
            print("Bot created successfully.")
            chatbot.manage_incoming_message(message)

            return jsonify({"status": "ok"}), 200
        else:
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except Exception as e:
        logging.error(f"Error al recibir el mensaje: {e}")
        logging.error(f"Body recibido: {body}")
        return (
            jsonify({"status": "error", "message": "Error interno del servidor"}),
            500,
        )


def send_template_message():
    try:
        body = request.get_json()
        if not body:
            return (
                jsonify(
                    {"status": "error", "message": "No se proporcionó cuerpo JSON"}
                ),
                400,
            )

        to_number = body.get("to_number")
        from_id = body.get("from_id")
        token = body.get("token")
        template = body.get("template")

        if not to_number or not from_id:
            return (
                jsonify({"status": "error", "message": "Faltan parámetros requeridos"}),
                400,
            )

        message = TemplateMessage(
            template=template, to_number=to_number, from_id=from_id, parameters=True
        )
        call = send_whatsapp_message(
            from_whatsapp_id=from_id, token=token, message=message
        )

        db_content = get_template_message_content(message.template)
        MessageFirebaseRepository().create_chat_message(
            from_id,
            message.to_number,
            db_content,
            wa_id=call["body"]["messages"][0]["id"],
        )

        return (
            jsonify(
                {
                    "status": "ok",
                    "message": f"Conversación iniciada con éxito para el número {to_number}",
                }
            ),
            200,
            CORS_HEADERS,
        )
    except Exception as e:
        logging.error(f"Error al iniciar la conversación: {str(e)}")
        return (
            jsonify({"status": "error", "message": "Error interno del servidor"}),
            500,
        )


def batchify(iterable, batch_size):
    """Divide un iterable en sublistas de tamaño batch_size."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


def send_massive_message():
    if "file" not in request.files:
        return {"error": "No se encontró un archivo en la solicitud"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "El archivo está vacío"}, 400
    file_data = pd.read_excel(file, header=None, converters={0: str})
    users = file_data[0].tolist()

    form = request.form
    required_params = ["from_id", "token"]
    for param in required_params:
        if param not in form:
            return (
                jsonify(
                    {"status": "error", "message": f"El parámetro {param} es requerido"}
                ),
                400,
            )

    from_id = form.get("from_id")
    token = form.get("token")
    message = form.get("message")
    template = form.get("template")
    language_code = form.get("language_code") or "es"

    business_snapshots = db.collection("business").where("ws_id", "==", from_id).get()
    if not business_snapshots:
        raise Exception(f"No hay business registrado para {from_id}")

    campaign_ref = business_snapshots[0].reference.collection("campaigns").document()
    campaign_ref.set(
        {
            "users_count": len(users),
            "created_at": firebase_admin.firestore.firestore.SERVER_TIMESTAMP,
            "platform": "whatsapp",
        }
    )

    messages = []
    for user in users:
        user = str(user)
        
        if not user.isdigit():
            continue
        msg = TemplateMessage(template=template, to_number=user, code=language_code)
        if not template:
            msg = TextMessage(number=user, text=message)
        messages.append(msg)

    def send_msg(msg: WhatsAppMessage):
        call = send_whatsapp_message(from_id, token, msg)
        db_content = get_template_message_content(msg.template)

        if not template:
            db_content = msg.text

        contact_ref = get_or_create_contact(msg.to_number, from_id)
        conversation_ref = get_or_create_conversation(contact_ref)

        MessageFirebaseRepository().create_chat_message(
            conversation_ref=conversation_ref,
            contact_ref=contact_ref,
            ws_id=from_id,
            phone_number=msg.to_number,
            message=db_content,
            wa_id=call["body"]["messages"][0]["id"],
        )

        contact_ref.update(
            {
                "last_message": {
                    "content": db_content,
                    "created_at": firebase_admin.firestore.firestore.SERVER_TIMESTAMP,
                }
            }
        )

        campaign_ref.update(
            {"sent_messages": firebase_admin.firestore.firestore.Increment(1)}
        )

        return call

    batch_size = 20

    def send_message_batch(batch):
        results = []
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = list(executor.map(lambda msg: send_msg(msg), batch))
        return results

    all_results = []
    for batch in batchify(messages, batch_size):
        batch_results = send_message_batch(batch)
        all_results.extend(batch_results)
        time.sleep(0.02)

    success_requests = sum(1 for result in all_results if result["status"] == "success")
    error_requests = len(users) - success_requests

    return (
        jsonify(
            {
                "status": "ok",
                "message": f"Mensajes enviados con éxito a {success_requests} usuarios, {error_requests} errores",
                "details": all_results,
            }
        ),
        200,
        CORS_HEADERS,
    )


def send_message():
    try:
        body = request.get_json()
        to_number = body.get("to_number")
        from_id = body.get("from_id")
        token = body.get("token")
        message = body.get("message")

        if not to_number or not from_id or not message:
            return (
                jsonify({"status": "error", "message": "Faltan parámetros requeridos"}),
                400,
            )

        message = TextMessage(number=to_number, text=message)
        call = send_whatsapp_message(
            from_whatsapp_id=from_id, token=token, message=message
        )

        logging.info(call)
        contact_ref = get_or_create_contact(to_number, from_id)
        conversation_ref = get_or_create_conversation(contact_ref)

        if call["status"] == "success":
            MessageFirebaseRepository().create_chat_message(
                conversation_ref=conversation_ref,
                contact_ref=contact_ref,
                ws_id=from_id,
                phone_number=to_number,
                message=message.text,
                wa_id=call["body"]["messages"][0]["id"],
            )

        return (
            jsonify({"status": "ok", "message": "Mensaje enviado con éxito"}),
            200,
            CORS_HEADERS,
        )

    except Exception as e:
        logging.error(e)
        return jsonify({"status": "error", "message": str(e)}), 500


## -------- TODO: ##
def get_template_message_content(template):
    template_messages = {
        "gano_excel_1": """🌟 ¡Gran Lanzamiento de la Línea Fit JM! 🌟
¡Hola! 😊 Hoy queremos compartir contigo una excelente noticia: estrenamos una nueva línea diseñada especialmente para facilitar tu proceso de compra y ofrecerte los mejores productos saludables.

🎉 Además, ¡tenemos promociones exclusivas por lanzamiento!
Escríbele a Jorge, nuestro asesor, y descubre cómo puedes aprovechar estas ofertas hoy mismo.

📲 ¡Estamos aquí para ayudarte a dar el siguiente paso hacia un estilo de vida más saludable!""",
        "gano_excel_2": """¡Este año sí vas a cumplir las promesas de año nuevo! ¿Cierto? 🧐

Si pediste por salud y vida, aquí llegó la señal divina 🙏 Que no te falte el café en cada mañana para iniciar con energía, fusionado con Ganoderma para una vida larga y prospera. ☕ Si diciembre te dejó apretado, relájate. 😌 Porque si llevas 2 o más cajas de nuestro café 3 en 1 o clásico, vas a tener tremendo descuento en tú compra. 😱 ¡Estamos botados! 
La promo es hasta el 15 de enero. 🛒""",
        "ano_nuevo": """☕✨ ¡Feliz Año Nuevo! ✨☕

        Si llevas 2 o más cajas de nuestro café 3 en 1 o clásico, te damos un precio especial. 
        La promo es hasta el 15 de enero. 🏃‍♀""",
        "hola": """Hola""",
    }

    if template in template_messages:
        return template_messages[template]
    else:
        raise Exception("No se encontró el contenido del template solicitado.")
