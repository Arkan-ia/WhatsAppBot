from typing import Dict, List

from injector import inject, singleton
import pandas as pd

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
    def __init__(self, message_repository: MessageRepository):
        self.__message_repository = message_repository

    def run(self, file: any, metadata: Dict[str, str]):
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
        for user in users:
            if not user.isdigit():
                continue

            msg: Message = TextMessage(message)
            msg.sender = sender
            msg.to = user

            if template:
                msg: Message = TemplateMessage()
                msg.sender = sender
                msg.to = user
                msg.template = template
                msg.code = language_code
                msg.parameters = parameters

            messages.append(msg)

        return self.__message_repository.send_massive_message(messages)
