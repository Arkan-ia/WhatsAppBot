from abc import ABC, abstractmethod


class ChatRepository(ABC):
    @abstractmethod
    def chat_with_customer(self, message: str, business_id: str) -> str:
        pass
