from abc import abstractmethod
from injector import singleton
from google.cloud.firestore_v1.document import DocumentReference


@singleton
class LeadRepository:
    @abstractmethod
    def get_or_create_contact(
        self, phone_number: str, from_whatsapp_id: str
    ) -> DocumentReference:
        pass

    @abstractmethod
    def update_last_message(self, contact_ref, content):
        pass

    @abstractmethod
    def update_contact(self, ws_id, phone_number, data):
        pass

