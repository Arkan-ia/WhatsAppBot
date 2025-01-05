from flask import Blueprint

from src.views.whatsapp_webhook import process_message


chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.post('/')
def chat():
  # TODO: Replace with a service call
  # TODO: Add config with flask
  return process_message()