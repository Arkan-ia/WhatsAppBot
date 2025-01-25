from abc import ABC, abstractmethod


class BusinessRepository(ABC):
    @abstractmethod
    def exists(self, business_id: str) -> bool:
        pass
