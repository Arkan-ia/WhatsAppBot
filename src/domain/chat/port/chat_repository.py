from abc import ABC, abstractmethod
from typing import List

from src.domain.chat.model.chat import Chat
from src.domain.message.model.message import Message


class ChatRepository(ABC):
    @abstractmethod
    def chat_with_customer(self, chat: Chat, messages: List[Message]) -> str:
        pass
