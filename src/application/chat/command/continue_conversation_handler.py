from injector import inject, singleton


from src.application.chat.command.continue_conversation_command import (
    ContinueConversationCommand,
)
from src.application.message.command.send_message_command import SendMessageCommand
from src.domain.business.model.business import Business
from src.domain.chat.model.chat import Chat, MessageType
from src.domain.chat.service.continue_conversation import ContinueConversationService
from src.domain.lead.model.lead import Lead


@singleton
class HandlerContinueConversation:
    @inject
    def __init__(self, continue_conversation_service: ContinueConversationService):
        self.__continue_conversation_service = continue_conversation_service

    def run(self, command: ContinueConversationCommand):

        return self.__continue_conversation_service.run(
            command.get("business_id"), command.get("lead_id")
        )
