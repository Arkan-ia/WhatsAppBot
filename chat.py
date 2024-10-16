# chat.py
import json
import time
import logging
import re
import unicodedata
import openai
import sett 
from whatsappbot.whatsappbot import WhatsAppBot


bot = WhatsAppBot(
    api_url=sett.whatsapp_url,
    token=sett.whatsapp_token)


def handle_incoming_message(message):
    """
    Handles an incoming WhatsApp message and manages the chatbot logic, using GPT-4 to generate natural responses.
    """
    # Extract message details
    text = bot.get_whatsapp_message(message)
    number = message['from']
    message_id = message.get('id', None)
    name = message.get('profile', {}).get('name', '')
    logging.info(f"User message from {number}: {text}")
    
    list_messages = []

    # Mark message as read
    mark_read = bot.mark_read_message(message_id)
    list_messages.append(mark_read)
    time.sleep(1)

    # Check if user information is missing
    if bot.is_user_info_missing(number):
        current_state = bot.get_conversation_state(number)
        user_data = bot.get_user_data(number)

        if current_state is None or current_state == 'solicitar_nombre':
            if not user_data.get('nombre'):
                # Generate LLM response to ask for the name
                response = bot.generate_llm_response(text, 'solicitar_nombre', user_data)
                bot.update_conversation_state(number, 'esperando_nombre')
                data = bot.text_message(number, response)
                list_messages.append(data)
            else:
                bot.update_conversation_state(number, 'esperando_direccion')

        elif current_state == 'esperando_nombre':
            # Validate if the input is a name
            is_name = bot.validate_input_with_gpt(text, 'nombre')
            if is_name:
                # Save the provided name and ask for the address
                bot.save_user_data(number, name=text)
                user_data['nombre'] = text  # Update local user data
                response = bot.generate_llm_response(text, 'esperando_nombre', user_data)
                bot.update_conversation_state(number, 'esperando_direccion')
                data = bot.text_message(number, response)
                list_messages.append(data)
            else:
                # Ask for the name again
                error_message = "Disculpa, necesito saber tu nombre para continuar. ¿Podrías decírmelo, por favor?"
                data = bot.text_message(number, error_message)
                list_messages.append(data)

        elif current_state == 'esperando_direccion':
            # Validate if the input is an address
            is_address = bot.validate_input_with_gpt(text, 'direccion')
            if is_address:
                # Save the provided address and ask for the email
                bot.save_user_data(number, address=text)
                user_data['direccion'] = text  # Update local user data
                response = bot.generate_llm_response(text, 'esperando_direccion', user_data)
                bot.update_conversation_state(number, 'esperando_correo')
                data = bot.text_message(number, response)
                list_messages.append(data)
            else:
                # Ask for the address again
                error_message = "Gracias por tu respuesta, pero parece que esa no es una dirección válida. Por favor, proporciona tu dirección para continuar."
                data = bot.text_message(number, error_message)
                list_messages.append(data)

        elif current_state == 'esperando_correo':
            # Validate email
            if is_valid_email(text):
                # Save the provided email and finish the info gathering
                bot.save_user_data(number, email=text)
                user_data['email'] = text  # Update local user data
                response = bot.generate_llm_response(text, 'esperando_correo', user_data)
                bot.update_conversation_state(number, None)  # Reset conversation state
                data = bot.text_message(number, response)
                list_messages.append(data)
            else:
                # Ask for a valid email again
                error_message = "Parece que el correo electrónico que proporcionaste no es válido. Por favor, ingresa un correo electrónico válido."
                data = bot.text_message(number, error_message)
                list_messages.append(data)
    else:
        # If no information is missing, proceed with usual logic, always using GPT-4 for responses
        if bot.is_requesting_pdf(text):
            # Send message and PDF
            pdf_url = sett.document_url  # Ensure this is set in your sett module
            caption = 'Aquí está nuestro menú en PDF. ¡Disfruta!'
            filename = 'Menu.pdf'
            response_text = "¡Claro! Te envío nuestro menú a continuación."
            data_text = bot.text_message(number, response_text)
            document = bot.document_message(number, pdf_url, caption, filename)
            list_messages.append(data_text)
            list_messages.append(document)
        else:
            # Generate response using GPT-4 for any other message
            user_data = bot.get_user_data(number)
            response_text = bot.generate_llm_response(text, None, user_data)
            data = bot.text_message(number, response_text)
            list_messages.append(data)

    # Send all messages in list_messages
    for item in list_messages:
        bot.send_whatsapp_message(item)
        logging.info("Message sent.")
