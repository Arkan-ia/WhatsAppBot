from db.firebase import add_chat_message
from flask import jsonify, request
import os
import logging
from src.chatbot_router import get_chatbot_from_number
from src.whatsapp_api_handler import WhatsAppAPIHandler
from utils.whatsapp_utils import is_valid_whatsapp_message

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
    
def handle_incoming_message():
    body = request.get_json()

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200
    
    entry = body['entry'][0]
    changes = entry['changes'][0]
    value = changes['value']
    message = value['messages'][0]
    from_id = value["metadata"]["phone_number_id"]

    try:
        if is_valid_whatsapp_message(body):

            chatbot = get_chatbot_from_number(from_id)
            chatbot.handle_incoming_message(message)

            return jsonify({"status": "ok", "message": "Mensaje enviado con éxito"}), 200
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


def start_conversation():
    try:
        body = request.get_json()
        if not body:
            return jsonify({"status": "error", "message": "No se proporcionó cuerpo JSON"}), 400

        to_number = body.get('to_number')
        from_id = body.get('from_id')
        token = body.get('token')
        template = body.get('template')
        
        bot = WhatsAppAPIHandler(api_url=f"https://graph.facebook.com/v21.0/{from_id}/messages", token=token)

        if not to_number or not from_id:
            return jsonify({"status": "error", "message": "Faltan parámetros requeridos"}), 400

        bot.start_conversation(template=template, to_number=to_number, from_id=from_id)
        
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
    
    bot = WhatsAppAPIHandler(api_url=f"https://graph.facebook.com/v21.0/{from_id}/messages", token=token)
    
    data = bot.text_message(to_number, message)
    bot.send_whatsapp_message(data)

    add_chat_message(from_id, to_number, message)
    
    return jsonify({"status": "ok", "message": "Mensaje enviado con éxito"}), 200
