from abc import ABC, abstractmethod


class ChatRepository(ABC):
  @abstractmethod
  def chat_with_customer(self, message: str, market_id: str) -> str:
    pass
