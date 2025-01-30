from injector import inject, singleton

from src.domain.business.model.business import Business
from src.domain.business.port.business_repository import BusinessRepository
from src.domain.chat.model.chat import Chat, MessageType
from src.domain.chat.port.chat_repository import ChatRepository
from src.domain.errors.business_not_found import BusinessNotFoundError
from src.domain.lead.model.lead import Lead


@singleton
class ChatWithLeadService:
    @inject
    def __init__(
        self, chat_repository: ChatRepository, business_repository: BusinessRepository
    ) -> None:
        self.__chat_repository = chat_repository
        self.__business_repository = business_repository

    def run(self, chat: Chat) -> str:
        # if not self.__business_repository.exists(chat.business.id):
        #     raise BusinessNotFoundError(chat.business.id)

        is_reaction_mesage = chat.message_type == MessageType.REACTION

        if is_reaction_mesage:
            return {
                "status": "ok",
            }, 200

        return self.__chat_repository.chat_with_customer(chat), 200
