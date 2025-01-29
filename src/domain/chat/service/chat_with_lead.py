from injector import inject, singleton

from src.domain.business.model.business import Business
from src.domain.business.port.business_repository import BusinessRepository
from src.domain.chat.model.chat import Chat
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

    def run(self, lead: Lead, business: Business) -> str:
        print("Got chat", lead, business)

        if not self.__business_repository.exists(business.id):
            raise BusinessNotFoundError(business.id)
        return "Chat with costumer", 200
        # return self.__chat_repository.chat_with_customer(message, business_id)
