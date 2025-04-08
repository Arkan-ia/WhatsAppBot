import json
from typing import List
from injector import inject, singleton
import requests

from src.domain.business.model.business import Business
from src.domain.business.port.business_repository import BusinessRepository
from src.domain.chat.model.chat import Chat, MessageType
from src.domain.chat.port.chat_repository import (
    ActionHandler,
    AgentResponse,
    ChatRepository,
)
from src.domain.errors.business_not_found import BusinessNotFoundError
from src.domain.errors.invalid_phone_number import InvalidPhoneNumberError
from src.domain.lead.model.lead import Lead
from src.domain.lead.port.lead_repository import LeadRepository
from src.domain.message.model.message import (
    Message,
    ReadMessage,
    Sender,
    WhatsAppSender,
    TextMessage,
)
from src.domain.message.port.message_repository import MessageRepository, TimeUnits
from src.infrastructure.shared.logger.logger import LogAppManager
from src.common.utils.notifications import send_email_notification


@singleton
class ChatWithLeadService:
    @inject
    def __init__(
        self,
        chat_repository: ChatRepository,
        business_repository: BusinessRepository,
        message_repository: MessageRepository,
        lead_repository: LeadRepository,
        logger: LogAppManager,
    ) -> None:
        self.__chat_repository = chat_repository
        action_handlers: List[ActionHandler] = [
            ActionHandler(
                name="customer_buy",
                description="Envía un correo electrónico al dueño del negocio notificando que un cliente quiere pagar.",
                params={
                    "products": {
                        "type": "string",
                        "description": "Los productos realizados por el cliente.",
                    },
                    "price": {
                        "type": "number",
                        "description": "El precio total del pedido.",
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "El número de teléfono del cliente.",
                    },
                    "name": {
                        "type": "string",
                        "description": "El nombre del cliente.",
                    },
                    "cedula": {
                        "type": "string",
                        "description": "La cédula del cliente.",
                    },
                    "address": {
                        "type": "string",
                        "description": "La dirección del cliente.",
                    },
                    "city": {
                        "type": "string",
                        "description": "La ciudad del cliente.",
                    },
                },
                required_params=["products", "price", "cedula", "address", "city"],
                handler=self.handle_customer_buy,
                reply_to_costumer_message="Gracias por tu compra, ha sido enviada para realizar el envío. Me pondré en contacto contigo para informarte el estado de tu pedio.",
            ),
        ]
        self.__action_handlers = action_handlers
        self.__chat_repository.set_action_handlers(action_handlers)
        self.__business_repository = business_repository
        self.__message_repository = message_repository
        self.__lead_repository = lead_repository
        self.__logger = logger
        self.__logger.set_caller("ChatWithLeadService")

    @staticmethod
    def handle_customer_buy(
        products: str,
        price: float,
        phone_number: str = None,
        name: str = None,
        cedula: str = None,
        address: str = None,
        city: str = None,
    ):
        subject = "Nueva solicitud de pago"
        body = f"Un cliente ha solicitado realizar un pago. Los detalles del cliente son:\n- Precio: {price}\n- Productos: {products}\n- Nombre: {name}\n- Número de teléfono: {phone_number}\n- Cédula: {cedula}\n- Dirección: {address}\n- Ciudad: {city}.\n Por favor revisa tu panel de control en https://arkania.flutterflow.app/chats"
        send_email_notification(
            to="kevinskate.kg@gmail.com", message=body, subject=subject
        )

    def run(self, chat: Chat) -> str:
        ## TODO: add toll calls to send to bot
        business_id = chat.business.id

        is_valid_lead = chat.lead.is_valid_phone_number()
        if not is_valid_lead:
            raise InvalidPhoneNumberError(chat.lead.phone_number)

        exists_business = self.__business_repository.exists(business_id)
        if not exists_business:
            raise BusinessNotFoundError(business_id)

        exists_lead = self.__lead_repository.exists(chat.lead.phone_number, business_id)
        if not exists_lead:
            self.__logger.info(
                f"Saving lead {chat.lead.phone_number} to business {business_id}"
            )
            chat.lead.last_message = {
                "content": chat.message,
                "status": "pending",
            }
            self.__lead_repository.save(chat.lead, business_id)

        exist_chat = self.__chat_repository.exists(chat)
        if not exist_chat:
            self.__logger.info(
                f"Creating chat for lead {chat.lead.phone_number} and business {business_id}"
            )
            self.__chat_repository.create(chat, "whatsapp")

        is_reaction_mesage = chat.message_type == MessageType.REACTION
        if is_reaction_mesage:
            return "Ok", 200

        messages = self.__message_repository.get_messages(
            business_id, chat.lead.phone_number, 10
        )
        # TODO: define a logic of fallback to prevent answer multiple times
        # TODO: validate if message_id already exist, to prevent answer old messages

        token = self.__business_repository.get_token_by_id(business_id)
        sender: Sender = WhatsAppSender()
        sender.from_token = token
        sender.from_identifier = chat.business.id
        message: Message = ReadMessage()
        message.sender = sender
        message.message_id = chat.message_id
        message.to = chat.lead.phone_number
        message.content = chat.message
        message.metadata = {}

        self.__message_repository.mark_message_as_read(message)

        ## TODO: replace with db query to get infor about client and create custom promt
        agent_response: AgentResponse
        if chat.business.id == "527260523813925":
            org_id = "5PyLKbnwpUlTAOdd2QvF"
            response = requests.post(
                "https://us-central1-zalee-943c2.cloudfunctions.net/mainpython/organizer",
                json={"org_id": org_id},
            )
            custom_prompt = f"Our following events are the following: {response.json()}"
            agent_response = self.__chat_repository.chat_with_agent(
                chat, messages, custom_prompt
            )
        else:
            agent_response = self.__chat_repository.chat_with_agent(chat, messages)

        reply_message: Message = TextMessage()
        reply_message.tool_call = []
        # Handle tool calls
        if agent_response.has_tool_calls:
            reply_message.tool_call = agent_response.tool_calls
            for tool_call in agent_response.tool_calls:
                for handler in self.__action_handlers:
                    if handler.name == tool_call.name:
                        agent_response.content = handler.reply_to_costumer_message
                        handler.handler(**tool_call.arguments)

        # Save the user message first
        self.__message_repository.save_message(message, "user", "whatsapp")

        self.__logger.info(f"Agent response: {agent_response.content}")

        try:
            # Check if the content is a list (multiple messages)
            json_response = json.loads(agent_response.content)
            # Send each message individually
            for msg_content in json_response.get("response"):
                single_reply = TextMessage()
                single_reply.content = msg_content
                single_reply.sender = sender
                single_reply.to = chat.lead.phone_number
                single_reply.message_id = chat.message_id
                single_reply.metadata = agent_response.to_dict()
                single_reply.tool_call = reply_message.tool_call

                # Send each message separately
                self.__message_repository.send_single_message(single_reply)

        except json.decoder.JSONDecodeError as e:

            response = agent_response.content
            single_reply = TextMessage()
            single_reply.content = response
            single_reply.sender = sender
            single_reply.to = chat.lead.phone_number
            single_reply.message_id = chat.message_id
            single_reply.metadata = agent_response.to_dict()
            single_reply.tool_call = reply_message.tool_call

            self.__message_repository.send_single_message(single_reply)
            self.__logger.error(f"Error decoding JSON: {e}")
            self.__logger.error(f"Agent response content: {response}")

        # Only program the later message for the last message
        self.__message_repository.program_later_message(
            single_reply, {TimeUnits.HOURS: 1}
        )

        return "ok", 200
