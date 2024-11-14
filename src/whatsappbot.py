#whatsappbot.py
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests

MODEL = 'gpt-4o-mini'
LOCATION = 'Pasto - Boyacá - Colombia'


class WhatsAppBot:
    """
    A class to interact with the WhatsApp API and manage chatbot conversations.
    """

    def __init__(self, api_url: str, token: str, stickers: Optional[Dict[str, str]] = None):
        """
        Initialize the WhatsAppBot with API credentials and optional media IDs.

        Args:
            api_url (str): The WhatsApp API endpoint URL.
            token (str): The authentication token for the API.
            stickers (Optional[Dict[str, str]]): A dictionary of sticker names to media IDs.
        """
        self.api_url = api_url
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.usuarios: Dict[str, Dict] = {}
        self.estados_conversacion: Dict[str, str] = {}
        self.stickers = stickers or {}

    # Conversation State Management Methods

    def update_conversation_state(self, number: str, state: str) -> None:
        """
        Update the conversation state for a user.

        Args:
            number (str): The user's phone number.
            state (str): The new conversation state.
        """
        self.estados_conversacion[number] = state
        logging.debug(f"Conversation state updated for {number}: {state}")

    def get_conversation_state(self, number: str) -> Optional[str]:
        """
        Get the current conversation state for a user.

        Args:
            number (str): The user's phone number.

        Returns:
            Optional[str]: The current conversation state.
        """
        return self.estados_conversacion.get(number)

    # Message Handling Methods

    def get_whatsapp_message(self, message: Dict) -> str:
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

    def send_whatsapp_message(self, data: str) -> None:
        """
        Send a message through the WhatsApp API.

        Args:
            data (str): The JSON-formatted message data.
        """
        try:
            response = requests.post(self.api_url, headers=self.headers, data=data)

            if response.status_code == 200:
                logging.info("Message sent successfully.")
            else:
                logging.error(
                    f"Error sending message: {response.status_code}, {response.text}"
                )
        except Exception as e:
            logging.exception(f"Exception occurred while sending message: {e}")

    # Message Creation Methods

    def text_message(self, number: str, text: str) -> str:
        """
        Create a text message in JSON format.

        Args:
            number (str): The recipient's phone number.
            text (str): The message text.

        Returns:
            str: The JSON-formatted message data.
        """
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {"body": text},
            }
        )
        return data

    def mark_read_message(self, message_id: str) -> str:
        """
        Create a JSON message to mark a message as read.

        Args:
            message_id (str): The ID of the message to mark as read.

        Returns:
            str: The JSON-formatted message data.
        """
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            }
        )
        return data

    def button_reply_message(
        self, number: str, options: List[str], body: str, footer: str, session_id: str
    ) -> str:
        """
        Create a button reply message.

        Args:
            number (str): The recipient's phone number.
            options (List[str]): List of button titles.
            body (str): The message body text.
            footer (str): The footer text.
            session_id (str): A unique identifier for the session.

        Returns:
            str: The JSON-formatted message data.
        """
        buttons = []
        for i, option in enumerate(options):
            buttons.append(
                {
                    "type": "reply",
                    "reply": {
                        "id": f"{session_id}_btn_{i+1}",
                        "title": option,
                    },
                }
            )

        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": body},
                    "footer": {"text": footer},
                    "action": {"buttons": buttons},
                },
            }
        )
        return data

    def list_reply_message(
        self, number: str, options: List[str], body: str, footer: str, session_id: str
    ) -> str:
        """
        Create a list reply message.

        Args:
            number (str): The recipient's phone number.
            options (List[str]): List of list item titles.
            body (str): The message body text.
            footer (str): The footer text.
            session_id (str): A unique identifier for the session.

        Returns:
            str: The JSON-formatted message data.
        """
        rows = []
        for i, option in enumerate(options):
            rows.append(
                {
                    "id": f"{session_id}_row_{i+1}",
                    "title": option,
                    "description": "",
                }
            )

        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": body},
                    "footer": {"text": footer},
                    "action": {
                        "button": "Ver Opciones",
                        "sections": [{"title": "Secciones", "rows": rows}],
                    },
                },
            }
        )
        return data

    def document_message(
        self, number: str, url: str, caption: str, filename: str
    ) -> str:
        """
        Create a document message.

        Args:
            number (str): The recipient's phone number.
            url (str): The URL of the document.
            caption (str): The caption for the document.
            filename (str): The filename of the document.

        Returns:
            str: The JSON-formatted message data.
        """
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "document",
                "document": {
                    "link": url,
                    "caption": caption,
                    "filename": filename,
                },
            }
        )
        return data

    def reply_reaction_message(self, number: str, message_id: str, emoji: str) -> str:
        """
        Create a reaction message to reply to a user's message.

        Args:
            number (str): The recipient's phone number.
            message_id (str): The ID of the message to react to.
            emoji (str): The emoji to use as a reaction.

        Returns:
            str: The JSON-formatted message data.
        """
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "reaction",
                "reaction": {"message_id": message_id, "emoji": emoji},
            }
        )
        return data

    def reply_text_message(
        self, number: str, message_id: str, text: str
    ) -> str:
        """
        Create a text message in reply to a user's message.

        Args:
            number (str): The recipient's phone number.
            message_id (str): The ID of the message to reply to.
            text (str): The reply text.

        Returns:
            str: The JSON-formatted message data.
        """
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "context": {"message_id": message_id},
                "type": "text",
                "text": {"body": text},
            }
        )
        return data

    # Media Management Methods

    def get_media_id(self, media_name: str, media_type: str) -> Optional[str]:
        """
        Retrieve the media ID for a given media name and type.

        Args:
            media_name (str): The name of the media.
            media_type (str): The type of media ('sticker', 'image', etc.).

        Returns:
            Optional[str]: The media ID if found, None otherwise.
        """
        if media_type == "sticker":
            return self.stickers.get(media_name)
        # Extend this method for other media types if necessary
        return None
    
    def get_media(self, id: str):
        answer = requests.post(f"https://graph.facebook.com/v21.0/{id}/", headers=self.headers)
        url = answer["url"]
        
        image = requests.get(url, headers=self.headers)
        return image


