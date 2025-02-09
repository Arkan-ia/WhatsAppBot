from abc import ABC, abstractmethod
from typing import Any, List
from unittest.mock import MagicMock

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from injector import Module, inject

from src.infrastructure.shared.logger.logger import LogAppManager
from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper


class VectorStoreManager(ABC):
    @abstractmethod
    def get_relevant_sections(self, query: str, number_of_documents: int) -> List[str]:
        pass

    @abstractmethod
    def set_store_path(self, store_path: str) -> None:
        pass

    @abstractmethod
    def set_embedding_model(self, embedding_model: Any) -> None:
        pass


class FAISSVectorStoreManager(VectorStoreManager):
    @inject
    def __init__(self, logger: LogAppManager):
        self.__logger = logger
        self.__logger.set_caller("FAISSVectorStoreManager")
        self.__store = None
        self.__embedding_model = OpenAIEmbeddings()
        self.__path = None

    def get_relevant_sections(
        self, query: str, number_of_documents: int = 10
    ) -> List[str]:

        try:
            docs = self.__store.similarity_search(query, k=number_of_documents)
            return [doc.page_content for doc in docs]
        except Exception as e:
            self.__logger.error(f"Error retrieving relevant sections: {str(e)}")
            raise

    def __init_store(self):
        if self.__store == None:
            try:
                self.__store = FAISS.load_local(
                    self.__path,
                    self.__embedding_model,
                    allow_dangerous_deserialization=True,
                )
                self.__logger.debug(
                    f"Store initialized: {self.__store} path: {self.__path}"
                )
            except Exception as e:
                self.__logger.error(
                    f"Error initializing store: {str(e)} path: {self.__path} embedding_model: {self.__embedding_model}"
                )
                raise e

    def set_store_path(self, store_path: str) -> None:
        self.__path = store_path
        self.__init_store()

    def set_embedding_model(self, embedding_model: Any) -> None:
        self.__embedding_model = embedding_model
        self.__init_store()


VectorStoreManagerMock = MagicMock()


class VectorStoreModule(Module):
    @flexible_bind_wrapper(
        mock=VectorStoreManagerMock,
        interface=VectorStoreManager,
        to=FAISSVectorStoreManager,
    )
    def configure(self, binder):
        return
