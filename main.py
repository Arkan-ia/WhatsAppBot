from flask import Flask, jsonify, request,Request
from flask_cors import CORS
from dotenv import load_dotenv
from src.utils.notifications import send_email_notification
from src.views.whatsapp_webhook import *

load_dotenv()

app = Flask(__name__)
CORS(app)

def main(request: Request):
    """
    Esta función maneja todas las solicitudes HTTP entrantes.
    """

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    with app.app_context():
        if request.path == '/' and request.method == 'GET':
            return verify()

        elif request.path == '/' and request.method == 'POST':
            return process_message()

        elif request.path == '/start-conversation' and request.method == 'POST':
            return start_conversation()

        elif request.path == '/send-message' and request.method == 'POST':
            return send_message()
        
        elif request.path == '/send-email' and request.method == 'GET':
            return send_email_notification("kevinskate.kg@gmail.com", "Cuerpo del email", "Prueba")
        
        elif request.path == '/ping' and request.method == 'GET':
            return jsonify({"message": "pong"}), 200

        else:
            print("Ruta no encontrada + " + request.path)
            return 'Ruta no encontrada', 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
