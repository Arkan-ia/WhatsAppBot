from injector import inject

from src.domain.business.port.business_repository import BusinessRepository
from src.domain.chat.model.chat import Chat
from src.domain.chat.port.chat_repository import ChatRepository
from src.domain.errors.business_not_found import BusinessNotFoundError


class ChatWithCostumerService:
    @inject
    def __init__(
        self, chat_repository: ChatRepository, business_repository: BusinessRepository
    ) -> None:
        self.__chat_repository = chat_repository
        self.__business_repository = business_repository

    def run(self, chat: Chat) -> str:
        if not self.__business_repository.exists(chat.business_id):
            raise BusinessNotFoundError(chat.sender.from_identifier)
        print(chat)
        return "Chat with costumer", 200
        # return self.__chat_repository.chat_with_customer(message, business_id)
