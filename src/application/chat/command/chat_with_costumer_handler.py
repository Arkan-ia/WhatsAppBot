from injector import inject, singleton

from src.application.chat.command.chat_with_costumer_command import (
    ChatWithCostumerCommand,
)
from src.application.message.command.send_message_command import SendMessageCommand
from src.domain.chat.model.chat import Chat
from src.domain.chat.service.chat_with_costumer import ChatWithCostumerService
from src.domain.message.service.send_massive import SendMassiveMesageService


@singleton
class HandlerChatWithCostumer:
    @inject
    def __init__(self, chat_service: ChatWithCostumerService):
        self.__chat_service = chat_service

    def run(self, command: ChatWithCostumerCommand):
        print("Command", command)
        chat = Chat()
        chat.message = command.get("message")
        chat.sender = command.get("sender")
        chat.message_type = command.get("message_type")
        chat.status = command.get("status")

        return self.__chat_service.run(command)
