import logging
from src.data.repositories.contact_repository import ContactRepository
from src.data.sources.firebase.utils import get_contact_ref

class ContactFirebaseRepository(ContactRepository):
    def get_contact(self, ws_id, phone_number):
        """Obtiene los datos del usuario."""
        try:
            contact_ref = get_contact_ref(ws_id, phone_number)
            return contact_ref.get().to_dict()

        except Exception as e:
            print(f"Error al obtener datos del usuario {ws_id}: {str(e)}")
            raise


    def update_contact(self, ws_id, phone_number, data):
        """Actualiza los datos de un contacto."""
        try:
            contact_ref = get_contact_ref(ws_id, phone_number)
            contact_ref.update(data)
            logging.error(f"Datos de {phone_number} actualizados con {data}")
        except Exception as e:
            print(
                f"Error al actualizar datos del contacto {phone_number} para {ws_id}: {str(e)}"
            )
            raise

    
    def create_contact(ws_id, phone_number):
        pass
    

    def delete_contact(ws_id, phone_number, data):
        pass