from abc import ABC, abstractmethod, ab

from injector import inject

from src.infrastructure.shared.http.http_manager import HttpManager
from src.infrastructure.shared.messaging.message import Message, Sender


class MessagingManager(ABC):
  @abstractmethod
  def send_message(self, message: Message, sender: Sender) -> str:
    pass
  
class WhatsAppMessagingManager(MessagingManager):
  @inject
  def __init__(self, http_manager: HttpManager) -> None:
    http_manager.set_base_url("https://graph.facebook.com/v21.0")
    self.__http_manager = http_manager
    
  def send_message(self, message: Message, sender: Sender) -> str:
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {sender.from_token}"
    }

    try:
      response = self.__http_manager.post(
        f"/{sender.from_identifier}/messages",
        message.get_message(),
        headers=headers
      )
      if response.statuscode != 200:
        print(response.json())
        raise Exception(f"Failed to send message. Status code: {response.statuscode}")

      return response
    except Exception as e:
      print(e)
      raise e