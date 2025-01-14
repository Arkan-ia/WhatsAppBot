from abc import ABC, abstractmethod
from typing import List

from src.domain.message.model.message import Message, Sender


class MessageRepository(ABC):
    @abstractmethod
    def send_single_message(self, message: Message) -> str:
        pass

    @abstractmethod
    def send_group_message(self, message: List[Message]) -> str:
        pass
