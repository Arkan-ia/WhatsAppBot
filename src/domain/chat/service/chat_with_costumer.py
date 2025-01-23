from injector import inject

from src.domain.chat.model.chat import Chat
from src.domain.chat.port.chat_repository import ChatRepository


class ChatWithCostumerService:
    @inject
    def __init__(self, chat_repository: ChatRepository) -> None:
        self.__chat_repository = chat_repository

    def run(self, chat: Chat) -> str:
        print(chat)
        # return self.__chat_repository.chat_with_customer(message, business_id)
