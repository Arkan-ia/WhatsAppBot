from concurrent.futures import ThreadPoolExecutor
import time
from typing import List

from flask import jsonify
from injector import Module, inject, singleton

from src.domain.message.model.message import Message, Sender
from src.domain.message.port.message_repository import MessageRepository
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.messaging.mesaging_manager import MessagingManager


@singleton
class MessageWhatsAppApiAdapter(MessageRepository):
    __batch_size = 20
    __wait_time_between_batches = 0.001

    @inject
    def __init__(
        self, messaging_manager: MessagingManager, logger: LogAppManager
    ) -> None:
        self.__messaging_manager = messaging_manager
        self.__logger = logger
        self.__logger.set_caller("MessageWhatsAppApiAdapter")

    def send_single_message(self, message: Message) -> str:
        try:
            sender = message.sender
            self.__messaging_manager.send_message(message, sender)
            # TODO: Save into db
            return {
                "status": "success",
                "message": f"Message sent to {message.to} from {sender.from_identifier}",
            }
        except Exception as e:
            self.__logger.error(e)
            return {
                "status": "error",
                "message": f"Error sending message to {message.to} from {sender.from_identifier}",
            }

    def send_massive_message(self, messages: List[Message]) -> str:
        print(messages)
        all_results = []
        for batch in self.__batchify(messages, self.__batch_size):
            batch_results = self.__send_message_batch(batch)
            all_results.extend(batch_results)
            time.sleep(self.__wait_time_between_batches)

        success_requests = sum(
            1 for result in all_results if result["status"] == "success"
        )
        error_requests = len(messages) - success_requests
        return jsonify(
            {
                "status": "ok",
                "message": f"Mensajes enviados con éxito a {success_requests} usuarios, {error_requests} errores",
                "details": all_results,
            }
        )

    def __batchify(self, iterable: iter, batch_size: int) -> iter:
        """Split an interable into batches of batch_size."""
        for i in range(0, len(iterable), batch_size):
            yield iterable[i : i + batch_size]

    def __send_message_batch(self, batch: List[Message]):
        results = []
        with ThreadPoolExecutor(max_workers=self.__batch_size) as executor:
            results = list(
                executor.map(lambda msg: self.send_single_message(msg), batch)
            )
        return results


class MessageModule(Module):
    def configure(self, binder):
        binder.bind(MessageRepository, to=MessageWhatsAppApiAdapter)
