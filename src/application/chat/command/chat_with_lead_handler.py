from injector import inject, singleton

from src.application.chat.command.chat_with_lead_command import (
    ChatWithLeadCommand,
)
from src.application.message.command.send_message_command import SendMessageCommand
from src.domain.business.model.business import Business
from src.domain.chat.model.chat import Chat, MessageType
from src.domain.chat.service.chat_with_lead import ChatWithLeadService
from src.domain.lead.model.lead import Lead


@singleton
class HandlerChatWithLead:
    @inject
    def __init__(self, chat_service: ChatWithLeadService):
        self.__chat_service = chat_service

    def run(self, command: ChatWithLeadCommand):
        lead = Lead()
        lead.name = command.get("lead").get("name")
        lead.phone_number = command.get("lead").get("phone_number")

        business = Business()
        business.name = command.get("business").get("name")
        business.id = command.get("business").get("id")

        chat = Chat()
        chat.lead = lead
        chat.business = business

        chat.message_type = MessageType(command.get("message_type"))
        chat.message = command.get("message_content")

        return self.__chat_service.run(chat)
