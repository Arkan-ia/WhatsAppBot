import json
import logging
from typing import Any, Dict

from src.db.firebase import update_contact_data
from src.utils.notifications import send_mail




def get_notify_payment_mail_tool():
    return {
        "type": "function",
        "function": {
            "name": "notify_payment_mail",
            "description": "Envía un correo electrónico al dueño del negocio notificando que un cliente quiere pagar.",
        },
    }


def notify_payment_mail(to: str):
    """
    Envía un correo electrónico notificando un pago.
    
    Args:
        to (str): Dirección de correo del destinatario
        
    Returns:
        None
    """
    try:
        subject = "Nueva solicitud de pago"
        body = "Un cliente ha solicitado realizar un pago. Por favor revisa tu panel de control."
        
        send_mail(to=to, subject=subject, body=body)
        logging.info(f"Correo de notificación de pago enviado a {to}")
    except Exception as e:
        logging.error(f"Error al enviar correo de notificación de pago a {to}: {str(e)}")
        raise


def get_notify_payment_push_notification_tool():
    return {
        "type": "function",
        "function": {
            "name": "notify_payment_push_notification",
            "description": "Envía una notificación push al dueño del negocio notificando que un cliente quiere pagar.",
        },
    }


def get_send_menu_pdf_tool():
    return {
        "type": "function",
        "function": {
            "name": "send_menu_pdf",
            "description": "Envía el menú del negocio en formato PDF",
            "parameters": {
                "type": "object",
                "properties": {
                    "menu_path": {
                        "type": "string",
                        "description": "La ruta del menú en formato PDF",
                    },
                },
                "required": ["menu_path"],
            },
        },
    }



# def send_menu_pdf(menu_path: str, number: str):
#     """
#     Envía el menú del negocio en formato PDF.
    
#     Args:
#         menu_path (str): La ruta del menú en formato PDF
        
#     Returns:
#         None
#     """
#     try:
#         caption = "Aquí está nuestro menú en PDF."
#         filename = "Menu.pdf"
#         document = whatsapp_api_handler.document_message(
#                 number, menu_path, caption, filename
#         )
#         whatsapp_api_handler.send_whatsapp_message(document)
#         print(f"Menu PDF sent to {number}")
#     except Exception as e:
#             logging.exception("Error al enviar el PDF del menú: %s", str(e))
#             raise
def get_store_user_data_tool(data: Dict[str, Any] = None):
    return {
        "type": "function",
        "function": {
            "name": "store_user_data",
            "description": "Almacena información importante del usuario como su nombre, correo electrónico o condiciones médicas en la base de datos. Cada que el usuario envia alguno de estos datos, llama a esta función para almacenarlos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the user, e.g. John Doe",
                    },
                    "email": {
                        "type": "string",
                        "description": "The email address of the user, e.g. john@doe.com",
                    },
                    "sickness": {
                        "type": "string",
                        "description": "The sickness of the user, e.g. cold, flu, etc.",
                    },
                },
                #"required": ["name", "email", "id", "sickness"],
            },
        },
    }


def store_user_data(ws_id: str, phone_number: str, data: Dict[str, Any]):
    """
    Almacena los datos del usuario en la base de datos.
    
    Args:
        kwargs (dict): Los datos del usuario
        
    Returns:
        None
    """
    update_contact_data(ws_id, phone_number, data)

