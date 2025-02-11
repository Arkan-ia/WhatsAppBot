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
from src.domain.message.port.message_repository import MessageRepository, TimeUnits
from src.infrastructure.shared.logger.logger import LogAppManager


@singleton
class ChatWithLeadService:
    @inject
    def __init__(
        self,
        chat_repository: ChatRepository,
        business_repository: BusinessRepository,
        message_repository: MessageRepository,
        lead_repository: LeadRepository,
        logger: LogAppManager,
    ) -> None:
        self.__chat_repository = chat_repository
        self.__business_repository = business_repository
        self.__message_repository = message_repository
        self.__lead_repository = lead_repository
        self.__logger = logger
        self.__logger.set_caller("ChatWithLeadService")

    def run(self, chat: Chat) -> str:
        ## TODO: add toll calls to send to bot
        business_id = chat.business.id

        is_valid_lead = chat.lead.is_valid_phone_number()
        if not is_valid_lead:
            raise InvalidPhoneNumberError(chat.lead.phone_number)

        exists_business = self.__business_repository.exists(business_id)
        if not exists_business:
            raise BusinessNotFoundError(business_id)

        exists_lead = self.__lead_repository.exists(chat.lead.phone_number, business_id)
        if not exists_lead:
            self.__logger.info(
                f"Saving lead {chat.lead.phone_number} to business {business_id}"
            )
            chat.lead.last_message = {
                "content": chat.message,
                "status": "pending",
            }
            self.__lead_repository.save(chat.lead, business_id)

        exist_chat = self.__chat_repository.exists(chat)
        if not exist_chat:
            self.__logger.info(
                f"Creating chat for lead {chat.lead.phone_number} and business {business_id}"
            )
            self.__chat_repository.create(chat, "whatsapp")

        is_reaction_mesage = chat.message_type == MessageType.REACTION
        if is_reaction_mesage:
            return "Ok", 200

        messages = self.__message_repository.get_messages(
            business_id, chat.lead.phone_number, 10
        )
        # TODO: define a logic of fallback to prevent answer multiple times
        # TODO: validate if message_id already exist, to prevent answer old messages

        token = self.__business_repository.get_token_by_id(business_id)
        sender: Sender = WhatsAppSender()
        sender.from_token = token
        sender.from_identifier = chat.business.id
        message: Message = ReadMessage()
        message.sender = sender
        message.message_id = chat.message_id
        message.to = chat.lead.phone_number
        message.content = chat.message
        message.metadata = {}

        self.__message_repository.mark_message_as_read(message)

        agent_response = self.__chat_repository.chat_with_agent(chat, messages)

        reply_message: Message = TextMessage()
        reply_message.content = agent_response.content
        reply_message.sender = sender
        reply_message.to = chat.lead.phone_number
        reply_message.message_id = chat.message_id
        reply_message.metadata = agent_response.to_dict()
        reply_message.message_id = chat.message_id

        self.__message_repository.save_message(message, "user", "whatsapp")
        self.__message_repository.send_single_message(reply_message)
        self.__message_repository.program_later_message(
            reply_message, {TimeUnits.HOURS: 1}
        )

        return "ok", 200
