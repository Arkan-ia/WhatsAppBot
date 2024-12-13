from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from src.utils.notifications import send_email_notification
from src.views.whatsapp_webhook import *

load_dotenv()

app = Flask(__name__)
CORS(app)

# Ruta para verificar el webhook
@app.route('/', methods=['GET'])
def verify_route():
    print("in verify  ----------------->")
    return verify()

# Ruta para manejar POST en '/'
@app.route('/', methods=['POST'])
def handle_message_route():
    print("in handle message  ----------------->")
    return process_message()

# Ruta para el ping
@app.route('/ping', methods=['GET'])
def ping_route():
    return jsonify({"message": "pong"}), 200

# Ruta para iniciar conversación
@app.route('/start-conversation', methods=['POST'])
def start_conversation_route():
    return start_conversation()

# Ruta para enviar mensaje
@app.route('/send-message', methods=['POST'])
def send_message_route():
    return send_message()

@app.route('/send-email', methods=['GET'])
def send_email_route():
    return send_email_notification("kevinskate.kg@gmail.com", "Cuerpo del email", "Prueba")

@app.before_request
def before_request(): 
    print("before request")

# Manejo de CORS para OPTIONS
""" @app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
