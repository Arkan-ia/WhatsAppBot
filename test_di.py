from abc import ABC, abstractmethod
from injector import Injector, Module, singleton, inject

# Definición de la interfaz abstracta Animal
class Animal(ABC):
    @abstractmethod
    def make_sound(self) -> str:
        pass

    @abstractmethod
    def move(self) -> str:
        pass

# Implementación concreta de Dog
class Dog(Animal):
    def make_sound(self) -> str:
        return "Bark"

    def move(self) -> str:
        return "Runs"

# Implementación concreta de Bird
class Bird(Animal):
    def make_sound(self) -> str:
        return "Chirp"

    def move(self) -> str:
        return "Flies"

# Servicio que utiliza Animal como dependencia
class AnimalService:
    @inject
    def __init__(self, animal: Animal) -> None:
        self.animal = animal

    def describe_animal(self) -> str:
        return f"Sound: {self.animal.make_sound()}, Movement: {self.animal.move()}"

# Configuración del contenedor de inyección
class AnimalModule(Module):
    def configure(self, binder) -> None:
        # Aquí configuramos qué implementación usar para la interfaz Animal
        binder.bind(Animal, to=Bird, scope=singleton)  # Cambiar Dog por Bird si deseas

# Crear el contenedor e inyectar dependencias
injector = Injector([AnimalModule])

# Instancia de AnimalService con dependencia inyectada
animal_service = injector.get(AnimalService)

# Uso del servicio
print(animal_service.describe_animal())  # Output: Sound: Bark, Movement: Runs
