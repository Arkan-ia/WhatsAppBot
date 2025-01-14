from flask import Blueprint, request

from src.application.message.command.send_message_command import SendMessageCommand
from src.infrastructure.di.container import handler_send_message
from src.views.whatsapp_webhook import process_message, send_massive_message

message_bp = Blueprint("message", __name__, url_prefix="/message")


@message_bp.post("")
def send():
    command = SendMessageCommand().load(request.get_json())
    return handler_send_message.run(command)


@message_bp.post("/massive")
def send_massive():
    return send_massive_message()
