from injector import inject

from src.domain.chat.port.chat_repository import ChatRepository

class ChatWithCostumerService:
  @inject
  def __init__(self, chat_repository: ChatRepository) -> None:
    self.__chat_repository = chat_repository

  def run(self, message: str, market_id: str) -> str:
    return self.__chat_repository.chat_with_customer(message, market_id)
