import json
from typing import Any, Dict, List, Literal, Optional, Tuple
from unittest.mock import MagicMock
from injector import Module, inject, singleton
from src.common.open_ai_tools import get_notify_payment_mail_tool
from src.domain.chat.model.chat import Chat
from src.domain.chat.port.chat_repository import AgentResponse, ChatRepository
from src.domain.message.model.message import Message
from src.domain.message.port.message_repository import MessageRepository
from src.infrastructure.shared.gpt.gpt_manager import GPTManager
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRealtionalDBManager,
)
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


@singleton
class ChatAdapter(ChatRepository):
    @inject
    def __init__(
        self,
        logger: LogAppManager,
        gpt_manager: GPTManager,
        no_rel_db: NoRealtionalDBManager,
    ):
        self.__logger = logger
        self.__logger.set_caller("ChatAdapter")
        self.__gpt_manager = gpt_manager
        self.__storage = no_rel_db

    def __get_tool_calls(self, obj: Dict[str, Any]):
        if obj.get("tool_calls") is not None:
            if len(obj.get("tool_calls")) > 0:
                return obj.get("tool_calls")
            return None
        return None

    def __parse_messages_to_openai(self, messages: List[Message]):
        parsed_messages = []
        for message in messages:
            tc = message.tool_call
            message = {
                "role": message.role,
                "content": message.content,
            }
            tool_messages = []
            if tc is not None and len(tc) > 0:
                message["tool_calls"] = tc
                for tool_call in tc:
                    tool_messages.append(
                        {
                            "role": "tool",
                            "content": "tool_call.content",
                            "tool_call_id": tool_call.get("id", ""),
                            "name": tool_call.get("function", {"name": ""}).get(
                                "name", ""
                            ),
                        }
                    )
            parsed_messages.append(message)
            if len(tool_messages) > 0:
                parsed_messages.extend(tool_messages)
        return parsed_messages

    def set_action_handlers(self, action_handlers):
        self.__gpt_manager.set_tools(action_handlers)

    def chat_with_agent(
        self, chat: Chat, messages: List[Message], custom_prompt: Optional[str]
    ) -> AgentResponse:
        messages_to_send = self.__parse_messages_to_openai(messages)
        messages_to_send.append(
            {
                "role": "user",
                "content": chat.message,
            }
        )

        try:
            response = self.__gpt_manager.process_messages(
                messages=messages_to_send,
                query=chat.message,
                gpt_id=chat.business.id,
                relevant_promt_data="",
                custom_prompt=custom_prompt,
            )

            return response
        except Exception as e:
            self.__logger.error(f"Error generating answer: {str(e)}")
            raise e

    def create(self, chat: Chat, platform: Literal["whatsapp"]) -> Chat:
        lead_id = chat.lead.phone_number
        business_id = chat.business.id

        try:
            contacts_snapshots = (
                self.__storage.getCollectionGroup("contacts")
                .where("phone_number", "==", lead_id)
                .where("ws_id", "==", business_id)
                .limit(1)
                .get()
            )
            contact_ref = contacts_snapshots[0].reference

            conversation_doc = self.__storage.getRawCollection(
                "conversations"
            ).document()
            conversation_doc.set(
                {
                    "contact_ref": contact_ref,
                    "start_time": self.__storage.getServerTimestamp(),
                    "platform": platform,
                    "status": "ongoing",
                    "intention": "comertial",  # TODO: Replace with gpt interpretation
                }
            )

            self.__logger.info(
                f"Chat created for lead with id {lead_id} and business with id {business_id}",
                "[method:create_chat]",
                f"[conversation_ref]: {conversation_doc.id}",
            )
        except Exception as e:
            error_message = f"Error has occurred trying create chat for lead with id {lead_id} and business with id {business_id}: {e}"
            self.__logger.error(error_message, "[method:create_chat]")
            raise error_message

    def exists(self, chat):
        lead_id = chat.lead.phone_number
        business_id = chat.business.id
        try:
            contacts_snapshots = (
                self.__storage.getCollectionGroup("contacts")
                .where("phone_number", "==", lead_id)
                .where("ws_id", "==", business_id)
                .limit(1)
                .get()
            )
            contact_ref = contacts_snapshots[0].reference

            conversation_snapshots = (
                self.__storage.getCollectionGroup("conversations")
                .where("contact_ref", "==", contact_ref)
                .limit(1)
                .get()
            )

            return len(conversation_snapshots) > 0
        except Exception as e:
            error_message = f"Error has occurred trying validate if chat exist for lead with id {lead_id} and business with id {business_id}: {e}"
            self.__logger.error(error_message, "[method:exists]")
            raise error_message

    def continue_conversation(
        self, messages: List[Message], business_id: str
    ) -> Tuple[bool, str]:
        messages_to_send = self.__parse_messages_to_openai(messages)
        try:
            response = self.__gpt_manager.continue_conversation(
                messages=messages_to_send, gpt_id=business_id
            )
            self.__logger.info("response", response.content)
            response_json = json.loads(response.content)
            return response_json.get("should_reply"), response_json.get("message")

        except Exception as e:
            self.__logger.error(f"Error contunuing conversation: {str(e)}")
            raise e


ChatAdapterMock = MagicMock()


class ChatModule(Module):
    @flexible_bind_wrapper(
        interface=ChatRepository, to=ChatAdapter, mock=ChatAdapterMock
    )
    def configure(self, binder):
        return
