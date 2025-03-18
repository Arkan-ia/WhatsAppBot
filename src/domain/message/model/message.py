from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar

from src.domain.chat.model.tool_call import ToolCall


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
    def content(self) -> str:
        pass

    @content.setter
    @abstractmethod
    def content(self, content: str) -> None:
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

    @property
    def message_id(self) -> str:
        pass

    @message_id.setter
    @abstractmethod
    def message_id(self, id: str) -> None:
        pass

    @property
    def metadata(self) -> Dict[str, Any]:
        pass

    @metadata.setter
    @abstractmethod
    def metadata(self, metadata: Dict[str, Any]) -> None:
        pass

    @property
    def tool_call(self) -> List[ToolCall]:
        pass

    @tool_call.setter
    @abstractmethod
    def tool_call(self, tool_call: List[ToolCall]) -> None:
        pass

    @property
    def role(self) -> str:
        pass

    @role.setter
    @abstractmethod
    def role(self, role: str) -> None:
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
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content

    @property
    def message_id(self) -> str:
        return self.__id

    @message_id.setter
    def message_id(self, id: str) -> None:
        self.__id = id

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.__metadata

    @metadata.setter
    def metadata(self, metadata: Dict[str, Any]) -> None:
        self.__metadata = metadata

    @property
    def tool_call(self) -> List[ToolCall]:
        return self.__tool_call

    @tool_call.setter
    def tool_call(self, tool_call: List[ToolCall]) -> None:
        self.__tool_call = tool_call

    @property
    def role(self) -> str:
        return self.__role

    @role.setter
    def role(self, role: str) -> None:
        self.__role = role

    def get_message(self) -> Dict[str, Any]:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.to,
            "type": "text",
            "text": {"body": self.__content},
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

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return self.__parameters

    @parameters.setter
    def parameters(self, parameters: List[Dict[str, Any]]) -> None:
        self.__parameters = parameters

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content

    @property
    def message_id(self) -> str:
        return self.__id

    @message_id.setter
    def message_id(self, id: str) -> None:
        self.__id = id

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.__metadata

    @metadata.setter
    def metadata(self, metadata: Dict[str, Any]) -> None:
        self.__metadata = metadata

    def get_message(self) -> Dict[str, Any]:
        template_object = {
            "name": self.__template,
            "language": {"code": self.__code},
        }
        if self.__parameters:
            template_object["components"] = [
                {"type": "header", "parameters": self.__parameters},
            ]
        return {
            "messaging_product": "whatsapp",
            "to": self.__to,
            "type": "template",
            "template": template_object,
        }


class ReadMessage(Message[Dict[str, Any]]):
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
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        self.__content = content

    @property
    def message_id(self) -> str:
        return self.__id

    @message_id.setter
    def message_id(self, id: str) -> None:
        self.__id = id

    @property
    def metadata(self) -> Dict[str, Any]:
        return getattr(self, "__metadata", {})

    @metadata.setter
    def metadata(self, metadata: Dict[str, Any]) -> None:
        self.__metadata = metadata

    @property
    def tool_call(self) -> List[ToolCall]:
        return getattr(self, "__tool_call", [])

    @tool_call.setter
    def tool_call(self, tool_call: List[ToolCall]) -> None:
        self.__tool_call = tool_call

    @property
    def role(self) -> str:
        return self.__role

    @role.setter
    def role(self, role: str) -> None:
        self.__role = role

    def get_message(self) -> Dict[str, Any]:
        return {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": self.__id,
        }
