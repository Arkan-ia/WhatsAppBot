from src.domain.chat.port.chat_repository import ChatRepository


class ChatAdapter(ChatRepository):
  def chat_with_customer(self, message: str, market_id: str) -> str:
    return f"Chat with customer {message} {market_id}"