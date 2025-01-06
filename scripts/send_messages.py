import pandas as pd

from src.common.utils.whatsapp_utils import send_whatsapp_message
from src.common.whatsapp.models.models import TemplateMessage, TextMessage
from src.data.sources.firebase.message_impl import MessageFirebaseRepository
from src.views.whatsapp_webhook import get_template_message_content


def send(file_path, from_id, token, message, template=None, language_code="es"):
    if not file_path:
        return {"error": "El archivo está vacío"}, 400
    file_data = pd.read_excel(file_path, header=None)
    users = file_data[0].tolist()

    for number in users:
        print(f"Enviando mensaje a {number}")
        if template:
            ws_message = TemplateMessage(
                to_number=str(number), template=template, code=language_code
            )
            db_content = get_template_message_content(ws_message.template)
        else:
            ws_message = TextMessage(number=str(number), text=message)
            db_content = ws_message.text

        send_whatsapp_message(from_whatsapp_id=from_id, token=token, message=ws_message)
        MessageFirebaseRepository().create_chat_message(from_id, str(number), db_content)


send(
    "scripts/jorge.xlsx",
    "450361964838178",
    "EAAPyxlZB9ZAvgBOzoE2FgHy1r4hewz7NAzeSRQhj52AWky2B5TgWucSFAL38NCoQy1OWUZCJHH3uqlwe3wMZC2PnZAqRit4EQ8TDYiidkyxcFot2y95W7XlLbNVE1dBNfRLs8exqUoTzk7cpGaC8QX6dkUFmQ5MILUG9v6KMTiFrZBltbCkJPI8iZCPZAqAx6aZBpBwZDZD",
    "que hizo rey",
    "ano_nuevo",
)
