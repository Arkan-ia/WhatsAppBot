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
        try:
            business_ref: CollectionReference = self.__storage.getRawCollection(
                "business"
            )

            business_snapshots = (
                business_ref.where("ws_id", "==", business_id).limit(1).get()
            )
            business_ref = business_snapshots[0].reference

            return business_ref.get().exists
        except Exception as e:
            self.__logger.info(f"Error has occurred: {e}")
            return False

    def get_token_by_id(self, business_id: str) -> str:
        try:
            business_snapshots: CollectionReference = (
                self.__storage.getRawCollection("business")
                .where("ws_id", "==", business_id)
                .limit(1)
                .get()
            )
            if not business_snapshots:
                error_message = f"Business with ref {business_id} was not found"
                self.__logger.error(error_message)
                raise Exception(error_message)

            business_ref = business_snapshots[0].reference
            return business_ref.get().to_dict()["ws_token"]
        except Exception as e:
            self.__logger.error(
                f"Error has occurred getting token of business with id {business_id}: {e}"
            )
            raise e


BusinessRepositoryMock = MagicMock()


class BusinessModule(Module):
    @flexible_bind_wrapper(
        mock=BusinessRepositoryMock,
        interface=BusinessRepository,
        to=BusinessAdapter,
    )
    def configure(self, binder):
        binder.bind(BusinessRepository, to=BusinessAdapter)
