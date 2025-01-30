from abc import ABC, abstractmethod
import time
from typing import Any, Dict, List
from unittest.mock import MagicMock

from injector import Injector, Module, inject, singleton

from src.data.models.chatbot import ChatbotModel
from src.data.sources.firebase import chat_configs
from src.infrastructure.shared.logger.logger import LogAppManager
from src.data.sources.firebase.chat_configs import chatbot_configs

from src.infrastructure.shared.utils.decorators import flexible_bind_wrapper
from src.infrastructure.shared.vectorstore.vector_store_manager import (
    VectorStoreManager,
)
from openai import OpenAI


class GPTManager(ABC):
    @abstractmethod
    def process_message(self, message: str, gpt_id: str) -> str:
        pass

    @abstractmethod
    def process_messages(
        self, messages: List[str], query: str, gpt_id: str, relevant_promt_data: str
    ) -> str:
        pass

    @abstractmethod
    def set_tools(self, tools: List[Any]) -> None:
        pass

    @abstractmethod
    def generate_answer(self, messages: List[str], gpt_id: str) -> str:
        pass


@singleton
class OpenAIGPTManager(GPTManager):
    @inject
    def __init__(self, logger: LogAppManager, injector: Injector):
        # TODO: get paths and data from config or database
        agent_configs_data = [
            {
                "business": {"id": "450361964838178", "name": "Gano Excel"},
                "vectorstore_path": "./vectorstores/juan_gano_excel",
                "embedding_key": "OpenIA",
                "max_tokens": 800,
                "model": "gpt-4o-mini",
                "temperature": 0.1,
            }
        ]

        vector_stores = {}
        agent_configs = {}
        for config in agent_configs_data:
            store: VectorStoreManager = injector.get(VectorStoreManager)
            store.set_store_path(config["vectorstore_path"])
            vector_stores[config["business"]["id"]] = store
            agent_configs[config["business"]["id"]] = {
                "model": config["model"],
                "max_tokens": config["max_tokens"],
                "temperature": config["temperature"],
            }
        self.__agent_configs = agent_configs
        self.__logger = logger
        self.__logger.set_caller("OpenAIGPTManager")
        self.__vector_stores = vector_stores
        self.__client = OpenAI()
        self.__tools = []

    def process_message(self, message: str) -> str:
        return message

    def process_messages(
        self, messages: List[str], query: str, gpt_id: str, relevant_promt_data: str
    ) -> str:
        vector_store = self.__vector_stores[gpt_id]
        if vector_store == None:
            self.__logger.error(f"No vector store found for GPT with ID: {gpt_id}")
            raise Exception(f"No vector store found for GPT with ID: {gpt_id}")
        # TODO: impelment image processing

        # TODO: The specific prompt should be trianed on model to avoid send a lot of token on each message
        business_propmt = ChatbotModel(**chatbot_configs[gpt_id]).system_prompt

        try:
            # TODO: Review vectorial db becase it is not working at all
            # And also take a lot of time to excecute query and search from 1.1s to 1.6s
            start_time = time.time()
            # relevant_sections = vector_store.get_relevant_sections(query, 10)
            self.__logger.debug(
                f"Time to retrieve relevant sections: {time.time() - start_time}"
            )
            # context = " ".join(relevant_sections)
            # print("Context----->", context) # Printed to see whats happening with the "context"
            system_prompt = (
                f"{business_propmt}"
                # f"Contexto relevante: {context}"
                f"{relevant_promt_data}"
            )
            messages = [{"role": "system", "content": system_prompt}, *messages]
            response = self.generate_answer(messages, gpt_id)
            self.__logger.debug(f"Answer from gpt: {response}")
            return response.content
        except Exception as e:
            self.__logger.error(f"Error processing request: {str(e)}")
            raise e

    def set_tools(self, tools: List[Any]) -> None:
        self.__tools = tools

    def generate_answer(self, messages: List[str], gpt_id: str) -> str:
        try:
            model = self.__agent_configs[gpt_id]["model"]
            max_tokens = self.__agent_configs[gpt_id]["max_tokens"]
            temperature = self.__agent_configs[gpt_id]["temperature"]
            response = self.__client.chat.completions.create(
                model=model,
                messages=messages,
                tools=self.__tools,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message
        except Exception as e:
            self.__logger.error(
                f"Error generating answer: {str(e)}",
                f"model:{model}",
                f"max_tokens:{max_tokens}",
                f"temperature:{temperature}",
            )
            raise e


MockGPTManager = MagicMock()


class GPTManagerModule(Module):
    @flexible_bind_wrapper(
        mock=MockGPTManager, interface=GPTManager, to=OpenAIGPTManager
    )
    def configure(self, binder):
        return
