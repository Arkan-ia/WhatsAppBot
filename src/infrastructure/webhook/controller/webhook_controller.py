from flask import Blueprint, request

from src.application.chat.command.chat_with_lead_command import (
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
    command = MetaWebhookSchema().load(request.get_json())
    return handler_chat_with_costumer.run(command)
