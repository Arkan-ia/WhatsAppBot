from typing import Dict, List

from injector import inject, singleton
import pandas as pd

from src.domain.business.port.business_repository import BusinessRepository
from src.domain.errors.business_not_found import BusinessNotFoundError
from src.domain.message.model.message import (
    Message,
    Sender,
    TemplateMessage,
    TextMessage,
    WhatsAppSender,
)
from src.domain.message.port.message_repository import MessageRepository


@singleton
class SendMassiveMesageService:
    @inject
    def __init__(
        self,
        message_repository: MessageRepository,
        business_repository: BusinessRepository,
    ):
        self.__message_repository = message_repository
        self.__business_repository = business_repository

    def run(self, file: any, metadata: Dict[str, str]):
        if not self.__business_repository.exists(metadata.get("from_id")):
            raise BusinessNotFoundError(metadata.get("from_id"))
        file_data = pd.read_excel(file, header=None, converters={0: str})
        users = file_data[0].tolist()

        template = metadata.get("template")
        language_code = metadata.get("language_code")
        message = metadata.get("message")
        parameters = metadata.get("parameters")

        sender: Sender = WhatsAppSender()
        sender.from_identifier = metadata.get("from_id")
        sender.from_token = metadata.get("token")

        messages: List[Message] = []
        template_data = ""
        for user in users:
            if not user.isdigit():
                continue

            msg: Message = TextMessage()
            msg.sender = sender
            msg.to = user
            msg.content = message

            if template:
                if len(template_data) == 0:
                    # TODO: Apply and test raise exceptio when a template doesnt exists
                    template_data = self.__message_repository.get_template_data(
                        metadata.get("from_id"), template
                    )
                msg: Message = TemplateMessage()
                msg.sender = sender
                msg.to = user
                msg.template = template
                msg.code = language_code
                msg.parameters = parameters
                msg.content = template_data

            messages.append(msg)

        return self.__message_repository.send_massive_message(messages)
