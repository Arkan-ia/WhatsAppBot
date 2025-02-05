from typing import Any, Dict, List
from unittest.mock import MagicMock
from injector import Module, inject, singleton
from src.common.open_ai_tools import get_notify_payment_mail_tool
from src.domain.chat.model.chat import Chat
from src.domain.chat.port.chat_repository import AgentResponse, ChatRepository
from src.domain.message.model.message import Message
from src.domain.message.port.message_repository import MessageRepository
from src.infrastructure.shared.gpt.gpt_manager import GPTManager
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


@singleton
class ChatAdapter(ChatRepository):
    @inject
    def __init__(
        self,
        logger: LogAppManager,
        gpt_manager: GPTManager,
        message_repository: MessageRepository,
    ):
        self.__logger = logger
        self.__logger.set_caller("ChatAdapter")
        self.__gpt_manager = gpt_manager
        self.__gpt_manager.set_tools([get_notify_payment_mail_tool()])

    def __get_tool_calls(self, obj: Dict[str, Any]):
        if obj.get("tool_calls") is not None:
            if len(obj.get("tool_calls")) > 0:
                return obj.get("tool_calls")
            return None
        return None

    def chat_with_customer(self, chat: Chat, messages: List[Message]) -> AgentResponse:
        messages_to_send = [
            {
                "role": m.metadata.get("role"),
                "content": m.metadata.get("content"),
                "function_call": m.metadata.get("function_call"),
                "function_name": m.metadata.get("function_name"),
                "function_response": m.metadata.get("function_response"),
                "tool_calls": self.__get_tool_calls(m.metadata),
            }
            for m in messages
        ]
        messages_to_send.append(
            {
                "role": "user",
                "content": chat.message,
            }
        )

        try:
            response = self.__gpt_manager.process_messages(
                messages=messages_to_send,
                query=chat.message,
                gpt_id=chat.business.id,
                relevant_promt_data="",
            )

            return response
        except Exception as e:
            self.__logger.error(f"Error generating answer: {str(e)}")
            raise e


ChatAdapterMock = MagicMock()


class ChatModule(Module):
    @flexible_bind_wrapper(
        interface=ChatRepository, to=ChatAdapter, mock=ChatAdapterMock
    )
    def configure(self, binder):
        return
