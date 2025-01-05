from abc import ABC, abstractmethod


class GPTManager(ABC):
  @abstractmethod
  def send_message(self, message: str) -> str:
    pass
  
  @abstractmethod
  def send_mesages(self, messages: list) -> str:
    pass