from abc import ABC, abstractmethod
import json
from typing import Dict, Any, List


class WhatsAppMessage(ABC):
    @abstractmethod
    def create_message(self) -> Dict[str, Any]:
        pass


class TemplateMessage(WhatsAppMessage):
    def __init__(self, to_number, template):
        self.to_number = to_number
        self.template = template

    def create_message(self):
        return json.dumps({
            "messaging_product": "whatsapp",
            "to": self.to_number,
            "type": "template",
            "template": {"name": self.template, "language": {"code": "es"}},
        })


class TextMessage(WhatsAppMessage):
    def __init__(self, number, text):
        self.number = number
        self.text = text

    def create_message(self):
        return json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.number,
            "type": "text",
            "text": {"body": self.text},
        })


class MarkReadMessage(WhatsAppMessage):
    def __init__(self, message_id: str):
        self.message_id = message_id

    def create_message(self) -> Dict[str, Any]:
        return json.dumps({
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": self.message_id,
        })


class ButtonReplyMessage(WhatsAppMessage):
    def __init__(
        self, number: str, options: List[str], body: str, footer: str, session_id: str
    ):
        self.number = number
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

        return json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": self.body},
                "footer": {"text": self.footer},
                "action": {"buttons": buttons},
            },
        })


class ListReplyMessage(WhatsAppMessage):
    def __init__(
        self, number: str, options: List[str], body: str, footer: str, session_id: str
    ):
        self.number = number
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

        return json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.number,
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
        })


class DocumentMessage(WhatsAppMessage):
    def __init__(self, number: str, url: str, caption: str, filename: str):
        self.number = number
        self.url = url
        self.caption = caption
        self.filename = filename

    def create_message(self) -> Dict[str, Any]:
        return json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.number,
            "type": "document",
            "document": {
                "link": self.url,
                "caption": self.caption,
                "filename": self.filename,
            },
        })


class ReplyReactionMessage(WhatsAppMessage):
    def __init__(self, number: str, message_id: str, emoji: str):
        self.number = number
        self.message_id = message_id
        self.emoji = emoji

    def create_message(self) -> Dict[str, Any]:
        return json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.number,
            "type": "reaction",
            "reaction": {"message_id": self.message_id, "emoji": self.emoji},
        })


class ReplyTextMessage(WhatsAppMessage):
    def __init__(self, number: str, message_id: str, text: str):
        self.number = number
        self.message_id = message_id
        self.text = text

    def create_message(self) -> Dict[str, Any]:
        return json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.number,
            "context": {"message_id": self.message_id},
            "type": "text",
            "text": {"body": self.text},
        })
