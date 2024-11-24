from datetime import datetime
import logging
from typing import Dict, Optional

usuarios = {}

def save_user_data(
         number: str, name: Optional[str] = None, order: Optional[str] = None, address: Optional[str] = None
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

    if number not in usuarios:
        usuarios[number] = {
            "nombre": name,
            "order": order,
            "address": address,
            "timestamp": current_time,
            "telefono": number,
        }
    else:
        if name:
            usuarios[number]["name"] = name
        if order:
            usuarios[number]["order"] = order
        if address:
            usuarios[number]["address"] = address

        usuarios[number]["timestamp"] = current_time

    logging.debug(f"Updated user data: {usuarios[number]}")


def get_user_data( number: str) -> Dict:
    """
    Retrieve user data.

    Args:
        number (str): The user's phone number.

    Returns:
        Dict: The user's data dictionary.
    """
    return usuarios.get(number, {})

def is_user_info_missing( number: str) -> bool:
    """
    Check if the user is missing required information.

    Args:
        number (str): The user's phone number.

    Returns:
        bool: True if information is missing, False otherwise.
    """
    usuario = usuarios.get(number, {})
    return not usuario.get("nombre") or not usuario.get("information")


def get_whatsapp_token(from_id: str) -> str:
    # Esta función debería consultar una base de datos.
    print("from_id: ", from_id)
    if from_id == "541794965673706":
        return "EAAFcOeGfUCEBO4ZAEeQhrAghK6M7R3PZA9yjyU96pehgNZCyWB0TWEOCJB93Ukdcy1XGCrBjUZCgE4CG6um0EW64NYPed4zdQTQxaGsShnZBgZC0Q4UxhgtqnmgRkZCeFfPL5KM0WoTRKk4wfmTUVnoHENFov8vu5u9jesswSQFxmiroOLV0yPZAdywQXx8Ta1j7mgZDZD"
