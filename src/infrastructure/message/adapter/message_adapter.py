from injector import Module, inject, singleton

from src.domain.message.model.message import Message, Sender
from src.domain.message.port.message_repository import MessageRepository
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.messaging.mesaging_manager import MessagingManager


@singleton
class MessageWhatsAppApiAdapter(MessageRepository):
    @inject
    def __init__(
        self, messaging_manager: MessagingManager, logger: LogAppManager
    ) -> None:
        self.__messaging_manager = messaging_manager
        self.__logger = logger
        self.__logger.set_caller("MessageWhatsAppApiAdapter")

    def send_single_message(self, message: Message) -> str:
        try:
            sender = message.sender
            self.__messaging_manager.send_message(message, sender)
            return f"Message sent to {message.to} from {sender.from_identifier}"
        except Exception as e:
            return (
                f"Error sending message to {message.to} from {sender.from_identifier}"
            )

    def send_group_message(self, message: Message) -> str:
        return "Not implemented yet"


class MessageModule(Module):
    def configure(self, binder):
        binder.bind(MessageRepository, to=MessageWhatsAppApiAdapter)
