from flask import Flask, Request
from flask_cors import CORS
from dotenv import load_dotenv
from views.whatsapp_webhook import *

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
            return handle_incoming_message()

        elif request.path == '/start-conversation' and request.method == 'POST':
            return start_conversation()

        elif request.path == '/send-message' and request.method == 'POST':
            return send_message()

        else:
            print("Ruta no encontrada + " + request.path)
            return 'Ruta no encontrada', 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
