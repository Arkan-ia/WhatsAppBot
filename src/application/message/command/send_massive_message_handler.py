from injector import inject, singleton

from src.application.message.command.send_message_command import SendMessageCommand
from src.domain.message.model.message import (
    Message,
    TemplateMessage,
    TextMessage,
    WhatsAppSender,
)
from src.domain.message.service.send_massive import SendMassiveMesageService


@singleton
class HandlerSendMassiveMessage:
    @inject
    def __init__(self, message_service: SendMassiveMesageService):
        self.__message_service = message_service

    def run(self, command: SendMessageCommand):
        sender = WhatsAppSender()
        sender.from_identifier = command["from_id"]
        sender.from_token = command["token"]

        message: Message = TextMessage(message=command["message"])
        message.sender = sender
        message.to = ""

        if command["template"]:
            message = TemplateMessage()
            message.sender = sender
            message.to = ""
            message.template = command["template"]
            message.code = command["language_code"]

        return self.__message_service.run(message, command["file"])
