from abc import ABC, abstractmethod
import json
from typing import Generic, TypeVar
from typing import Dict, Any, List

T = TypeVar('T')

class Message(ABC, Generic[T]):
  @property
  @abstractmethod
  def to(self) -> str:
    pass
  
  @to.setter
  @abstractmethod
  def to(self, to: str) -> None:
    pass
  
  @abstractmethod
  def get_message(self) -> T:
    pass

class Sender(ABC):
  @property
  @abstractmethod
  def from_identifier(self) -> str:
    """In case of whatsapp oficial api, this is the whatsapp_id"""
    pass
  @from_identifier.setter
  @abstractmethod
  def from_identifier(self, from_identifier: str) -> None:
    pass
  
  @property
  @abstractmethod
  def from_token(self) -> str:
    """In case of whatsapp oficial api, this is the token"""
    pass
  
  @from_token.setter
  @abstractmethod
  def from_token(self, from_token: str) -> None:
    pass

class WhatsAppSender(Sender):
  @property
  def from_identifier(self) -> str:
    return self._from_identifier
  @from_identifier.setter
  def from_identifier(self, from_identifier: str) -> None:
    self._from_identifier = from_identifier
    
  @property
  def from_token(self) -> str:
    return self._from_token
  @from_token.setter
  def from_token(self, from_token: str) -> None:
    self._from_token = from_token

class TextMessage(Message[Dict[str, Any]]):
  def __init__(self, message: str) -> None:
    self._message = message

  @property
  def to(self) -> str:
    return self._to
  
  @to.setter
  def to(self, to: str) -> None:
    self._to = to

  @property
  def from_identifier(self) -> str:
    return self._from_identifier
  
  @from_identifier.setter
  def from_identifier(self, from_identifier: str) -> None:
    self._from_identifier = from_identifier
    
  def get_message(self) -> Dict[str, Any]:
    return json.dumps({
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": self.to,
      "type": "text",
      "text": {"body": self._message},
    })