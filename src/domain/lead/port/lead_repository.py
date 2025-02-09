from abc import ABC, abstractmethod
from src.domain.lead.model.lead import Lead


class LeadRepository(ABC):
    @abstractmethod
    def exists(self, lead_id: str, business_id: str) -> bool:
        pass

    @abstractmethod
    def save(self, lead: Lead, business_id: str) -> Lead:
        pass

    @abstractmethod
    def update(self, lead: Lead, business_id: str) -> Lead:
        pass
