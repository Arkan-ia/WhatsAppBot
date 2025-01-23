from concurrent.futures import ThreadPoolExecutor
import time
from typing import List, Literal
from unittest.mock import MagicMock

from flask import jsonify
from injector import Module, inject, singleton

from src.domain.message.model.message import Message, Sender
from src.domain.message.port.message_repository import MessageRepository
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.messaging.mesaging_manager import MessagingManager
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRealtionalDBManager,
)
from google.cloud.firestore_v1.query_results import QueryResultsList
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference

from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


@singleton
class MessageWhatsAppApiAdapter(MessageRepository):
    __batch_size = 20
    __wait_time_between_batches = 0.001

    @inject
    def __init__(
        self,
        messaging_manager: MessagingManager,
        logger: LogAppManager,
        no_rel_db: NoRealtionalDBManager,
    ) -> None:
        self.__messaging_manager = messaging_manager
        self.__logger = logger
        self.__logger.set_caller("MessageWhatsAppApiAdapter")
        self.__storage = no_rel_db

    def __validate_to(self, phone_number):
        if len(phone_number) != 12:
            raise ValueError(
                "The number must include the country code and have 12 digits."
            )

    # TODO: implement getting from db
    def get_template_data(self, business_id: str, template_name: str) -> str:
        # TODO: get from db
        o = {"gano_excel": {"gano_excel_1": "En navidad...."}}
        result = [business_id][template_name]
        return "template data"

    def save_message(
        self,
        message: Message,
        role: Literal["user", "assistant"],
        platform: Literal["whatsapp"],
    ) -> str:
        business_ref: CollectionReference = (
            self.__storage.getRawCollection("users")
            .where("ws_id", "==", message.sender.from_identifier)
            .limit(1)
            .get()
        )
        if not business_ref:
            raise Exception(f"Business with ref {message.to} was not found")

        business_doc = business_ref[0].reference
        contact_ref: DocumentReference = business_doc.collection("contacts").document(
            message.to
        )
        if not contact_ref:
            raise Exception(
                f"Contact with ref {message.to} was not found in business {message.sender.from_identifier}"
            )

        doest_exist_contact = not contact_ref.get().exists
        if doest_exist_contact:
            self.__logger.info(
                f"Creating new contact {message.to} in business {message.sender.from_identifier}"
            )
            contact_ref.set({"ws_id": message.to})

        message_ref: DocumentReference = business_doc.collection("messages").document()
        message_ref.set(
            {
                "content": message.content,
                "platform": platform,
                "timestamp": self.__storage.getServerTimestamp(),
                "role": role,
                "contact_ref": contact_ref,
            }
        )

    def send_single_message(self, message: Message) -> str:
        sender = message.sender
        try:
            self.__validate_to(message.to)
            self.__messaging_manager.send_message(message, sender)
            self.save_message(message, "assistant", "whatsapp")

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
        all_results = []
        for batch in self.__batchify(messages, self.__batch_size):
            batch_results = self.__send_message_batch(batch)
            all_results.extend(batch_results)
            time.sleep(self.__wait_time_between_batches)

        success_requests = sum(
            1 for result in all_results if result["status"] == "success"
        )
        error_requests = len(messages) - success_requests

        return {
            "status": "ok",
            "message": f"Mensajes enviados con éxito a {success_requests} usuarios, {error_requests} errores",
            "details": all_results,
        }

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


MessageRepositoryMock = MagicMock()


class MessageModule(Module):
    @flexible_bind_wrapper(
        mock=MessageRepositoryMock,
        interface=MessageRepository,
        to=MessageWhatsAppApiAdapter,
    )
    def configure(self, binder):
        return
