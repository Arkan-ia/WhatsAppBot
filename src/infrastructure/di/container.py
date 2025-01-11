from injector import Injector

from src.domain.chat.service.chat_with_costumer import ChatWithCostumerService
from src.infrastructure.chat.adapter.module import ChatModule
from src.infrastructure.shared.http.http_manager import HttpManager, HttpModule
from src.infrastructure.shared.logger.logger import LogAppManager, LoggerModule
from src.services.chat_service import ChatbotService

injector = Injector([ChatModule, HttpModule, LoggerModule])

# Services
chatbot_service: ChatWithCostumerService = injector.get(ChatWithCostumerService)

# Shared deps and singletons
http_manager: HttpManager = injector.get(HttpManager)
