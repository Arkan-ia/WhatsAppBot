from flask import Blueprint, request

from src.application.chat.command.chat_with_lead_command import (
    MetaWebhookSchema,
)
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.webhook.controller.schemas import (
    StatusUpdateSchema,
    StatusChangeSchema,
    SuccessfullSentMessageSchema,
)
from src.views.whatsapp_webhook import process_message, verify
from src.infrastructure.di.container import handler_chat_with_costumer

from src.infrastructure.di.container import injector


webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")
logger: LogAppManager = injector.get(LogAppManager)
logger.set_caller("/Webhook")


@webhook_bp.get("/")
def verify_connection():
    return verify()


schemas = [
    {
        "name": "Incomming message",
        "schema": MetaWebhookSchema(),
        "action": lambda command: handler_chat_with_costumer.run(command),
    },
    {
        "name": "Status update",
        "schema": StatusUpdateSchema(),
        "action": lambda command: ("ok", 200),
    },
    {
        "name": "Status change",
        "schema": StatusChangeSchema(),
        "action": lambda command: ("ok", 200),
    },
    {
        "name": "Successfull sent message",
        "schema": SuccessfullSentMessageSchema(),
        "action": lambda command: ("ok", 200),
    },
]


@webhook_bp.post("/")
def chat():
    error_message: str
    error: Exception
    # Iterate over schemas to check if request is valid and execute action
    # To avoid logging of inccomming request
    for schema in schemas:
        name = schema["name"]
        try:
            command = schema["schema"].load(request.get_json())
            result = schema["action"](command)
            return result
        except Exception as e:
            error_message = f"Error loading {name} schema"
            error = e

    logger.error(error_message, error)
