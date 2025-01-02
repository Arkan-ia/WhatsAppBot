

from abc import ABC, abstractmethod


class ContactRepository(ABC):
    @abstractmethod
    def create_contact(ws_id, phone_number):
        pass

    @abstractmethod
    def get_contact(ws_id, phone_number):
        pass
    
    @abstractmethod
    def update_contact(ws_id, phone_number, data):
        pass
    
    @abstractmethod
    def delete_contact(ws_id, phone_number, data):
        pass