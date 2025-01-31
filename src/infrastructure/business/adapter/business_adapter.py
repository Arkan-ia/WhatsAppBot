from unittest.mock import MagicMock
from injector import Module, inject, singleton
from src.domain.business.port.business_repository import BusinessRepository
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRealtionalDBManager,
)
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper
from google.cloud.firestore_v1.collection import CollectionReference


@singleton
class BusinessAdapter(BusinessRepository):
    @inject
    def __init__(self, logger: LogAppManager, no_rel_db: NoRealtionalDBManager):
        self.__storage = no_rel_db
        self.__logger = logger
        self.__logger.set_caller("BusinessAdapter")

    def exists(self, business_id: str) -> bool:
        business_ref: CollectionReference = (
            self.__storage.getRawCollection("projects")
            .where("ws_id", "==", business_id)
            .limit(1)
            .get()
        )
        bussiness_doc = business_ref[0].reference
        return bussiness_doc.get().exists
        # business_ref = self.__storage.getRawDocument("business", business_id)
        # business_doc = business_ref.get()

        # return business_doc.exists

    def get_token_by_id(self, business_id: str) -> str:
        business_ref: CollectionReference = (
            self.__storage.getRawCollection("projects")
            .where("ws_id", "==", business_id)
            .limit(1)
            .get()
        )
        if not business_ref:
            self.__logger.info(f"Business with ref {business_id} was not found")
            raise Exception(f"Business with ref {message.to} was not found")

        business_doc = business_ref[0].reference
        return business_doc.get().to_dict()["ws_token"]


BusinessRepositoryMock = MagicMock()


class BusinessModule(Module):
    @flexible_bind_wrapper(
        mock=BusinessRepositoryMock,
        interface=BusinessRepository,
        to=BusinessAdapter,
    )
    def configure(self, binder):
        binder.bind(BusinessRepository, to=BusinessAdapter)
