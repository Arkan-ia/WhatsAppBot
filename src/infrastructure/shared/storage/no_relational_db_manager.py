from abc import ABC, abstractmethod, abstractproperty
from typing import Any

from injector import Binder, Module, inject, singleton
from firebase_admin.firestore import firestore


import firebase_admin
from firebase_admin import credentials, firestore as fs

from src.infrastructure.shared.logger.logger import LogAppManager


class NoRealtionalDBManager(ABC):
    @abstractmethod
    def getRawDocument(self, collection: str, document: str) -> Any:
        pass

    @abstractmethod
    def getRawCollection(self, collection: str) -> Any:
        pass

    @abstractmethod
    def getServerTimestamp(self) -> Any:
        pass

    @abstractmethod
    def getCollectionGroup(self, collection: str) -> Any:
        pass


@singleton
class FirebaseNoRelationalDBManager(NoRealtionalDBManager):
    @inject
    def __init__(self, logger: LogAppManager) -> None:
        self.__logger = logger
        self.__logger.set_caller("FirebaseNoRelationalDBManager")
        try:
            cred = credentials.Certificate(
                "src/infrastructure/shared/storage/firebase.json"
            )
            firebase_admin.initialize_app(cred)
            self.db = fs.client()
            self.__logger.info(f"Firebase started {self.db}")
        except Exception as e:
            self.__logger.error("Error starting firebase", e)

    def getRawDocument(
        self, collection: str, document: str
    ) -> firestore.DocumentReference:
        self.__db.collection_group
        return self.__db.collection(collection).document(document)

    def getRawCollection(self, collection: str) -> firestore.CollectionReference:
        return self.db.collection(collection)

    def getServerTimestamp(self) -> Any:
        return firestore.SERVER_TIMESTAMP

    def getCollectionGroup(self, collection):
        return self.__db.collection_group(collection)


class NoRelationalDBModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(
            NoRealtionalDBManager,
            to=FirebaseNoRelationalDBManager,
        )
