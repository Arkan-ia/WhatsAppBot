from flask import Flask, jsonify, Request
from flask_cors import CORS
from dotenv import load_dotenv
from src.common.utils.notifications import send_email_notification
from src.views.whatsapp_webhook import *
import pandas as pd

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

        elif request.path == '/send-template' and request.method == 'POST':
            return send_template_message()

        elif request.path == '/send-message' and request.method == 'POST':
            return send_message()
        
        elif request.path == '/send-email' and request.method == 'GET':
            return send_email_notification("kevinskate.kg@gmail.com", "Cuerpo del email", "Prueba")
        
        elif request.path == '/ping' and request.method == 'GET':
            return jsonify({"message": "pong"}), 200
        
        elif request.path == '/send-message/massive' and request.method == 'POST':
            return send_massive_message()

        else:
            print("Ruta no encontrada + " + request.path)
            return 'Ruta no encontrada', 404

app.add_url_rule('/<path:path>', 'main', lambda path: main(request), methods=['GET', 'POST', 'OPTIONS'])
app.add_url_rule('/', 'main_root', lambda: main(request), methods=['GET', 'POST', 'OPTIONS']) 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    
