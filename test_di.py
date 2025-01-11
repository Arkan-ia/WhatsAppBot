from abc import ABC, abstractmethod

from injector import Injector, Module, inject, singleton
from loguru import logger

from src.infrastructure.di.container import chatbot_service, http_manager
from src.infrastructure.shared.http.http_manager import HttpManager, HttpModule
from src.infrastructure.shared.logger.logger import LoggerModule

print(chatbot_service.run("Hola", "Test market"))


class User:
    @inject
    def __init__(self, http_manager: HttpManager):
        self.http_manager = http_manager
        self.http_manager.set_base_url("https://jsonplaceholder.typicode.com")

    def get_posts(self, user_id: int):
        return self.http_manager.get(f"posts/{user_id}")


class Pokemons:
    @inject
    def __init__(self, http_manager: HttpManager):
        self.http_manager = http_manager
        self.http_manager.set_base_url("https://pokeapi.co/api/v2")

    def get_pokemons(self):
        return self.http_manager.get("ability/?limit=20&offset=20")


injector = Injector([HttpModule, LoggerModule])
user = injector.get(User)
poke = injector.get(Pokemons)
posts = user.get_posts(1)
print("posts ->", posts)
pokemons = poke.get_pokemons()

print("poke ->", pokemons)
