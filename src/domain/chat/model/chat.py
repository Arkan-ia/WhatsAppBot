from enum import Enum

from src.domain.message.model.message import Sender


class Status(Enum):
    READ = "read"


class MessageType(Enum):
    TEXT = "text"
    REACTION = "reaction"


class Chat:
    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, message: str) -> None:
        self.__message = message

    @property
    def status(self) -> Status:
        return self.__status

    @status.setter
    def status(self, status: Status) -> None:
        self.__status = status

    @property
    def sender(self) -> Sender:
        return self.__sender

    @sender.setter
    def sender(self, sender: Sender) -> None:
        self.__sender = sender

    @property
    def message_type(self) -> MessageType:
        return self.__message_type

    @message_type.setter
    def message_type(self, message_type: MessageType) -> None:
        self.__message_type = message_type
