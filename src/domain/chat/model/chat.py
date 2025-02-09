from enum import Enum

from src.domain.business.model.business import Business
from src.domain.lead.model.lead import Lead
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
    def business(self) -> Business:
        return self.__business

    @business.setter
    def business(self, business: Business) -> None:
        self.__business = business

    @property
    def lead(self) -> Lead:
        return self.__lead

    @lead.setter
    def lead(self, lead: Lead) -> None:
        self.__lead = lead

    @property
    def message_type(self) -> MessageType:
        return self.__message_type

    @message_type.setter
    def message_type(self, message_type: MessageType) -> None:
        self.__message_type = message_type

    @property
    def message_id(self) -> str:
        return self.__message_id

    @message_id.setter
    def message_id(self, message_id: str) -> None:
        self.__message_id = message_id
