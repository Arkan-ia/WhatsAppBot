#app.py
import json
import logging
from flask import Flask, jsonify, request
import os

import requests
import chatbot
from chatbot import bot
from db.firebase import add_chat_message
import templates
from utils.whatsapp import send_initial_message  

app = Flask(__name__)


@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == os.getenv('TOKEN') and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
      
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]

        chatbot.handle_incoming_message(message)
        return 'enviado'

    except Exception as e:
        print('Exception in recibir_mensajes:', str(e))
        return 'no enviado ' + str(e)

@app.route('/start-conversation', methods=['POST'])
def init_conversation():
    try:
        body = request.get_json()
        if not body:
            return jsonify({"status": "error", "message": "No se proporcionó cuerpo JSON"}), 400

        to_number = body.get('to_number')
        from_id = body.get('from_id')

        if not to_number or not from_id:
            return jsonify({"status": "error", "message": "Faltan parámetros requeridos"}), 400

        template = templates.hello_world
        send_initial_message(template=template, to_number=to_number, from_id=from_id)
        
        return jsonify({
            "status": "ok",
            "message": f"Conversación iniciada con éxito para el número {to_number}"
        }), 200
    except Exception as e:
        logging.error(f"Error al iniciar la conversación: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500



@app.route('/send-message', methods=['POST'])

def send_message():
    body = request.get_json()
    to_number = body.get('to_number')
    from_id = body.get('from_id')
    message = body.get('message')

    if not to_number or not from_id or not message:
        return jsonify({"status": "error", "message": "Faltan parámetros requeridos"}), 400
    
    data = text_message(to_number, message)
    send_whatsapp_message(data)

    add_chat_message(from_id, to_number, message)
    
    return jsonify({"status": "ok", "message": "Mensaje enviado con éxito"}), 200


if __name__ == '__main__':
    app.run()




def send_whatsapp_message(self, data: str) -> None:
        """
        Send a message through the WhatsApp API.

        Args:
            data (str): The JSON-formatted message data.
        """
        try:
            response = requests.post(self.api_url, headers=self.headers, data=data)

            if response.status_code == 200:
                logging.info("Message sent successfully.")
            else:
                logging.error(
                    f"Error sending message: {response.status_code}, {response.text}"
                )
        except Exception as e:
            logging.exception(f"Exception occurred while sending message: {e}")

    # Message Creation Methods

def text_message(self, number: str, text: str) -> str:
    """
    Create a text message in JSON format.

    Args:
        number (str): The recipient's phone number.
        text (str): The message text.

    Returns:
        str: The JSON-formatted message data.
    """
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {"body": text},
        }
    )
    return data
