from abc import ABC, abstractmethod
import json
import os
import sys

from injector import Binder, Module, inject, singleton
from loguru import logger


class LogAppManager(ABC):
    @abstractmethod
    def debug(self, *message: any) -> None:
        pass

    @abstractmethod
    def info(self, *message: any) -> None:
        pass

    @abstractmethod
    def warn(self, *message: any) -> None:
        pass

    @abstractmethod
    def error(self, *message: any) -> None:
        pass

    @abstractmethod
    def set_caller(self, caller: str) -> None:
        pass

    @abstractmethod
    def set_max_json_length(self, max_json_length: int) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class ConsoleLogAppManager(LogAppManager):
    @inject
    def __init__(self):
        self.__caller = "ConsoleLogAppManager"
        self.__max_json_length = 400

        logger.remove()
        logger.add(
            sys.stderr,
            format=(
                "<level>[{time:YYYY-MM-DD HH:mm:ss}] [{level}] <bg #000066><fg #2423b5><bold>[{extra[caller]}]</bold></fg #2423b5></bg #000066> {message} </level>"
            ),
            level=os.getenv("LOG_LEVEL", "DEBUG"),
            colorize=True,
        )

        self.__logger = logger

    def _get_message(self) -> str:
        return f"[{self.__caller}]"

    def _parse_message(self, *message: any) -> list[str]:
        return [
            (
                json.dumps(arg, indent=2)[: self.__max_json_length] + "... [truncated]"
                if isinstance(arg, dict)
                else str(arg)
            )
            for arg in message
        ]

    def debug(self, *message: any) -> None:
        self.__logger.debug(" ".join(self._parse_message(*message)))

    def info(self, *message: any) -> None:
        self.__logger.info(" ".join(self._parse_message(*message)))

    def warn(self, *message: any) -> None:
        self.__logger.warning(" ".join(self._parse_message(*message)))

    def error(self, *message: any) -> None:
        self.__logger.error(" ".join(self._parse_message(*message)))

    def set_caller(self, caller: str) -> None:
        self.__caller = caller
        self.__logger = self.__logger.bind(caller=caller)

    def set_max_json_length(self, max_json_length: int) -> None:
        self.__max_json_length = max_json_length

    def clear(self) -> None:
        pass


class LoggerModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(LogAppManager, to=ConsoleLogAppManager)
