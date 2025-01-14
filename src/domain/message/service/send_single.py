from injector import inject, singleton

from src.domain.message.model.message import Message, Sender
from src.domain.message.port.message_repository import MessageRepository


@singleton
class SendSingleMesageService:
    @inject
    def __init__(self, message_repository: MessageRepository):
        self.__message_repository = message_repository

    def run(self, message: Message):
        return self.__message_repository.send_single_message(message)
