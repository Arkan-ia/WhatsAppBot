from concurrent.futures import ThreadPoolExecutor
import time
from typing import List, Literal
from unittest.mock import MagicMock

from flask import jsonify
from injector import Module, inject, singleton

from src.domain.conversation.port.conversation_repository import ConversationRepository
from src.domain.message.model.message import Message, Sender
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
class ConversationAdapter(ConversationRepository):
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
        self.__logger.set_caller("ConversationAdapter")
        self.__storage = no_rel_db

    def get_or_create_conversation(
        self,
        contact_ref: DocumentReference,
    ) -> DocumentReference:
        """
        Obtiene o crea una conversación en la base de datos.

        Args:
            contact_ref (firebase_admin.firestore.DocumentReference): La referencia del contacto.

        Returns:
            firebase_admin.firestore.DocumentReference: La referencia de la conversación.
        """
        conversations_query = (
            self.__storage.db.collection("conversations")
            .where("status", "==", "ongoing")
            .where("contact_ref", "==", contact_ref)
        )
        conversations_snapshots = conversations_query.get()

        if not conversations_snapshots:
            conversation_ref = self.__storage.db.collection("conversations").document()
            conversation_ref.set(
                {
                    "contact_ref": contact_ref,
                    "start_time": self.__storage.getServerTimestamp(),
                    "platform": "whatsapp",
                    "status": "ongoing",
                    "intention": "comertial",  # TODO: Replace with gpt interpretation
                }
            )

        else:
            conversation_ref = conversations_snapshots[0].reference

        return conversation_ref


ConversationRepositoryMock = MagicMock()


class ConvarsationModule(Module):
    @flexible_bind_wrapper(
        mock=ConversationRepositoryMock,
        interface=ConversationRepository,
        to=ConversationAdapter,
    )
    def configure(self, binder):
        return
