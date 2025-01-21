from abc import ABC, abstractmethod
from typing import List, Literal

from src.domain.message.model.message import Message, Sender


class MessageRepository(ABC):
    @abstractmethod
    def send_single_message(self, message: Message) -> str:
        pass

    @abstractmethod
    def send_massive_message(self, message: List[Message]) -> str:
        pass

    @abstractmethod
    def save_message(
        self,
        message: Message,
        role: Literal["user", "assistant"],
        platform: Literal["whatsapp"],
    ) -> str:
        pass

    @abstractmethod
    def get_template_data(self, business_id: str, template_name: str) -> str:
        pass
