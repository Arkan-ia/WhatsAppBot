from abc import ABC, abstractmethod
from typing import List, Literal

from src.domain.message.model.message import Message


class MessageRepository(ABC):
    @abstractmethod
    def send_single_message(self, message: Message) -> str:
        pass

    @abstractmethod
    def send_massive_message(self, message: List[Message]) -> str:
        pass

    @abstractmethod
    def save_message(
        self,
        message: Message,
        role: Literal["user", "assistant"],
        platform: Literal["whatsapp"],
    ) -> str:
        pass

    @abstractmethod
    def get_template_data(self, business_id: str, template_name: str) -> str:
        pass

    @abstractmethod
    def create_message(
        conversation_ref,
        contact_ref,
        ws_id,
        phone_number,
        message,
        role,
        wa_id,
        **kwargs,
    ):
        pass

    @abstractmethod
    def get_message(self, msj_id):
        pass

    @abstractmethod
    def get_messages(self, user_id, phone_number) -> List:
        pass

    def create_contact_message(
        self,
        conversation_ref,
        contact_ref,
        ws_id,
        wa_id,
        phone_number,
        message,
        **kargs,
    ):
        self.create_message(
            conversation_ref=conversation_ref,
            contact_ref=contact_ref,
            ws_id=ws_id,
            phone_number=phone_number,
            message=message,
            wa_id=wa_id,
            role="user",
            **kargs,
        )

    def create_chat_message(
        self,
        conversation_ref,
        contact_ref,
        ws_id,
        phone_number,
        message,
        wa_id,
        tool_calls=None,
    ):
        self.create_message(
            conversation_ref=conversation_ref,
            contact_ref=contact_ref,
            ws_id=ws_id,
            phone_number=phone_number,
            message=message,
            role="assistant",
            tool_calls=tool_calls,
            wa_id=wa_id,
        )

    def create_tool_message(
        self,
        ws_id,
        phone_number,
        message,
        tool_call_id,
        function_name,
        function_response,
        contact_ref,
        conversation_ref,
        **kargs,
    ):

        self.create_message(
            conversation_ref=conversation_ref,
            contact_ref=contact_ref,
            wa_id="",
            ws_id=ws_id,
            phone_number=phone_number,
            message=message,
            role="tool",
            tool_call_id=tool_call_id,
            name=function_name,
            content=function_response,
            **kargs,
        )

    @abstractmethod
    def store_tool_call_responses(self, from_id, response, number):
        pass
