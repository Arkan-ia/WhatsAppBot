from abc import ABC, abstractmethod


class BusinessRepository(ABC):
    @abstractmethod
    def exists(self, business_id: str) -> bool:
        pass

    @abstractmethod
    def get_token_by_id(self, business_id: str) -> str:
        pass
