from datetime import datetime
import logging
from typing import Dict, Optional


def save_user_data(
        self, number: str, name: Optional[str] = None, order: Optional[str] = None, address: Optional[str] = None
) -> None:
    """
    Save or update user data.

    Args:
        number (str): The user's phone number.
        name (Optional[str]): The user's name.
        order (Optional[str]): The user's order.
        address (Optional[str]): The user's address.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if number not in self.usuarios:
        self.usuarios[number] = {
            "nombre": name,
            "order": order,
            "address": address,
            "timestamp": current_time,
            "telefono": number,
        }
    else:
        if name:
            self.usuarios[number]["name"] = name
        if order:
            self.usuarios[number]["order"] = order
        if address:
            self.usuarios[number]["address"] = address

        self.usuarios[number]["timestamp"] = current_time

    logging.debug(f"Updated user data: {self.usuarios[number]}")


def get_user_data(self, number: str) -> Dict:
    """
    Retrieve user data.

    Args:
        number (str): The user's phone number.

    Returns:
        Dict: The user's data dictionary.
    """
    return self.usuarios.get(number, {})

def is_user_info_missing(self, number: str) -> bool:
    """
    Check if the user is missing required information.

    Args:
        number (str): The user's phone number.

    Returns:
        bool: True if information is missing, False otherwise.
    """
    usuario = self.usuarios.get(number, {})
    return not usuario.get("nombre") or not usuario.get("information")