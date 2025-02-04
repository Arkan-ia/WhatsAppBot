from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

from src.domain.chat.model.chat import Chat
from src.domain.message.model.message import Message


class AgentResponse(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[str]]
    tool_call_id: Optional[str]
    function_name: Optional[str]
    function_response: Optional[str]
    message_id: str

    def __str__(self):
        return (
            f"{self.role}: {self.content}\n"
            f"Tool calls: {self.tool_calls}\n"
            f"Tool call id: {self.tool_call_id}\n"
            f"Function name: {self.function_name}\n"
            f"Function response: {self.function_response}\n"
            f"Message id: {self.message_id}\n"
        )

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id,
            "function_name": self.function_name,
            "function_response": self.function_response,
            "message_id": self.message_id,
        }


class ChatRepository(ABC):
    @abstractmethod
    def chat_with_customer(self, chat: Chat, messages: List[Message]) -> AgentResponse:
        pass
