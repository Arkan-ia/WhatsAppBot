from injector import inject, singleton

from src.application.message.command.send_message_command import SendMessageCommand
from src.domain.message.model.message import TextMessage, WhatsAppSender
from src.domain.message.service.send_single import SendSingleMesageService


@singleton
class HandlerSendMessage:
    @inject
    def __init__(self, message_service: SendSingleMesageService):
        self.__message_service = message_service

    def run(self, command: SendMessageCommand):
        sender = WhatsAppSender()
        sender.from_identifier = command.get("from_id")
        sender.from_token = command.get("token")

        message = TextMessage(message=command.get("message"))
        message.sender = sender
        message.to = command.get("to")
        return self.__message_service.run(message)
