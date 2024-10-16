#whatsappbot/whatsappbot.py
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

import openai
import requests


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

    # User Data Management Methods

    def save_user_data(
        self, number: str, name: Optional[str] = None, information: Optional[str] = None
    ) -> None:
        """
        Save or update user data.

        Args:
            number (str): The user's phone number.
            name (Optional[str]): The user's name.
            information (Optional[str]): Additional information from the user.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if number not in self.usuarios:
            self.usuarios[number] = {
                "nombre": name,
                "information": [information] if information else [],
                "timestamp": current_time,
                "telefono": number,
            }
        else:
            if name:
                self.usuarios[number]["nombre"] = name
            if information:
                self.usuarios[number].setdefault("information", []).append(information)

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

    # GPT-4 Integration Methods

    def validate_input_with_gpt(
        self, input_text: str, validation_type: str
    ) -> bool:
        """
        Use GPT-4 to validate if the input is a valid name or entity.

        Args:
            input_text (str): The user's input text.
            validation_type (str): The type of validation ('nombre' or 'entidad').

        Returns:
            bool: True if valid, False otherwise.
        """
        if validation_type == "nombre":
            system_prompt = (
                "You are a validator for names. Respond with 'TRUE' if the input is a name and 'FALSE' otherwise."
            )
            prompt = f"Is '{input_text}' a valid name?"
        elif validation_type == "entidad":
            system_prompt = (
                "You are a validator for entities. Respond with 'TRUE' if the input is a valid entity and 'FALSE' otherwise."
            )
            prompt = f"Is '{input_text}' a valid entity?"
        else:
            logging.warning(f"Unknown validation type: {validation_type}")
            return False

        try:
            validation_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=5,
                temperature=0,
            )
            response_text = (
                validation_response["choices"][0]["message"]["content"].strip().lower()
            )
            return response_text == "true"
        except Exception as e:
            logging.exception(f"Error with OpenAI API during validation: {e}")
            return False

    def generate_llm_response(
        self,
        user_message: str,
        conversation_state: str,
        user_data: Dict,
        validation_success: bool = True,
    ) -> str:
        """
        Generate a response using GPT-4 based on the conversation state.

        Args:
            user_message (str): The user's message.
            conversation_state (str): The current state of the conversation.
            user_data (Dict): The user's data.
            validation_success (bool): Whether the previous validation was successful.

        Returns:
            str: The generated response text.
        """
        system_prompt = (
            "You are an assistant who speaks informally and directly. Respond in a friendly tone."
        )

        if conversation_state == "solicitar_nombre":
            prompt = "Ask the user for their name in a friendly tone."
        elif conversation_state == "esperando_nombre":
            if validation_success:
                prompt = "Thank the user for their name and ask them what they are looking for."
            else:
                prompt = "Request the user's name again as their previous input was invalid."
        elif conversation_state == "esperando_information":
            if validation_success:
                prompt = "Thank the user for providing the information and ask if they need anything else."
            else:
                prompt = "Ask the user to provide a valid entity."
        else:
            prompt = f"Handle the user's message: '{user_message}' in a friendly tone."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logging.exception(f"Error with OpenAI API during response generation: {e}")
            return "Sorry, there was a system error. Please try again."
    # GPT-4 Integration Methods

    def interpret_user_message(self, user_message: str) -> tuple:
        """
        Uses GPT-4 to interpret the user's message and determine their intent.
        Returns a tuple (intent, entity), where 'intent' can be 'affirmative', 'negative', 'provide_entity', or 'other'.
        If 'intent' is 'provide_entity', 'entity' will contain the name of the entity; otherwise, it will be None.
        """
        system_prompt = (
            "Eres un asistente que interpreta mensajes de usuarios para determinar su intención. "
            "Las posibles intenciones son: 'affirmative' si el usuario está diciendo que sí o afirmando; "
            "'negative' si el usuario está diciendo que no o negando; "
            "'provide_entity' si el usuario está mencionando una nueva entidad que necesita; "
            "o 'other' si el mensaje no encaja en las anteriores. "
            "Responde únicamente con un JSON en el siguiente formato:\n"
            '{"intent": "intention", "entity": "entity_name_or_null"}\n'
            "Si la intención es 'provide_entity', incluye la 'entity' mencionada; de lo contrario, 'entity' debe ser null."
        )
        prompt = f"El usuario ha dicho: '{user_message}'.\nDetermina su intención y responde en el formato indicado."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.0
            )
            response_text = response['choices'][0]['message']['content'].strip()
            print(f"Interpretation of user message: '{response_text}'")  

            # Parse the JSON response
            result = json.loads(response_text)
            intent = result.get('intent', 'other')
            entity = result.get('entity', None)
            if entity == 'null':
                entity = None
            return intent, entity
        except Exception as e:
            print(f"Error interpreting user message: {e}")
            return 'other', None
          
    def is_requesting_pdf(self, user_message: str) -> bool:
        """
        Determines if the user is requesting a PDF (menu, prices, catalog) using GPT-4.

        Args:
            user_message (str): The user's message.

        Returns:
            bool: True if the user is requesting a PDF, False otherwise.
        """
        system_prompt = (
            "You are an assistant that helps determine if the user is requesting a menu, prices, catalog, or something related. "
            "Respond only with 'Yes' or 'No'. Do not add any additional text."
        )
        prompt = f"The user has said: '{user_message}'.\nIs the user requesting a menu, prices, catalog, or something related?"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3,
                temperature=0
            )
            response_text = response['choices'][0]['message']['content'].strip().lower()
            logging.debug(f"PDF request validation response: '{response_text}'")
            is_requesting = response_text.startswith('yes')
            return is_requesting
        except Exception as e:
            logging.exception(f"Error with OpenAI API during PDF request validation: {e}")
            return False
