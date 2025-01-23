from flask import Blueprint, request

from src.application.chat.command.chat_with_costumer_command import (
    ChatWithCostumerCommand,
    MetaWebhookSchema,
)
from src.views.whatsapp_webhook import process_message, verify
from src.infrastructure.di.container import handler_chat_with_costumer


webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")


@webhook_bp.get("/")
def verify_connection():
    return verify()


@webhook_bp.post("/")
def chat():
    print("json", request.get_json())
    command = MetaWebhookSchema().load(request.get_json())
    print("command ->", command)
    return handler_chat_with_costumer.run(command)
