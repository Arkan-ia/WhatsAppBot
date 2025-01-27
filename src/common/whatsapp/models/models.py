from abc import ABC, abstractmethod
import json
from typing import Dict, Any, List


class WhatsAppMessage(ABC):
    def __init__(self, to_number):
        self.to_number = to_number

    @abstractmethod
    def create_message(self) -> Dict[str, Any]:
        pass


class TemplateMessage(WhatsAppMessage):
    def __init__(self, to_number, template, code="es", parameters=None):
        self.to_number = to_number
        self.template = template
        self.code = code
        self.parameters = parameters

    def create_message(self):
        template_object = {
            "name": self.template,
            "language": {"code": self.code},
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "link": "https://firebasestorage.googleapis.com/v0/b/arcania-c4669.appspot.com/o/ganeexcel1.jpg?alt=media&token=8c3e0644-13b7-49fd-9f66-4c7b303a149e"
                            },
                        }
                    ],
                }
            ],
        }
        if self.parameters:
            template_object["components"] = [
                {"type": "body", "parameters": self.parameters},
            ]
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "to": self.to_number,
                "type": "template",
                "template": template_object,
            }
        )


class TextMessage(WhatsAppMessage):
    def __init__(self, number, text):
        self.to_number = number
        self.text = text

    def create_message(self):
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.to_number,
                "type": "text",
                "text": {"body": self.text},
            }
        )


class MarkReadMessage(WhatsAppMessage):
    to_number = "" #N No quitar

    def __init__(self, message_id: str):
        self.message_id = message_id

    def create_message(self) -> Dict[str, Any]:
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": self.message_id,
            }
        )


class ButtonReplyMessage(WhatsAppMessage):
    def __init__(
        self, number: str, options: List[str], body: str, footer: str, session_id: str
    ):
        self.to_number = number
        self.options = options
        self.body = body
        self.footer = footer
        self.session_id = session_id

    def create_message(self) -> Dict[str, Any]:
        buttons = []
        for i, option in enumerate(self.options):
            buttons.append(
                {
                    "type": "reply",
                    "reply": {
                        "id": f"{self.session_id}_btn_{i+1}",
                        "title": option,
                    },
                }
            )

        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.to_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": self.body},
                    "footer": {"text": self.footer},
                    "action": {"buttons": buttons},
                },
            }
        )


class ListReplyMessage(WhatsAppMessage):
    def __init__(
        self, number: str, options: List[str], body: str, footer: str, session_id: str
    ):
        self.to_number = number
        self.options = options
        self.body = body
        self.footer = footer
        self.session_id = session_id

    def create_message(self) -> Dict[str, Any]:
        rows = []
        for i, option in enumerate(self.options):
            rows.append(
                {
                    "id": f"{self.session_id}_row_{i+1}",
                    "title": option,
                    "description": "",
                }
            )

        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.to_number,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": self.body},
                    "footer": {"text": self.footer},
                    "action": {
                        "button": "Ver Opciones",
                        "sections": [{"title": "Secciones", "rows": rows}],
                    },
                },
            }
        )


class DocumentMessage(WhatsAppMessage):
    def __init__(self, number: str, url: str, caption: str, filename: str):
        self.to_number = number
        self.url = url
        self.caption = caption
        self.filename = filename

    def create_message(self) -> Dict[str, Any]:
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.to_number,
                "type": "document",
                "document": {
                    "link": self.url,
                    "caption": self.caption,
                    "filename": self.filename,
                },
            }
        )


class ReplyReactionMessage(WhatsAppMessage):
    def __init__(self, number: str, message_id: str, emoji: str):
        self.to_number = number
        self.message_id = message_id
        self.emoji = emoji

    def create_message(self) -> Dict[str, Any]:
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.to_number,
                "type": "reaction",
                "reaction": {"message_id": self.message_id, "emoji": self.emoji},
            }
        )


class ReplyTextMessage(WhatsAppMessage):
    def __init__(self, number: str, message_id: str, text: str):
        self.to_number = number
        self.message_id = message_id
        self.text = text

    def create_message(self) -> Dict[str, Any]:
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.to_number,
                "context": {"message_id": self.message_id},
                "type": "text",
                "text": {"body": self.text},
            }
        )
