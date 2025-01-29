from concurrent.futures import ThreadPoolExecutor
import time
from typing import List, Literal
from unittest.mock import MagicMock

from flask import jsonify
from injector import Module, inject, singleton

from src.domain.lead.port.lead_repository import LeadRepository
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
class LeadAdapter(LeadRepository):
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

    # COSOS QUE TOCA CAMBIAR DE LADO
    def get_or_create_contact(
        self, phone_number: str, from_whatsapp_id: str
    ) -> DocumentReference:
        """
        Obtiene o crea un contacto en la base de datos.

        Args:
            phone_number (str): El número de teléfono del contacto.

        Returns:
            firebase_admin.firestore.DocumentReference: La referencia del contacto.
        """
        contacts_query = (
            self.__storage.db.collection_group("contacts")
            .where("phone_number", "==", phone_number)
            .where("ws_id", "==", from_whatsapp_id)
        )
        contacts_snapshots = contacts_query.get()

        if not contacts_snapshots:
            business_query = self.__storage.db.collection("business").where(
                "ws_id", "==", from_whatsapp_id
            )
            business_snapshots = business_query.get()

            if not business_snapshots:
                raise Exception(
                    f"No hay ningún negocio en Venya vinculado a este número {from_whatsapp_id}"
                )

            business_ref = business_snapshots[0].reference
            contact_ref = business_ref.collection("contacts").document()

            contact_ref.set({"phone_number": phone_number, "ws_id": from_whatsapp_id})

        else:
            contact_ref = contacts_snapshots[0].reference

        return contact_ref

    def update_last_message(self, contact_ref, content):
        contact_ref.update(
            {
                "last_message": {
                    "content": content,
                    "created_at": self.__storage.getServerTimestamp(),
                }
            }
        )


LeadRepositoryMock = MagicMock()


class LeadModule(Module):
    @flexible_bind_wrapper(
        mock=LeadRepositoryMock,
        interface=LeadRepository,
        to=LeadAdapter,
    )
    def configure(self, binder):
        return
