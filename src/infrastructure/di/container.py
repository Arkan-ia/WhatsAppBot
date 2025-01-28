from injector import Injector

from src.application.message.command.send_massive_message_handler import (
    HandlerSendMassiveMessage,
)
from src.application.message.command.send_message_handler import HandlerSendMessage
from src.application.chat.command.chat_with_costumer_handler import (
    HandlerChatWithCostumer,
)
from src.domain.chat.service.chat_with_costumer import ChatWithCostumerService
from src.domain.message.service.send_massive import SendMassiveMesageService
from src.domain.message.service.send_single import SendSingleMesageService
from src.infrastructure.business.adapter.business_adapter import BusinessModule
from src.infrastructure.chat.adapter.chat_adapter import ChatModule
from src.infrastructure.message.adapter.message_adapter import MessageModule
from src.infrastructure.shared.http.http_manager import HttpManager, HttpModule
from src.infrastructure.shared.logger.logger import LoggerModule
from src.infrastructure.shared.messaging.mesaging_manager import MessagingManagerModule
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRelationalDBModule,
)

injector = Injector(
    [
        ChatModule,
        HttpModule,
        LoggerModule,
        MessageModule,
        MessagingManagerModule,
        NoRelationalDBModule,
        BusinessModule,
    ]
)

# Services
send_single_message_service: SendSingleMesageService = injector.get(
    SendSingleMesageService
)
send_massive_message_service: SendMassiveMesageService = injector.get(
    SendMassiveMesageService
)
chat_with_costumer_service: ChatWithCostumerService = injector.get(
    ChatWithCostumerService
)

# Handlers
handler_send_message: HandlerSendMessage = HandlerSendMessage(
    send_single_message_service
)
handler_send_massive_message: HandlerSendMassiveMessage = HandlerSendMassiveMessage(
    send_massive_message_service
)
handler_chat_with_costumer: HandlerChatWithCostumer = HandlerChatWithCostumer(
    chat_with_costumer_service
)


# Shared deps and singletons
http_manager: HttpManager = injector.get(HttpManager)
