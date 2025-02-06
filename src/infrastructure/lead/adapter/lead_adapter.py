from unittest.mock import MagicMock
from injector import Module, inject, singleton
from src.domain.lead.model.lead import Lead
from src.domain.lead.port.lead_repository import LeadRepository
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRealtionalDBManager,
)
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


@singleton
class LeadAdapter(LeadRepository):
    @inject
    def __init__(self, logger: LogAppManager, no_rel_db: NoRealtionalDBManager):
        self.__logger = logger
        self.__logger.set_caller("LeadAdapter")
        self.__storage = no_rel_db

    def exists(self, lead_id: str, business_id: str):
        try:
            contacts_snapshots = (
                self.__storage.getCollectionGroup("contacts")
                .where("phone_number", "==", lead_id)
                .where("ws_id", "==", business_id)
                .get()
            )

            return len(contacts_snapshots) > 0
        except Exception as e:
            self.__logger.error(
                f"Error has validating if lead with id {lead_id} exist: {e}",
                "[method:exists]",
            )
            return False

    def save(self, lead: Lead, business_id: str):
        try:
            business_snapshots = (
                self.__storage.getRawCollection("business")
                .where("ws_id", "==", business_id)
                .get()
            )

            business_ref = business_snapshots[0].reference
            contact_doc = business_ref.collection("contacts").document()

            contact_doc.set(
                {
                    "phone_number": lead.phone_number,
                    "ws_id": business_id,
                    "last_message": {
                        **lead.last_message,
                        "created_at": self.__storage.getServerTimestamp(),
                    },
                }
            )
        except Exception as e:
            message_error = f"Error has occurred trying to save lead with id {lead.id} with business id {business_id}: {e}"
            self.__logger.error(
                message_error,
                "[method:save]",
            )
            raise message_error

    def update(self, lead: Lead, business_id: str):
        phone_number = lead.phone_number
        try:
            contact_snapshots = (
                self.__storage.db.collection_group("contacts")
                .where("ws_id", "==", business_id)
                .where("phone_number", "==", phone_number)
                .limit(1)
                .get()
            )

            contact_snapshots[0].reference.update(
                {
                    "display_name": lead.name,
                    "email": lead.email,
                    "purchase_count": lead.purchase_count,
                    "ws_id": business_id,
                    "phone_number": phone_number,
                    "last_message": lead.last_message,
                    "citizen_id": lead.citizen_id,
                    "address": lead.address,
                    "city": lead.city,
                }
            )

            return contact_snapshots[0].get()

        except Exception as e:
            error_message = f"Error has occurred trying to update lead with id {lead.id} with business id {business_id}: {e}"
            self.__logger.error(error_message)
            raise error_message


LeadRepositoryMock = MagicMock()


class LeadModule(Module):
    @flexible_bind_wrapper(
        mock=LeadRepositoryMock,
        interface=LeadRepository,
        to=LeadAdapter,
    )
    def configure(self, binder):
        return
