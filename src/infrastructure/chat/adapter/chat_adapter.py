from typing import List
from unittest.mock import MagicMock
from injector import Module, inject, singleton
from src.common.open_ai_tools import get_notify_payment_mail_tool
from src.domain.chat.model.chat import Chat
from src.domain.chat.port.chat_repository import ChatRepository
from src.domain.message.model.message import Message
from src.infrastructure.shared.gpt.gpt_manager import GPTManager
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


@singleton
class ChatAdapter(ChatRepository):
    @inject
    def __init__(self, logger: LogAppManager, gpt_manager: GPTManager):
        self.__logger = logger
        self.__logger.set_caller("ChatAdapter")
        self.__gpt_manager = gpt_manager
        self.__gpt_manager.set_tools([get_notify_payment_mail_tool()])

    def chat_with_customer(self, chat: Chat, messages: List[Message]) -> str:
        for m in messages:
            print("->", m.metadata)
        response = self.__gpt_manager.process_messages(
            # TODO: Replace with messages got from db
            messages=[
                {
                    "role": "user",
                    "content": "Hola, ¿qué productos tienes para mejorar mi circulación?",
                }
            ],
            query=chat.message,
            gpt_id=chat.business.id,
            relevant_promt_data="",
        )
        return response


ChatAdapterMock = MagicMock()


class ChatModule(Module):
    @flexible_bind_wrapper(
        interface=ChatRepository, to=ChatAdapter, mock=ChatAdapterMock
    )
    def configure(self, binder):
        return
