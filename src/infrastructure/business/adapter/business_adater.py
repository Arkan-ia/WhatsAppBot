from unittest.mock import MagicMock
from injector import Module, inject, singleton
from src.domain.business.port.business_repository import BusinessRepository
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRealtionalDBManager,
)
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


@singleton
class BusinessAdapter(BusinessRepository):
    @inject
    def __init__(self, logger: LogAppManager, no_rel_db: NoRealtionalDBManager):
        self.__storage = no_rel_db
        self.__logger = logger
        self.__logger.set_caller("BusinessAdapter")

    def exists(self, business_id):
        # TODO: implement
        return False


BusinessRepositoryMock = MagicMock()


class BusinessModule(Module):
    @flexible_bind_wrapper(
        mock=BusinessRepositoryMock,
        interface=BusinessRepository,
        to=BusinessAdapter,
    )
    def configure(self, binder):
        binder.bind(BusinessRepository, to=BusinessAdapter)
