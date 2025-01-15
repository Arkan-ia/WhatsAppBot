from typing import Dict

from injector import inject, singleton
import pandas as pd

from src.domain.message.model.message import Message, Sender
from src.domain.message.port.message_repository import MessageRepository


@singleton
class SendMassiveMesageService:
    @inject
    def __init__(self, message_repository: MessageRepository):
        self.__message_repository = message_repository

    def run(self, file: any, metadata: Dict[str, str]):
        file_data = pd.read_excel(file, header=None)
        users = file_data[0].tolist()
        print(len(users))
        print(metadata)
        return "Hola"
        # return self.__message_repository.send_single_message(message)
