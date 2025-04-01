from abc import ABC, abstractmethod
import json
import os
import time
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock

from injector import Injector, Module, inject, singleton

from src.data.models.chatbot import ChatbotModel
from src.data.sources.firebase import chat_configs
from src.domain.chat.port.chat_repository import ActionHandler, AgentResponse, ToolCall
from src.infrastructure.shared.logger.logger import LogAppManager
from src.data.sources.firebase.chat_configs import chatbot_configs


from src.infrastructure.shared.messaging.messaging_manager import MessagingManager
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
    ) -> AgentResponse:
        pass

    @abstractmethod
    def set_tools(self, tools: List[ActionHandler]) -> None:
        pass

    @abstractmethod
    def generate_answer(self, messages: List[str], gpt_id: str) -> str:
        pass

    @abstractmethod
    def continue_conversation(self, messages: List[str], gpt_id: str) -> AgentResponse:
        pass


@singleton
class OpenAIGPTManager(GPTManager):
    @inject
    def __init__(
        self,
        logger: LogAppManager,
        injector: Injector,
    ):
        # TODO: get paths and data from config or database
        agent_configs_data = [
            {
                "business": {"id": "450361964838178", "name": "Gano Excel"},
                "vectorstore_path": "./vectorstores/juan_gano_excel",
                "embedding_key": "OpenIA",
                "max_tokens": 800,
                "model": "gpt-4o-mini",
                "temperature": 0.1,
            },
            {
                "business": {"id": "400692489794103", "name": "Gano Excel"},
                "vectorstore_path": "./vectorstores/juan_gano_excel",
                "embedding_key": "OpenIA",
                "max_tokens": 800,
                "model": "gpt-4o-mini",
                "temperature": 0.1,
            },
            {
                "business": {"id": "511736975350831", "name": "Kevin"},
                "vectorstore_path": "./vectorstores/juan_gano_excel",
                "embedding_key": "OpenIA",
                "max_tokens": 800,
                "model": "gpt-4o-mini",
                "temperature": 0.1,
            },
            {
                "business": {"id": "527260523813925", "name": "Party Egls"},
                "vectorstore_path": "./vectorstores/juan_gano_excel",
                "embedding_key": "OpenIA",
                "max_tokens": 800,
                "model": "gpt-4o-mini",
                "temperature": 0.1,
            },
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
        self.__client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.__tools = []
        self.__action_handlers = []

    def process_message(self, message: str) -> str:
        return message

    def process_messages(
        self, messages: List[str], query: str, gpt_id: str, relevant_promt_data: str
    ) -> AgentResponse:
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

            return response
        except Exception as e:
            self.__logger.error(f"Error processing request: {str(e)}")
            raise e

    def continue_conversation(self, messages: List[str], gpt_id: str) -> AgentResponse:
        continue_conversation_prompt = """
        La conversación ha acabado porque el usuario no volvió a responder. Analiza el contexto y determina si el usuario mostró interés en una compra o acción específica.

        Retorna un JSON con la siguiente estructura:
        {
            "should_reply": boolean,  # true si el usuario mostró interés en comprar o continuar, false si no hay indicios claros de interés.
            "message": string | null  # Mensaje para reabrir la conversación si corresponde, de lo contrario, null.
        }

        Consideraciones:
        - Si el usuario hizo preguntas sobre precios, disponibilidad o mostró intención de compra, devuelve "should_reply": true.
        - Si la conversación quedó en un punto neutro o sin señales claras de interés, devuelve "should_reply": false.
        - Si decides reabrir la conversación, hazlo de forma natural y sin presión, por ejemplo, con una pregunta amigable o recordatorio.
        """
        messages = [
            *messages,
            {"role": "user", "content": continue_conversation_prompt},
        ]
        return self.process_messages(
            messages, continue_conversation_prompt, gpt_id, relevant_promt_data=""
        )

    def set_tools(self, action_handlers: List[ActionHandler]) -> None:
        tools = []
        for handler in action_handlers:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": handler.name,
                        "description": handler.description,
                        "parameters": {
                            "type": "object",
                            "properties": handler.params,
                            "required": handler.required_params,
                        },
                    },
                }
            )
        self.__action_handlers = action_handlers
        self.__tools = tools

    def generate_answer(self, messages: List[str], gpt_id: str) -> AgentResponse:
        try:
            model = self.__agent_configs[gpt_id]["model"]
            max_tokens = self.__agent_configs[gpt_id]["max_tokens"]
            temperature = self.__agent_configs[gpt_id]["temperature"]
            res = self.__client.chat.completions.create(
                model=model,
                messages=messages,
                tools=self.__tools,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response = res.choices[0].message
            has_tool_calls, tool_cals = self.__get_response_metadata(response)
            print(f"Has tool calls: {has_tool_calls}, tool calls: {tool_cals}")

            return AgentResponse(
                content=response.content,
                role=response.role,
                tool_calls=tool_cals,
                message_id=res.id,
                has_tool_calls=has_tool_calls,
            )

        except Exception as e:
            self.__logger.error(
                f"Error generating answer: {str(e)}",
                f"model:{model}",
                f"max_tokens:{max_tokens}",
                f"temperature:{temperature}",
            )
            raise e

    def __get_response_metadata(self, response) -> Tuple[bool, List[ToolCall]]:
        tool_calls = []
        has_tool_calls = False

        # TODO: Test manually this part
        if hasattr(response, "tool_calls") and response.tool_calls:
            has_tool_calls = True
            for tool_call in response.tool_calls:
                typee = tool_call.type
                idd = tool_call.id
                function = tool_call.function
                name = function.name
                arguments = function.arguments
                tool_calls.append(
                    ToolCall(
                        name=name, idd=idd, arguments=json.loads(arguments), typee=typee
                    )
                )

        return has_tool_calls, tool_calls


MockGPTManager = MagicMock()


class GPTManagerModule(Module):
    @flexible_bind_wrapper(
        mock=MockGPTManager, interface=GPTManager, to=OpenAIGPTManager
    )
    def configure(self, binder):
        return
