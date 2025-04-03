from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel

from src.domain.chat.model.chat import Chat
from src.domain.chat.model.tool_call import ToolCall
from src.domain.message.model.message import Message


class AgentResponse(BaseModel):
    role: str
    content: Optional[str]
    message_id: str
    tool_calls: Optional[List[ToolCall]]
    has_tool_calls: bool

    def __str__(self):
        tool_calls = "\n ".join([str(tool_call) for tool_call in self.tool_calls])
        return (
            f"{self.role}: {self.content}\n"
            f"Tool calls: {tool_calls}\n"
            f"Message id: {self.message_id}\n"
        )

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "message_id": self.message_id,
        }


class ActionHandler(BaseModel):
    name: str
    description: str
    params: Dict[str, Dict[str, str]]
    required_params: List[str]
    handler: Any
    reply_to_costumer_message: str

    def __str__(self):
        return f"ActionHandler(name={self.name}, desciption={self.description}, params={self.params}, required_params={self.required_params}, handler={self.handler})"


class ChatRepository(ABC):
    @abstractmethod
    def chat_with_agent(
        self, chat: Chat, messages: List[Message], custom_prompt: Optional[str]
    ) -> AgentResponse:
        pass

    @abstractmethod
    def create(self, chat: Chat, platform: Literal["whatsapp"]) -> Chat:
        pass

    @abstractmethod
    def exists(self, chat: Chat) -> bool:
        pass

    @abstractmethod
    def continue_conversation(
        self, messages: List[Message], business_id: str
    ) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def set_action_handlers(self, action_handlers: List[ActionHandler]):
        pass
