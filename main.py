from dotenv import load_dotenv

from src.common.utils.notifications import send_email_notification
from src.infrastructure.shared.middlewares.register import register_middlewares
from src.views.whatsapp_webhook import *

load_dotenv()
from flask import Flask, Request, jsonify
from flask_cors import CORS
import pandas as pd

from src.common.utils.notifications import send_email_notification
from src.infrastructure.chat.controller.chat_controller import chat_bp
from src.infrastructure.message.controller.mesage_controller import message_bp
from src.infrastructure.webhook.controller.webhook_controller import webhook_bp
from src.views.whatsapp_webhook import *

app = Flask(__name__)
CORS(app)
register_middlewares(app)

# def handle_massive_send(request):
#     """
#     Maneja la carga y procesamiento del archivo Excel para envío masivo.
#     """
#     if 'file' not in request.files:
#         return {"error": "No se encontró un archivo en la solicitud"}, 400

#     file = request.files['file']
#     if file.filename == '':
#         return {"error": "El archivo está vacío"}, 400

#     return process_excel_file(file)

# def process_excel_file(file_stream):
#     """
#     Procesa el archivo Excel cargado y extrae los datos relevantes desde el flujo.
#     """
#     try:
#         data = pd.read_excel(file_stream, header=None)

#         users = data[0].tolist()
#         return {"users": users}, 200
#     except Exception as e:
#         return {"error": f"Error procesando el archivo: {str(e)}"}, 500

# def main(request: Request):
#     """
#     Esta función maneja todas las solicitudes HTTP entrantes.
#     """

#     headers = {
#         'Access-Control-Allow-Origin': '*',
#         'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
#         'Access-Control-Allow-Headers': 'Content-Type'
#     }
#     if request.method == 'OPTIONS':
#         return ('', 204, headers)

#     with app.app_context():
#         if request.path == '/' and request.method == 'GET':
#             return verify()

#         elif request.path == '/' and request.method == 'POST':
#             return process_message()

#         elif request.path == '/send-template' and request.method == 'POST':
#             return send_template_message()

#         elif request.path == '/send-message' and request.method == 'POST':
#             return send_message()

#         elif request.path == '/send-email' and request.method == 'GET':
#             return send_email_notification("kevinskate.kg@gmail.com", "Cuerpo del email", "Prueba")

#         elif request.path == '/ping' and request.method == 'GET':
#             return jsonify({"message": "pong"}), 200

#         elif request.path == '/send-message/massive' and request.method == 'POST':
#             return send_massive_message()

#         else:
#             print("Ruta no encontrada + " + request.path)
#             return 'Ruta no encontrada', 404

# app.add_url_rule('/<path:path>', 'main', lambda path: main(request), methods=['GET', 'POST', 'OPTIONS'])
# app.add_url_rule('/', 'main_root', lambda: main(request), methods=['GET', 'POST', 'OPTIONS'])

app.register_blueprint(chat_bp)
app.register_blueprint(message_bp)
app.register_blueprint(webhook_bp)
app.get("/ping")(lambda: "pong")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
