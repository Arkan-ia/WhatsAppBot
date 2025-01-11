from flask import Blueprint

from src.views.whatsapp_webhook import process_message, send_massive_message

message_bp = Blueprint("message", __name__, url_prefix="/message")


@message_bp.post("/massive")
def chat():
    # TODO: Replace with a service call
    # TODO: Add config with flask
    return send_massive_message()
