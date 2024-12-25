import json
import logging
from typing import Any, Dict

from src.db.firebase import update_contact_data
from src.utils.notifications import send_email_notification




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
        
        send_email_notification(to=to, message=body, subject=subject)
        logging.info(f"Correo de notificación de pago enviado a {to}")
    except Exception as e:
        logging.error(f"Error al enviar correo de notificación de pago a {to}: {str(e)}")
        


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
            "description": """Almacena información importante del usuario en la base de datos. 
IMPORTANTE: Debes llamar a esta función cada vez que el usuario mencione:
- Su nombre o cómo se llama
- Cualquier condición médica o enfermedad que padezca
- Su correo electrónico

Ejemplos de cuando llamar la función:
- "Me llamo Juan"
- "Soy María"
- "Tengo diabetes"
- "Padezco de hipertensión"
- "Mi correo es usuario@email.com"
- "Pueden contactarme en juan@gmail.com"

No es necesario que el usuario proporcione todos los campos; envía solo los campos que el usuario haya mencionado.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "El nombre del usuario. Extráelo cuando el usuario lo mencione de cualquier forma (ej: 'me llamo X', 'soy X', etc.)",
                    },
                    "email": {
                        "type": "string",
                        "description": "El correo electrónico del usuario. Extráelo cuando el usuario lo mencione.",
                    },
                    "sickness": {
                        "type": "string",
                        "description": "Cualquier enfermedad o condición médica que el usuario mencione padecer (ej: diabetes, hipertensión, etc.)",
                    },
                    "cedula": {
                        "type": "string",
                        "description": "La cédula del usuario. Extráelo cuando el usuario lo mencione.",
                    },
                    "direction": {
                        "type": "string",
                        "description": "La dirección del usuario. Extráelo cuando el usuario lo mencione.",
                    },
                },
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

