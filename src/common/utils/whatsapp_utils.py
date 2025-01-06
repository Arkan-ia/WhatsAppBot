import logging
from typing import Any, Dict

import requests
from src.common.utils.openai_utils import get_text_from_audio
from src.common.whatsapp.models.models import TemplateMessage, TextMessage, WhatsAppMessage
from src.data.sources.firebase.message_impl import MessageFirebaseRepository


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )


def get_whatsapp_message(message: Dict) -> str:
    """
    Extract the text from an incoming WhatsApp message.

    Args:
        message (Dict): The incoming message dictionary.

    Returns:
        str: The extracted message text.
    """
    if "type" not in message:
        return "mensaje no reconocido"

    message_type = message["type"]
    if message_type == "text":
        return message["text"]["body"]
    elif message_type == "audio":
        media_id = message["audio"]["id"]
        return get_text_from_audio(media_id)
    elif message_type == "button":
        return message["button"]["text"]
    elif message_type == "interactive":
        interactive_type = message["interactive"]["type"]
        if interactive_type == "list_reply":
            return message["interactive"]["list_reply"]["title"]
        elif interactive_type == "button_reply":
            return message["interactive"]["button_reply"]["title"]
        else:
            return "mensaje no procesado"
    else:
        return "mensaje no procesado"


def send_whatsapp_message(
    from_whatsapp_id: str, token: str, message: WhatsAppMessage
) -> None:
    """
    Send a message through the WhatsApp API.

    Args:
        data (str): The JSON-formatted message data.
    """

    api_url = f"https://graph.facebook.com/v21.0/{from_whatsapp_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    
    try:
        data = message.create_message()
        response = requests.post(api_url, headers=headers, data=data)
        if response.status_code != 200:
            # TODO: Print only in productions
            logging.info(f"Status code: {response.status_code}.")
            raise Exception(f"Failed to send message. Status code: {response.status_code}. Repsonse:{response.json()}")
        return {"status": "success", "number": message.to_number}
    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        return {"status": "error", "number": message.to_number, "message": str(e) }
