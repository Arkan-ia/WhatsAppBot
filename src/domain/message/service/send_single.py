from injector import inject, singleton

from src.domain.business.port.business_repository import BusinessRepository
from src.domain.errors.business_not_found import BusinessNotFoundError
from src.domain.message.model.message import Message
from src.domain.message.port.message_repository import MessageRepository


@singleton
class SendSingleMesageService:
    @inject
    def __init__(
        self,
        message_repository: MessageRepository,
        business_repository: BusinessRepository,
    ):
        self.__message_repository = message_repository
        self.__business_repository = business_repository

    def run(self, message: Message):
        if not self.__business_repository.exists(message.sender.from_identifier):
            raise BusinessNotFoundError(message.sender.from_identifier)

        return self.__message_repository.send_single_message(message)
