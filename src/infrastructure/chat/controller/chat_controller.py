from flask import Blueprint, jsonify, request
from src.infrastructure.di.container import handler_continue_conversation
from src.application.chat.command.continue_conversation_command import (
    ContinueConversationCommand,
)
from src.views.whatsapp_webhook import process_message

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.post("/")
def chat():
    # TODO: Replace with a service call
    # TODO: Add config with flask
    return process_message()


@chat_bp.post("/continue-conversation")
def continue_whatsapp_conversation():
    body = request.get_json()
    command = ContinueConversationCommand().load(body)
    return handler_continue_conversation.run(command)
