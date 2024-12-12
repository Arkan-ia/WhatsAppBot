#whatsappbot.py
import json
import logging
from datetime import datetime
import os
from typing import Any, Dict, List, Optional
import requests
from openai import OpenAI

client = OpenAI() 
OPENAI_API_KEY="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"

from src.db.firebase import upload_media_to_storage, upload_audio_to_storage

MODEL = 'gpt-4o-mini'
LOCATION = 'Pasto - Boyacá - Colombia'


class WhatsAppAPIHandler:
    """
    A class to interact with the WhatsApp API and manage chatbot conversations.
    """

    def __init__(self, from_whatsapp_id: str, token: str, stickers: Optional[Dict[str, str]] = None):
        """
        Initialize the WhatsAppBot with API credentials and optional media IDs.

        Args:
            api_url (str): The WhatsApp API endpoint URL.
            token (str): The authentication token for the API.
            stickers (Optional[Dict[str, str]]): A dictionary of sticker names to media IDs.
        """
        self.from_whatsapp_id = from_whatsapp_id
        self.api_url = f"https://graph.facebook.com/v21.0/{from_whatsapp_id}/messages"
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.stickers = stickers or {}

    def start_conversation(self, template: str, to_number: str) -> None:
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template,
                "language": {
                    "code": "es"
                }
            },
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, data=data)

            if response.status_code == 200:
                print(f"Message sent successfully to {to_number}")
            else:
                logging.error(f"Failed to send message to {to_number}: {response.text}")
        except Exception as e:
            logging.exception(f"Exception occurred while sending message: {e}")

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
        elif message_type == "audio":
            media_id = message["audio"]["id"]
            return self.get_text_from_audio(media_id)
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
        
    def get_text_from_audio(self, media_id: str) -> str:
        """
        Convert an audio file to text using the OpenAI API.

        Args:
            audio_url (str): The URL of the audio file.

        Returns:
            str: The extracted text from the audio.
        """
        
        audio_media_response = self.get_media_response(media_id)
        
        # Upload to firestore
        file_name = f"audios/{media_id}.ogg"
        audio_path = upload_audio_to_storage(audio_media_response, file_name) #self.download_audio(audio_url)
        
        downloaded_audio_path = self.download_audio(audio_media_response.json()['url'])
        print(f"Audio descargado: {audio_path}")
        transcription = self.transcribe_audio(downloaded_audio_path)
        print(f"Transcripción: {transcription}")
        
        if os.path.exists(downloaded_audio_path):
            os.remove(downloaded_audio_path)
        
        return transcription
        
        #return transcription
    
    def get_media_response(self,media_id: str) -> str:
        """Obtener la URL del archivo de audio."""
        url = f"https://graph.facebook.com/v21.0/{media_id}"
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            # response.raise_for_status()
            return response
            
        except Exception as e:
            logging.exception(f"Exception occurred while sending message: {e}")
            
    def download_audio(self, url: str) -> str:
        """Descargar el archivo de audio."""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        file_path = "audio.ogg"
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return file_path
    
    def transcribe_audio(self,file_path):
        """Enviar el archivo de audio a OpenAI y obtener la transcripción."""
        response = client.audio.transcriptions.create(
            file=open(file_path, "rb"),
            model="whisper-1",
            response_format="text",
        )
        return response
    def send_whatsapp_message(self, data: str) -> None:
        """
        Send a message through the WhatsApp API.

        Args:
            data (str): The JSON-formatted message data.
        """
        try:
            response = requests.post(self.api_url, headers=self.headers, data=data)

            if response.status_code == 200:
                print("Message sent successfully.")
            else:
                logging.error(
                    f"Error sending message: {response.status_code}, {response.text}"
                )
        except Exception as e:
            logging.exception(f"Exception occurred while sending message: {e}")

    # Message Creation Methods

    def text_message(self, number: str, text: str) -> Dict[str, Any]:
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

    def mark_read_message(self, message_id: str) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
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

    def reply_reaction_message(self, number: str, message_id: str, emoji: str) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
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
        answer = requests.get(f"https://graph.facebook.com/v21.0/{id}/", headers=self.headers)
        if answer.status_code == 200:
            answer = answer.json()
            print("answer: ", answer)
            url = answer["url"]

            image = requests.get(url, headers=self.headers)
            
            return upload_media_to_storage(image, id)
        else:
            raise Exception(f"Error getting media: {answer.status_code}, {answer.text}")
    
    # Utility methods
    def handle_message(self, message: Dict[str, Any]):                
        text = self.get_whatsapp_message(message)
        message_id = message.get('id', None)

        return self.mark_read_message(message_id)
            

