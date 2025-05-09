from abc import ABC, abstractmethod
from typing import List


class MessageRepository(ABC):
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
    def update_message(self, user_id, phone_number, message, role, **kwargs):
        pass

    @abstractmethod
    def delete_message(self, user_id, phone_number, message, role, **kwargs):
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
            ws_id= ws_id,
            phone_number= phone_number,
            message= message,
            role="tool",
            tool_call_id=tool_call_id,
            name=function_name,
            content=function_response,
            **kargs,
        )

    @abstractmethod
    def store_tool_call_responses(self, from_id, response, number):
        pass
