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