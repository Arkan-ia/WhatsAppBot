from concurrent.futures import ThreadPoolExecutor
import time
from src.common.whatsapp.models.models import TemplateMessage, TextMessage
from flask import jsonify, request
import os
import logging
from src.chatbot_router import get_chatbot_from_number
from src.common.utils.whatsapp_utils import is_reaction_whatsapp_message, is_valid_whatsapp_message, send_whatsapp_message
from src.data.sources.firebase.message_impl import MessageFirebaseRepository
import pandas as pd


def verify():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == os.getenv('VERIFY_TOKEN') and challenge != None:
            return challenge
        else:
            return jsonify({"status": "error", "message": "Token incorrecto"}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    
    
def process_message():
    body = request.get_json()

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        print("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200
    
    print("Starting message processing...")

    entry = body['entry'][0]
    changes = entry['changes'][0]
    value = changes['value']
    message = value['messages'][0]
    from_id = value["metadata"]["phone_number_id"]

    try:
        if is_valid_whatsapp_message(body):
            print("Starting bot creation...")

            if is_reaction_whatsapp_message(message):
                return jsonify({"status": "ok"}), 200

            chatbot = get_chatbot_from_number(from_id)
            print("Bot created successfully.")
            chatbot.manage_incoming_message(message)

            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except Exception as e:
        logging.error(f"Error al recibir el mensaje: {e}")
        logging.error(f"Body recibido: {body}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


def send_template_message():
    try:
        body = request.get_json()
        if not body:
            return jsonify({"status": "error", "message": "No se proporcionó cuerpo JSON"}), 400

        to_number = body.get('to_number')
        from_id = body.get('from_id')
        token = body.get('token')
        template = body.get('template')
        
        if not to_number or not from_id:
            return jsonify({"status": "error", "message": "Faltan parámetros requeridos"}), 400

        message = TemplateMessage(template=template, to_number=to_number, from_id=from_id)
        send_whatsapp_message(from_whatsapp_id=from_id, token=token, message=message)
        
        db_content = get_template_message_content(message.template)
        MessageFirebaseRepository().create_chat_message(from_id, message.to_number, db_content)

        return jsonify({
            "status": "ok",
            "message": f"Conversación iniciada con éxito para el número {to_number}"
        }), 200
    except Exception as e:
        logging.error(f"Error al iniciar la conversación: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


def batchify(iterable, batch_size):
    """Divide un iterable en sublistas de tamaño batch_size."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]

def send_massive_message():
    if 'file' not in request.files:
        return {"error": "No se encontró un archivo en la solicitud"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"error": "El archivo está vacío"}, 400
    file_data = pd.read_excel(file, header=None, converters={0: str})
    users = file_data[0].tolist()

    form = request.form
    required_params = ['from_id', 'token']
    for param in required_params:
        if param not in form:
            return jsonify({"status": "error", "message": f"El parámetro {param} es requerido"}), 400
    from_id = form.get('from_id')
    token = form.get('token')
    message = form.get('message')
    template = form.get('template')
    language_code = form.get('language_code')

    messages = []
    for user in users:
        if not user.isdigit():
            continue
        msg = TemplateMessage(template=template, to_number=user, code=language_code)
        if not template:
            msg = TextMessage(number=user, text=message)
        messages.append(msg)

    batch_size = 20
    def send_message_batch(batch):
        results = []
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = list(executor.map(
                lambda msg: send_whatsapp_message(from_id, token, msg),
                batch
            ))
        return results

    all_results = []
    for batch in batchify(messages, batch_size):
        batch_results = send_message_batch(batch)
        all_results.extend(batch_results)
        time.sleep(0.02)

    success_requests = sum(1 for result in all_results if result["status"] == "success")
    error_requests = len(users) - success_requests

    return jsonify({
        "status": "ok",
        "message": f"Mensajes enviados con éxito a {success_requests} usuarios, {error_requests} errores",
        "details": all_results
    }), 200

def send_message():
    body = request.get_json()
    to_number = body.get('to_number')
    from_id = body.get('from_id')
    token = body.get('token')
    message = body.get('message')

    if not to_number or not from_id or not message:
        return jsonify({"status": "error", "message": "Faltan parámetros requeridos"}), 400
    
    message = TextMessage(number=to_number, text=message)
    call = send_whatsapp_message(from_whatsapp_id=from_id, token=token, message=message)
    
    if call["status"] == "success":
        MessageFirebaseRepository().create_chat_message(from_id, to_number, message.text)
    
    return jsonify({"status": "ok", "message": "Mensaje enviado con éxito"}), 200


## -------- TODO: ##
def get_template_message_content(*args):
    return """☕✨ ¡Feliz Año Nuevo! ✨☕

Si llevas 2 o más cajas de nuestro café 3 en 1 o clásico, te damos un precio especial. 
La promo es hasta el 15 de enero. 🏃‍♀"""