from injector import Injector

from src.domain.chat.service.chat_with_costumer import ChatWithCostumerService
from src.infrastructure.chat.adapter.module import ChatModule
from src.infrastructure.shared.http.http_manager import HttpManager, HttpModule
from src.services.chat_service import ChatbotService


injector = Injector([ChatModule, HttpModule])

# Services
chatbot_service: ChatWithCostumerService = injector.get(ChatWithCostumerService)

# Shared deps
http_manager: HttpManager = injector.get(HttpManager)