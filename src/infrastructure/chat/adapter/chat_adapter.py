from unittest.mock import MagicMock
from injector import Module, inject, singleton
from src.domain.chat.port.chat_repository import ChatRepository
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


@singleton
class ChatAdapter(ChatRepository):
    @inject
    def __init__(self, logger: LogAppManager):
        self.__logger = logger
        self.__logger.set_caller("ChatAdapter")

    def chat_with_customer(self, message: str, market_id: str) -> str:
        return f"Chat with customer {message} {market_id}"


ChatAdapterMock = MagicMock()


class ChatModule(Module):
    @flexible_bind_wrapper(
        interface=ChatRepository, to=ChatAdapter, mock=ChatAdapterMock
    )
    def configure(self, binder):
        return
