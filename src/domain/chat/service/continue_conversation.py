from injector import inject, singleton

from src.domain.business.model.business import Business
from src.domain.business.port.business_repository import BusinessRepository
from src.domain.chat.model.chat import Chat, MessageType
from src.domain.chat.port.chat_repository import ChatRepository
from src.domain.errors.business_not_found import BusinessNotFoundError
from src.domain.errors.invalid_phone_number import InvalidPhoneNumberError
from src.domain.lead.model.lead import Lead
from src.domain.lead.port.lead_repository import LeadRepository
from src.domain.message.model.message import (
    Message,
    ReadMessage,
    Sender,
    WhatsAppSender,
    TextMessage,
)
from src.domain.message.port.message_repository import MessageRepository
from src.infrastructure.shared.logger.logger import LogAppManager


@singleton
class ContinueConversationService:
    @inject
    def __init__(
        self,
        chat_repository: ChatRepository,
        business_repository: BusinessRepository,
        message_repository: MessageRepository,
        logger: LogAppManager,
    ) -> None:
        self.__chat_repository = chat_repository
        self.__business_repository = business_repository
        self.__message_repository = message_repository
        self.__logger = logger
        self.__logger.set_caller("ContinueConversationService")

    def run(self, business_id: str, lead_id: str):
        messages = self.__message_repository.get_messages(business_id, lead_id, 5)
        should_reply, message = self.__chat_repository.continue_conversation(
            messages, business_id
        )
        if not should_reply:
            return "ok", 200

        token = self.__business_repository.get_token_by_id(business_id)

        sender: Sender = WhatsAppSender()
        sender.from_identifier = business_id
        sender.from_token = token

        text_message: Message = TextMessage()
        text_message.content = message
        text_message.to = lead_id
        text_message.sender = sender
        text_message.metadata = {}
        text_message.message_id = ""  # ._.

        self.__message_repository.send_single_message(text_message)

        return "ok", 200
