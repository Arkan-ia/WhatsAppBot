# chatbot.py
import os
from src.conversation_manager import ConversationManager
from src.whatsappbot import WhatsAppBot
from utils.pdf_manager import PDFManager

bot = WhatsAppBot(
    api_url=os.getenv('WHATSAPP_URL'),
    token=os.getenv('WHATSAPP_TOKEN')
)

# Initialize the PDFManager and ConversationManager
pdf_manager = PDFManager("https://cdn.glitch.global/1e6c16f0-cf67-4f9c-b4af-433d3336cf2f/Menu.pdf?v=1729527777028")
conversation_manager = ConversationManager(bot, pdf_manager)

# In your main loop or webhook handler:
def handle_incoming_message(message):
    conversation_manager.handle_incoming_message(message)
