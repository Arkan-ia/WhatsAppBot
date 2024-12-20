import logging
from typing import Dict, Any

def send_whatsapp_notification(bot, number: str, message: Dict[str, Any]) -> None:
    """
    Sends a WhatsApp notification to the specified number.
    
    Args:
        bot: WhatsApp bot instance
        number (str): The recipient's phone number
        message (Dict[str, Any]): The message content to send
        
    Returns:
        None
    """
    try:
        bot.send_whatsapp_message(message)
        print(f"Notification sent to {number}")
    except Exception as e:
        logging.error(f"Failed to send notification to {number}: {str(e)}")




def send_mail(to: str, subject: str, body: str) -> None:
    """
    Envía un correo electrónico usando SMTP.
    
    Args:
        to (str): Dirección de correo del destinatario
        subject (str): Asunto del correo
        body (str): Contenido del correo
        
    Returns:
        None
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Configura estos valores según tu servidor SMTP
    SMTP_SERVER = "smtp.tuservidor.com"
    SMTP_PORT = 587
    SMTP_USER = "tu_correo@dominio.com"
    SMTP_PASSWORD = "tu_contraseña"
    
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to
        msg['Subject'] = subject
        
        # Agregar cuerpo del mensaje
        msg.attach(MIMEText(body, 'plain'))
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # Enviar correo
        server.send_message(msg)
        server.quit()
        
    except Exception as e:
        raise Exception(f"Error al enviar correo: {str(e)}")