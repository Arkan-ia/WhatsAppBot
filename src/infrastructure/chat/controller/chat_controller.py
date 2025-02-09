from flask import Blueprint, jsonify, request

from src.views.whatsapp_webhook import process_message

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.post("/")
def chat():
    # TODO: Replace with a service call
    # TODO: Add config with flask
    return process_message()


@chat_bp.post("/continue-conversation")
def continue_whatsapp_conversation():
    # 1. Read conversation
    body = request.get_json()
    business_id = body.get("business_id")
    lead_id = body.get("lead_id")

    # 2. Decide if should reply

    # 3. Send message

    return jsonify({"status": "ok"}), 200
