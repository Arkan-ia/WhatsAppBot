import logging
from src.data.repositories.contact_repository import ContactRepository
from src.data.sources.firebase.utils import get_contact_ref
from src.data.sources.firebase.config import db


class ContactFirebaseRepository(ContactRepository):
    def get_contact(self, ws_id, phone_number):
        """Obtiene los datos del usuario."""
        # try:
        #     contact_ref = get_contact_ref(ws_id, phone_number)
        #     return contact_ref.get().to_dict()

        # except Exception as e:
        #     print(f"Error al obtener datos del usuario {ws_id}: {str(e)}")
        #     raise

        ## --- :NEW DB: --- ##
        try:
            if len(phone_number) != 12:
                raise Exception(
                    "Los números a consultar deben tener su respectivo codigo de país"
                )

            contact_query = (
                db.collection_group("contacts")
                .where("ws_id", "==", ws_id)
                .where("phone_number", "==", phone_number)
                .limit(1)
            )

            contact_snapshots = contact_query.get()

            if not contact_snapshots:
                logging.info(
                    f"No se encontró ningún contacto con el número {phone_number} para el usuario con ws_id {ws_id}. Se creará uno nuevo"
                )
                return self.create_contact(ws_id, phone_number)

            return contact_snapshots[0].to_dict()

        except Exception as e:
            print(f"Error al obtener datos del usuario {ws_id}: {str(e)}")
            raise

    def update_contact(self, ws_id, phone_number, data):
        """Actualiza los datos de un contacto."""
        # try:
        #     print(f"-------------DATA----------------- {data}")
        #     contact_ref = get_contact_ref(ws_id, phone_number)
        #     contact_ref.update(data)
        #     logging.info(f"Datos de {phone_number} actualizados con {data}")
        # except Exception as e:
        #     logging.error(
        #         f"Error al actualizar datos del contacto {phone_number} para {ws_id}: {str(e)}"
        #     )
        #     raise
        ## --- :NEW DB: --- ##
        try:
            if len(phone_number) != 12:
                raise Exception(
                    "Los números a consultar deben tener su respectivo codigo de país"
                )

            contact_query = (
                db.collection_group("contacts")
                .where("ws_id", "==", ws_id)
                .where("phone_number", "==", phone_number)
                .limit(1)
            )

            contact_snapshots = contact_query.get()
            contact_snapshots[0].reference.update(data)
            
            return contact_snapshots[0].get()

        except Exception as e:
            logging.error(
                 f"Error al actualizar datos del contacto {phone_number} para {ws_id}: {str(e)}"
             )            
            raise


    def create_contact(self, ws_id: str, phone_number: str): # TODO: Add ws_token
        business_query = db.collection("business").where("ws_id", "==", ws_id)
        business_snapshots = business_query.get()

        if not business_snapshots:
            raise Exception(f"No se encontró ningún business con ws_id {ws_id}")
        
        business_ref = business_snapshots[0].reference
        contact_ref = business_ref.collection("contacts").document()
        contact_ref.set({"ws_id": ws_id, "phone_number": phone_number})

        return contact_ref

    def delete_contact(ws_id, phone_number, data):
        pass
