from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from urllib.parse import urljoin

from injector import Binder, Module, inject, provider, singleton
import requests

from src.infrastructure.shared.logger.logger import LogAppManager

T = TypeVar("T")


class HttpManager(ABC, Generic[T]):
    """Interface for HTTP Manager."""

    @abstractmethod
    def get(self, url: str) -> T:
        """Perform a GET request."""
        pass

    @abstractmethod
    def post(self, url: str, body: Any, headers: dict = None) -> T:
        """Perform a POST request."""
        pass

    @abstractmethod
    def set_token(self, token: str) -> None:
        """Set the authorization token for the HTTP requests."""
        pass

    @abstractmethod
    def set_base_url(self, base_url: str) -> None:
        """Set the base URL for the HTTP requests."""
        pass


class RequestsHttpManager(HttpManager):
    @inject
    def __init__(self, logger: LogAppManager):
        self.__base_url = ""
        self.__headers = {}
        self.__logger = logger
        self.__logger.set_caller("RequestsHttpManager")
        self.__logger.set_max_json_length(400)

    def build_url(self, url: str) -> str:
        return f"{self.__base_url.rstrip('/')}/{url.lstrip('/')}"

    def set_base_url(self, base_url: str) -> None:
        # determinate if last char is /
        if base_url[-1] != "/":
            base_url += "/"
        self.__base_url = base_url

    def get(self, url: str) -> T:
        full_url = self.build_url(url)
        try:
            response = requests.get(full_url, headers=self.__headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.__logger.error(
                "Error in GET",
                f"[URL:{full_url}]",
                f"[ERROR:{e}]",
                f"[HEADERS:{self.__headers}]",
            )
            raise e

    def post(self, url: str, body: Any, headers: dict = None) -> T:
        full_url = self.build_url(url)
        try:
            combined_headers = {**self.__headers, **(headers or {})}
            response = requests.post(full_url, json=body, headers=combined_headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.__logger.error(
                "Error in POST",
                f"[URL:{full_url}]",
                f"[ERROR:{e}]",
                f"[HEADERS:{combined_headers}]",
                f"[BODY:{body}]",
            )
            raise e

    def set_token(self, token: str) -> None:
        if len(token) < 10:
            raise ValueError("Invalid token")
        self.__headers["Authorization"] = token


class HttpModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(HttpManager, to=RequestsHttpManager)
