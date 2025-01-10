import json
import logging
from typing import Any, Dict
from src.common.utils.notifications import send_email_notification
from src.data.sources.firebase.contact_impl import ContactFirebaseRepository
def get_notify_payment_mail_tool():
    return {
        "type": "function",
        "function": {
            "name": "notify_payment_mail",
            "description": "Envía un correo electrónico al dueño del negocio notificando que un cliente quiere pagar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "products": {
                        "type": "string",
                        "description": "Los productos realizados por el cliente.",
                    },
                    "price": {
                        "type": "number",
                        "description": "El precio total del pedido.",
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "El número de teléfono del cliente.",
                    },
                    "name": {
                        "type": "string",
                        "description": "El nombre del cliente.",
                    },
                    "cedula": {
                        "type": "string",
                        "description": "La cédula del cliente.",
                    },
                    "address": {
                        "type": "string",
                        "description": "La dirección del cliente.",
                    },
                    "city": {
                        "type": "string",
                        "description": "La ciudad del cliente.",
                    },
                },
                "required": ["products", "price", "cedula", "address", "city"],
            },
        },
    }


def notify_payment_mail(
    to: str,
    products: str,
    price: float,
    phone_number: str = None,
    name: str = None,
    cedula: str = None,
    address: str = None,
    city: str = None,
):
    """
    Envía un correo electrónico notificando un pago.

    Args:
        to (str): Dirección de correo del destinatario
        pedido_realizado (str): El pedido realizado por el cliente
        monto_total (float): El monto total del pedido
        phone_number (str, optional): El número de teléfono del cliente.
        name (str, optional): El nombre del cliente.
        cedula (str, optional): La cédula del cliente.
        address (str, optional): La dirección del cliente.
        city (str, optional): La ciudad del cliente.

    Returns:
        None
    """
    try:
        subject = "Nueva solicitud de pago"
        body = f"Un cliente ha solicitado realizar un pago. Los detalles del cliente son:\n- Precio: {price}\n- Productos: {products}\n- Nombre: {name}\n- Número de teléfono: {phone_number}\n- Cédula: {cedula}\n- Dirección: {address}\n- Ciudad: {city}.\n Por favor revisa tu panel de control en https://arkania.flutterflow.app/chats"

        send_email_notification(to=to, message=body, subject=subject)
        send_email_notification(
            to="lozanojohan321@gmail.com", message=body, subject=subject
        )
        send_email_notification(
            to="florezanave@gmail.com", message=body, subject=subject
        )
        send_email_notification(
            to="kevinskate.kg@gmail.com", message=body, subject=subject
        )

        logging.info(f"Correo de notificación de pago enviado a {to}")
        return f"Correo de notificación de pago enviado a {to}"

    except Exception as e:
        logging.error(
            f"Error al enviar correo de notificación de pago a {to}: {str(e)}"
        )


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
                    "phone_number": {
                        "type": "string",
                        "description": "El número de teléfono del usuario, debe iniciar con el código del país sin el '+'. Por defecto es 57.",
                    },
                },
                "required": ["phone_number"],
            },
        },
    }


def store_user_data(ws_id: str, phone_number: str, data: Dict[str, Any] = None):
    """
    Almacena los datos del usuario en la base de datos.

    Args:
        kwargs (dict): Los datos del usuario

    Returns:
        None
    """
    ContactFirebaseRepository().update_contact(ws_id, phone_number, data)

    return "Usuario actualizado"
