from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
import requests
from injector import Binder, inject, Module, provider, singleton
from urllib.parse import urljoin

T = TypeVar('T')

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
    def __init__(self):
        self.__base_url__ = ""
        self.__headers__ = {}

    def build_url(self, url: str) -> str:
        return urljoin(self.__base_url__, url)
    
    def set_base_url(self, base_url: str) -> None:
        # determinate if last char is /
        if base_url[-1] != "/":
            base_url += "/"
        self.__base_url__ = base_url

    def get(self, url: str) -> T:
        full_url = self.build_url(url)
        try:
            response = requests.get(full_url, headers=self.__headers__)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise e

    def post(self, url: str, body: Any, headers: dict = None) -> T:
        full_url = self.build_url(url)
        try:
            combined_headers = {**self.__headers__, **(headers or {})}
            response = requests.post(full_url, json=body, headers=combined_headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise e

    def set_token(self, token: str) -> None:
        if len(token) < 10:
            raise ValueError("Invalid token")
        self.__headers__['Authorization'] = token

class HttpModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(HttpManager, to=RequestsHttpManager)