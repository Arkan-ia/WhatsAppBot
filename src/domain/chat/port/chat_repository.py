from abc import ABC, abstractmethod

from src.domain.chat.model.chat import Chat


class ChatRepository(ABC):
    @abstractmethod
    def chat_with_customer(self, chat: Chat) -> str:
        pass
