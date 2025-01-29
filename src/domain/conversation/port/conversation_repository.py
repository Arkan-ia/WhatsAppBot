from abc import abstractmethod
from injector import singleton
from google.cloud.firestore_v1.document import DocumentReference


@singleton
class ConversationRepository:
    @abstractmethod
    def get_or_create_conversation(self, contact_ref) -> DocumentReference:
        pass
