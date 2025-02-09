from abc import ABC, abstractmethod

from injector import Module, inject, singleton
from requests import Response

from src.domain.message.model.message import Message, Sender
from src.infrastructure.shared.http.http_manager import HttpManager
from src.infrastructure.shared.logger.logger import LogAppManager


class MessagingManager(ABC):
    @abstractmethod
    def send_message(self, message: Message) -> str:
        pass

    @abstractmethod
    def mark_message_as_read(self, message: Message) -> str:
        pass


@singleton
class WhatsAppMessagingManager(MessagingManager):
    @inject
    def __init__(self, http_manager: HttpManager, logger: LogAppManager) -> None:
        http_manager.set_base_url("https://graph.facebook.com/v21.0")
        self.__http_manager = http_manager
        self.__logger = logger
        self.__logger.set_caller("WhatsAppMessagingManager")

    def send_message(self, message: Message) -> str:
        sender = message.sender
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {sender.from_token}",
        }

        try:
            response: Response = self.__http_manager.post(
                f"/{sender.from_identifier}/messages",
                message.get_message(),
                headers=headers,
            )
            self.__logger.debug("Got response from facebook", response.json())
            if response.status_code != 200:
                raise Exception(
                    "Failed to send message", f"[status_code]:{response.statuscode}"
                )

            return response
        except Exception as e:
            self.__logger.error("Error sending message", e)
            raise e

    def mark_message_as_read(self, message: Message) -> str:
        sender = message.sender
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {sender.from_token}",
        }

        try:
            response: Response = self.__http_manager.post(
                f"/{sender.from_identifier}/messages",
                message.get_message(),
                headers=headers,
            )
            self.__logger.debug("Got response from facebook", response.json())
            if response.status_code != 200:
                raise Exception(
                    "Failed to mark message as read",
                    f"[status_code]:{response.statuscode}",
                )

            return response
        except Exception as e:
            self.__logger.error("Error marking message as read", f"[error]:{e}")
            raise e


class MessagingManagerModule(Module):
    def configure(self, binder):
        binder.bind(MessagingManager, to=WhatsAppMessagingManager)
