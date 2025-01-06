def add_context_to_chatbot(system_prompt, context, user_data) -> str:
    return (
        f"{system_prompt}"
        f"Contexto relevante: {context}"
        f"Ten en cuenta los datos del usuario: {user_data}"
    )

import json
import logging
import os
from typing import Any, Dict

from openai import OpenAI
import requests
from src.common.config import MAX_TOKENS, MODEL
from src.data.sources.firebase.utils import (
    upload_audio_to_storage,
    upload_media_to_storage,
)


def get_text_from_audio(media_id: str) -> str:
    """
    Convert an audio file to text using the OpenAI API.

    Args:
        audio_url (str): The URL of the audio file.

    Returns:
        str: The extracted text from the audio.
    """

    audio_media_response = get_media_from_id(media_id)

    # Upload to firestore
    file_name = f"audios/{media_id}.ogg"
    audio_path = upload_audio_to_storage(audio_media_response, file_name)

    downloaded_audio_path = download_audio_in_local(audio_media_response.json()["url"])
    print(f"Audio descargado: {audio_path}")
    transcription = transcribe_audio(downloaded_audio_path)
    print(f"Transcripción: {transcription}")

    if os.path.exists(downloaded_audio_path):
        os.remove(downloaded_audio_path)

    return transcription


def transcribe_audio(file_path):
    """Enviar el archivo de audio a OpenAI y obtener la transcripción."""
    client = OpenAI()

    response = client.audio.transcriptions.create(
        file=open(file_path, "rb"),
        model="whisper-1",
        response_format="text",
    )
    return response


def download_audio_in_local(url: str, headers) -> str:
    """Descargar el archivo de audio."""
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    file_path = "audio.ogg"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return file_path


def get_media_from_id(id: str, headers):
    answer = requests.get(f"https://graph.facebook.com/v21.0/{id}/", headers=headers)
    if answer.status_code == 200:
        answer = answer.json()
        print("answer: ", answer)
        url = answer["url"]

        image = requests.get(url, headers=headers)

        return upload_media_to_storage(image, id)
    else:
        raise Exception(f"Error getting media: {answer.status_code}, {answer.text}")


def generate_answer(messages, tools):
    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        max_tokens=MAX_TOKENS,
        temperature=0.1,
    )

    response = response.choices[0].message
    return response