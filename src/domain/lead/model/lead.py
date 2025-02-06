from typing import Dict


class Lead:
    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, email: str):
        self.__email = email

    @property
    def phone_number(self) -> str:
        return self.__phone

    @phone_number.setter
    def phone_number(self, phone: str):
        self.__phone = phone

    @property
    def purchase_count(self):
        return self.__purchase_count

    @purchase_count.setter
    def purchase_count(self, count):
        self.__purchase_count = count

    @property
    def last_message(self) -> Dict[str, any]:
        return self.__last_message

    @last_message.setter
    def last_message(self, message: Dict[str, any]):
        self.__last_message = message

    @property
    def citizen_id(self) -> str:
        return self.__citizen_id

    @citizen_id.setter
    def citizen_id(self, id: str):
        self.__citizen_id = id

    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, address: str):
        self.__address = address

    @property
    def city(self) -> str:
        return self.__city

    @city.setter
    def city(self, city: str):
        self.__city = city

    def is_valid_phone_number(self):
        return len(self.phone_number) == 12
