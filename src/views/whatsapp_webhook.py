from src.common.whatsapp.models.models import TemplateMessage, TextMessage
from flask import jsonify, request
import os
import logging
from src.chatbot_router import get_chatbot_from_number
from src.common.utils.whatsapp_utils import is_valid_whatsapp_message, send_whatsapp_message
from src.data.sources.firebase.message_impl import MessageFirebaseRepository

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

        return jsonify({
            "status": "ok",
            "message": f"Conversación iniciada con éxito para el número {to_number}"
        }), 200
    except Exception as e:
        logging.error(f"Error al iniciar la conversación: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


def send_message():
    body = request.get_json()
    to_number = body.get('to_number')
    from_id = body.get('from_id')
    token = body.get('token')
    message = body.get('message')

    if not to_number or not from_id or not message:
        return jsonify({"status": "error", "message": "Faltan parámetros requeridos"}), 400
    
    message = TextMessage(number=to_number, text=message)
    send_whatsapp_message(from_whatsapp_id=from_id, token=token, message=message)

    MessageFirebaseRepository().create_chat_message(from_id, to_number, message)
    
    return jsonify({"status": "ok", "message": "Mensaje enviado con éxito"}), 200
