from injector import inject, singleton

from src.domain.business.model.business import Business
from src.domain.business.port.business_repository import BusinessRepository
from src.domain.chat.model.chat import Chat, MessageType
from src.domain.chat.port.chat_repository import ChatRepository
from src.domain.errors.business_not_found import BusinessNotFoundError
from src.domain.lead.model.lead import Lead
from src.domain.message.model.message import (
    Message,
    ReadMessage,
    Sender,
    WhatsAppSender,
    TextMessage,
)
from src.domain.message.port.message_repository import MessageRepository


@singleton
class ChatWithLeadService:
    @inject
    def __init__(
        self,
        chat_repository: ChatRepository,
        business_repository: BusinessRepository,
        message_repository: MessageRepository,
    ) -> None:
        self.__chat_repository = chat_repository
        self.__business_repository = business_repository
        self.__message_repository = message_repository

    def run(self, chat: Chat) -> str:
        business_id = chat.business.id
        if not self.__business_repository.exists(business_id):
            raise BusinessNotFoundError(business_id)

        is_reaction_mesage = chat.message_type == MessageType.REACTION
        if is_reaction_mesage:
            return {
                "status": "ok",
            }, 200

        messages = self.__message_repository.get_messages(
            business_id, chat.lead.phone_number, 10
        )

        token = self.__business_repository.get_token_by_id(business_id)
        sender: Sender = WhatsAppSender()
        sender.from_token = token
        sender.from_identifier = chat.business.id
        message: Message = ReadMessage()
        message.sender = sender
        message.message_id = chat.message_id

        self.__message_repository.mark_message_as_read(message)

        # TODO: delete line
        chat.business.id = business_id
        agent_response = self.__chat_repository.chat_with_customer(chat, messages)

        reply_message: Message = TextMessage()
        reply_message.content = agent_response.content
        reply_message.sender = sender
        reply_message.to = chat.lead.phone_number
        reply_message.message_id = chat.message_id
        reply_message.metadata = agent_response.to_dict()
        self.__message_repository.send_single_message(reply_message)
        # self.__message_repository.save_message(reply_message, "assistant", "whatsapp")
        return "Ok", 200
