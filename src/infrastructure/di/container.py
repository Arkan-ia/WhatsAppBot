from injector import Injector

from src.application.chat.command.continue_conversation_handler import (
    HandlerContinueConversation,
)
from src.application.message.command.send_massive_message_handler import (
    HandlerSendMassiveMessage,
)
from src.application.message.command.send_message_handler import HandlerSendMessage
from src.application.chat.command.chat_with_lead_handler import (
    HandlerChatWithLead,
)
from src.domain.chat.service.chat_with_lead import ChatWithLeadService
from src.domain.chat.service.continue_conversation import ContinueConversationService
from src.domain.message.service.send_massive import SendMassiveMesageService
from src.domain.message.service.send_single import SendSingleMesageService
from src.infrastructure.business.adapter.business_adapter import BusinessModule
from src.infrastructure.chat.adapter.chat_adapter import ChatModule
from src.infrastructure.lead.adapter.lead_adapter import LeadModule
from src.infrastructure.message.adapter.message_adapter import MessageModule
from src.infrastructure.shared.gpt.gpt_manager import GPTManagerModule
from src.infrastructure.shared.http.http_manager import HttpManager, HttpModule
from src.infrastructure.shared.logger.logger import LoggerModule
from src.infrastructure.shared.messaging.messaging_manager import MessagingManagerModule
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRelationalDBModule,
)
from src.infrastructure.shared.vectorstore.vector_store_manager import VectorStoreModule

injector = Injector(
    [
        ChatModule,
        HttpModule,
        LoggerModule,
        MessageModule,
        MessagingManagerModule,
        NoRelationalDBModule,
        BusinessModule,
        VectorStoreModule,
        GPTManagerModule,
        LeadModule,
    ]
)

# Services
send_single_message_service: SendSingleMesageService = injector.get(
    SendSingleMesageService
)
send_massive_message_service: SendMassiveMesageService = injector.get(
    SendMassiveMesageService
)
chat_with_lead_service: ChatWithLeadService = injector.get(ChatWithLeadService)
continue_conversation_service: ContinueConversationService = injector.get(
    ContinueConversationService
)
# Handlers
handler_send_message: HandlerSendMessage = HandlerSendMessage(
    send_single_message_service
)
handler_send_massive_message: HandlerSendMassiveMessage = HandlerSendMassiveMessage(
    send_massive_message_service
)
handler_chat_with_costumer: HandlerChatWithLead = HandlerChatWithLead(
    chat_with_lead_service
)
handler_continue_conversation: HandlerContinueConversation = (
    HandlerContinueConversation(continue_conversation_service)
)


# Shared deps and singletons
http_manager: HttpManager = injector.get(HttpManager)
