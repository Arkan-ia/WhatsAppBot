from abc import ABC, abstractmethod
from typing import List


class MessageRepository(ABC):
    @abstractmethod
    def create_message(self, user_id, phone_number, message, role, **kwargs):
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

    def create_contact_message(self, ws_id, phone_number, message, **kargs):
        self.create_message(ws_id, phone_number, message, "user", **kargs)

    def create_chat_message(self, ws_id, phone_number, message, tool_calls=None, message_id=""):
        self.create_message(
            ws_id, phone_number, message, "assistant", tool_calls=tool_calls, message_id=message_id
        )

    def create_tool_message(
        self,
        ws_id,
        phone_number,
        message,
        tool_call_id,
        function_name,
        function_response,
        **kargs
    ):

        self.create_message(
            ws_id,
            phone_number,
            message,
            "tool",
            tool_call_id=tool_call_id,
            name=function_name,
            content=function_response,
            **kargs
        )

    @abstractmethod
    def store_tool_call_responses(self, from_id, response, number):
        pass
