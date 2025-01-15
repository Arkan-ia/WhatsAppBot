from abc import ABC, abstractmethod
import json
from typing import Any, Dict, Generic, List, TypeVar

T = TypeVar("T")


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


class Message(ABC, Generic[T]):
    @property
    @abstractmethod
    def to(self) -> str:
        pass

    @to.setter
    @abstractmethod
    def to(self, to: str) -> None:
        pass

    @property
    @abstractmethod
    def sender(self) -> Sender:
        pass

    @sender.setter
    @abstractmethod
    def sender(self, sender: Sender) -> None:
        pass

    @abstractmethod
    def get_message(self) -> T:
        pass


class WhatsAppSender(Sender):
    @property
    def from_identifier(self) -> str:
        return self.__from_identifier

    @from_identifier.setter
    def from_identifier(self, from_identifier: str) -> None:
        self.__from_identifier = from_identifier

    @property
    def from_token(self) -> str:
        return self.__from_token

    @from_token.setter
    def from_token(self, from_token: str) -> None:
        self.__from_token = from_token


class TextMessage(Message[Dict[str, Any]]):
    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def to(self) -> str:
        return self.__to

    @to.setter
    def to(self, to: str) -> None:
        self.__to = to

    @property
    def sender(self) -> WhatsAppSender:
        return self.__sender

    @sender.setter
    def sender(self, sender: WhatsAppSender) -> None:
        self.__sender = sender

    def get_message(self) -> Dict[str, Any]:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.to,
            "type": "text",
            "text": {"body": self._message},
        }


class TemplateMessage(Message[Dict[str, Any]]):

    @property
    def to(self) -> str:
        return self.__to

    @to.setter
    def to(self, to: str) -> None:
        self.__to = to

    @property
    def sender(self) -> WhatsAppSender:
        return self.__sender

    @sender.setter
    def sender(self, sender: WhatsAppSender) -> None:
        self.__sender = sender

    @property
    def template(self) -> str:
        return self.__template

    @template.setter
    def template(self, template: str) -> None:
        self.__template = template

    @property
    def code(self) -> str:
        return self.__code

    @code.setter
    def code(self, code: str) -> None:
        self.__code = code

    def get_message(self) -> Dict[str, Any]:
        return {
            "messaging_product": "whatsapp",
            "to": self.__to,
            "type": "template",
            "template": {"name": self.__template, "language": {"code": self.__code}},
        }
