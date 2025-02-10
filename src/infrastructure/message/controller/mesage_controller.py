import json
from typing import Any, Dict

from flask import Blueprint, jsonify, request

from src.application.message.command.send_massive_message_command import (
    SendMassiveMessageCommand,
)
from src.application.message.command.send_message_command import SendMessageCommand
from src.infrastructure.di.container import (
    handler_send_massive_message,
    handler_send_message,
)

message_bp = Blueprint("message", __name__, url_prefix="/message")


@message_bp.post("")
def send():
    command = SendMessageCommand().load(request.get_json())
    return handler_send_message.run(command)


@message_bp.post("/massive")
def send_massive():
    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400
    file = request.files["file"]
    form = request.form
    form_data: Dict[str, Any] = {
        "token": form["token"],
        "message": form["message"],
        "file": file,
        "from_id": form["from_id"],
        "template": form["template"],
        "language_code": form["language_code"],
    }

    if "parameters" in form:
        try:
            parameters_data = json.loads(request.form["parameters"])
            form_data["parameters"] = parameters_data
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for 'parameters'"}), 400

    command = SendMassiveMessageCommand().load(form_data)
    return handler_send_massive_message.run(command)




@message_bp.post("/single")
def send_single():
    ...
    # TODO: 1321
    
    
    # form_data: Dict[str, Any] = {
    #     "token": form["token"],
    #     "message": form["message"],
    #     "file": file,
    #     "from_id": form["from_id"],
    # }

    # if "parameters" in form:
    #     try:
    #         parameters_data = json.loads(request.form["parameters"])
    #         form_data["parameters"] = parameters_data
    #     except json.JSONDecodeError:
    #         return jsonify({"error": "Invalid JSON format for 'parameters'"}), 400

    # command = SendMassiveMessageCommand().load(form_data)
    # return handler_send_massive_message.run(command)
