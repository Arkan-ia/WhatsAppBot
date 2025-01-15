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
        return self.__message_service.run(command.get("file"), command)
