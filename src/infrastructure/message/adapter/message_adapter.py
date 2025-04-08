from concurrent.futures import ThreadPoolExecutor
import json
import time
from typing import Dict, List, Literal, Optional
from unittest.mock import MagicMock

from injector import Module, inject, singleton

from src.common.utils.google_tasks import create_task, delete_task
from src.domain.chat.port.chat_repository import ToolCall
from src.domain.message.model.message import (
    Message,
    Sender,
    TextMessage,
    WhatsAppSender,
)
from src.domain.message.port.message_repository import MessageRepository, TimeUnits
from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.messaging.messaging_manager import MessagingManager
from src.infrastructure.shared.storage.no_relational_db_manager import (
    NoRealtionalDBManager,
)
from google.cloud.firestore_v1.query_results import QueryResultsList
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference

from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper
from google.cloud.firestore_v1.query import CollectionGroup


@singleton
class MessageWhatsAppApiAdapter(MessageRepository):
    __batch_size = 20
    __wait_time_between_batches = 0.001

    @inject
    def __init__(
        self,
        messaging_manager: MessagingManager,
        logger: LogAppManager,
        no_rel_db: NoRealtionalDBManager,
    ) -> None:
        self.__messaging_manager = messaging_manager
        self.__logger = logger
        self.__logger.set_caller("MessageAdapter")
        self.__storage = no_rel_db

    def __validate_to(self, phone_number):
        if len(phone_number) != 12:
            raise ValueError(
                "The number must include the country code and have 12 digits."
            )

    # TODO: implement getting from db
    def get_template_data(self, business_id: str, template_name: str) -> str:
        db = {
            "450361964838178": {
                "gano_excel_1": """🌟 ¡Gran Lanzamiento de la Línea Fit JM! 🌟
¡Hola! 😊 Hoy queremos compartir contigo una excelente noticia: estrenamos una nueva línea diseñada especialmente para facilitar tu proceso de compra y ofrecerte los mejores productos saludables.

🎉 Además, ¡tenemos promociones exclusivas por lanzamiento!
Escríbele a Jorge, nuestro asesor, y descubre cómo puedes aprovechar estas ofertas hoy mismo.

📲 ¡Estamos aquí para ayudarte a dar el siguiente paso hacia un estilo de vida más saludable!""",
                "gano_excel_2": """¡Este año sí vas a cumplir las promesas de año nuevo! ¿Cierto? 🧐

Si pediste por salud y vida, aquí llegó la señal divina 🙏 Que no te falte el café en cada mañana para iniciar con energía, fusionado con Ganoderma para una vida larga y prospera. ☕ Si diciembre te dejó apretado, relájate. 😌 Porque si llevas 2 o más cajas de nuestro café 3 en 1 o clásico, vas a tener tremendo descuento en tú compra. 😱 ¡Estamos botados! 
La promo es hasta el 15 de enero. 🛒""",
                "ano_nuevo": """☕✨ ¡Feliz Año Nuevo! ✨☕

        Si llevas 2 o más cajas de nuestro café 3 en 1 o clásico, te damos un precio especial. 
        La promo es hasta el 15 de enero. 🏃‍♀""",
                "hola": """Hola""",
            },
        }

        result = db[business_id][template_name]
        return result

    def save_message(
        self,
        message: Message,
        role: Literal["user", "assistant"],
        platform: Literal["whatsapp"],
    ) -> str:
        lead_id = message.to
        business_id = message.sender.from_identifier
        db_tool_calls = []
        tool_calls: List[ToolCall] = message.tool_call
        for tool_call in tool_calls:
            db_tool_calls.append(tool_call.to_dict())

        message_metadata = {
            "tool_calls": db_tool_calls,
        }

        try:
            contacts_snapshots = (
                self.__storage.getCollectionGroup("contacts")
                .where("phone_number", "==", lead_id)
                .where("ws_id", "==", business_id)
                .limit(1)
                .get()
            )
            contact_ref = contacts_snapshots[0].reference

            conversation_snapshots = (
                self.__storage.getRawCollection("conversations")
                .where("contact_ref", "==", contact_ref)
                .limit(1)
                .get()
            )
            conversation_ref: DocumentReference = conversation_snapshots[0].reference

            message_doc: DocumentReference = conversation_ref.collection(
                "messages"
            ).document()

            message_doc.set(
                {
                    "content": message.content,
                    "platform": platform,
                    "timestamp": self.__storage.getServerTimestamp(),
                    "role": role,
                    "contact_ref": contact_ref,
                    "phone_number": lead_id,
                    "ws_id": business_id,
                    "wa_id": message.message_id,
                    **message_metadata,
                }
            )

            return ""
        except Exception as e:
            self.__logger.error("Error saving message", "[method: save_message]", e)
            raise e

    def send_single_message(self, message: Message) -> str:
        sender = message.sender
        try:
            self.__validate_to(message.to)
            response = self.__messaging_manager.send_message(message)
            if not message.message_id:
                message.message_id = response.json().get("messages")[0].get("id")

            self.save_message(message, "assistant", "whatsapp")

            return {
                "status": "success",
                "message": f"Message sent to {message.to} from {sender.from_identifier}",
            }
        except Exception as e:
            self.__logger.error(e)
            return {
                "status": "error",
                "message": f"Error sending message to {message.to} from {sender.from_identifier}",
            }

    def program_later_message(self, message: Message, time: Dict[TimeUnits, int]):
        lead_id = message.to
        business_id = message.sender.from_identifier
        try:
            contacts_snapshots: List[DocumentSnapshot] = (
                self.__storage.getCollectionGroup("contacts")
                .where("phone_number", "==", lead_id)
                .where("ws_id", "==", business_id)
                .limit(1)
                .get()
            )

            contact_ref: DocumentReference = contacts_snapshots[0].reference

            contact_snapshot = contact_ref.get()
            current_task = contact_snapshot.to_dict().get("task", None)

            if current_task:
                try:
                    delete_task(current_task)
                except:
                    pass

            answer_later_task = create_task(
                "https://7b7b-186-112-62-80.ngrok-free.app/chat/continue-conversation",
                time,
                json.dumps(
                    {
                        "business_id": business_id,
                        "lead_id": lead_id,
                    }
                ),
            )

            contact_ref.update({"task": answer_later_task})
        except Exception as e:
            self.__logger.error(f"Error programando el mensaje: {e}")

    def send_massive_message(self, messages: List[Message]) -> str:
        all_results = []
        for batch in self.__batchify(messages, self.__batch_size):
            batch_results = self.__send_message_batch(batch)
            all_results.extend(batch_results)
            time.sleep(self.__wait_time_between_batches)

        success_requests = sum(
            1 for result in all_results if result["status"] == "success"
        )
        error_requests = len(messages) - success_requests

        return {
            "status": "ok",
            "message": f"Mensajes enviados con éxito a {success_requests} usuarios, {error_requests} errores",
            "details": all_results,
        }

    def mark_message_as_read(self, message: Message) -> str:
        # TODO: Save interaction in database
        return self.__messaging_manager.mark_message_as_read(message)

    def get_messages(
        self, business_id: str, lead_id: str, limit: int = 10
    ) -> List[Message]:
        self.__validate_to(lead_id)
        try:
            messages_snapshots = (
                self.__storage.getCollectionGroup("messages")
                .where("phone_number", "==", lead_id)
                .where("ws_id", "==", business_id)
                .order_by("timestamp", "DESCENDING")
                .limit(limit)
                .get()
            )

            messages: List[Message] = []

            for db_message in messages_snapshots:
                db_message = db_message.to_dict()
                sender: Sender = WhatsAppSender()
                sender.from_identifier = business_id

                message: Message = TextMessage()
                message.role = db_message.get("role")
                message.tool_call = db_message.get("tool_calls")
                message.content = db_message.get("content")
                message.to = db_message.get("phone_number")
                message.message_id = db_message.get("wa_id")
                message.sender = sender

                self.__logger.info(f"Message in history: {message.content}")
                messages.append(message)

            return messages
        except Exception as e:
            self.__logger.error("Error getting messages", "[method: get_messages]", e)
            raise e

    def __batchify(self, iterable: iter, batch_size: int) -> iter:
        """Split an interable into batches of batch_size."""
        for i in range(0, len(iterable), batch_size):
            yield iterable[i : i + batch_size]

    def __send_message_batch(self, batch: List[Message]):
        results = []
        with ThreadPoolExecutor(max_workers=self.__batch_size) as executor:
            results = list(
                executor.map(lambda msg: self.send_single_message(msg), batch)
            )
        return results


MessageRepositoryMock = MagicMock()


class MessageModule(Module):
    @flexible_bind_wrapper(
        mock=MessageRepositoryMock,
        interface=MessageRepository,
        to=MessageWhatsAppApiAdapter,
    )
    def configure(self, binder):
        return
