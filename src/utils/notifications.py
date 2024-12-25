import logging
import os
from typing import Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


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


        
def send_email_notification(to: str, message: str, subject: str) -> None:
    """
    Sends an email notification to the specified email address.
    
    Args:
        to (str): The recipient's email address
        message (str): The message content to send
        subject (str): The subject of the email
    Returns:
        None
    """
    MSG = MIMEMultipart()
    MSG['From']    = os.getenv("EMAIL_ACCOUNT")
    MSG['To']      = to
    MSG['Subject'] = subject
    MSG.attach(MIMEText(message, 'plain'))
    password     = os.getenv("EMAIL_PASSWORD")
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
    
        server.login(MSG['From'], password=password)
        
        server.sendmail(MSG['From'], MSG['To'], MSG.as_string())
        server.quit()
        # Implement email notification logic here
        print(f"Email notification sent to {to}")
        return f"Email notification sent to {to}"
    except Exception as e:
        logging.error(f"Failed to send email notification to {to}: {str(e)}")
