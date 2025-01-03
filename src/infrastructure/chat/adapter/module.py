from injector import Module, singleton

from src.domain.chat.port.chat_repository import ChatRepository
from src.infrastructure.chat.adapter.chat_adapter import ChatAdapter


class ChatModule(Module):
  def configure(self, binder):
    binder.bind(ChatRepository, to=ChatAdapter, scope=singleton)