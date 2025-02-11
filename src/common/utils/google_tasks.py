import json
from typing import Dict
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
from google.oauth2 import service_account

from src.domain.message.port.message_repository import TimeUnits


def create_task(url, time: Dict[TimeUnits, int], payload=None):
    # Ruta a tu archivo JSON de credenciales
    credentials_path = "./gcp.json"

    # Carga las credenciales
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )

    # Crear cliente con las credenciales
    client = tasks_v2.CloudTasksClient(credentials=credentials)

    parent = client.queue_path(
        "innate-tempo-448214-e5", "northamerica-northeast1", "continueConversationn"
    )

    # Configurar la solicitud HTTP
    task = {
        "http_request": {
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "url": url,
        }
    }

    if payload:
        task["http_request"]["body"] = payload.encode("utf-8")
    timedelta_kwargs = {unit.value: value for unit, value in time.items()}
    d = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        **timedelta_kwargs
    )
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(d)
    task["schedule_time"] = timestamp

    response = client.create_task(request={"parent": parent, "task": task})
    print(f"Tarea creada: {response.name}")
    return response.name  # Retorna el identificador de la tarea creada


def delete_task(task_name):
    # Ruta a tu archivo JSON de credenciales
    credentials_path = "./gcp.json"

    # Carga las credenciales
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )

    # Crear cliente con las credenciales
    client = tasks_v2.CloudTasksClient(credentials=credentials)

    # Eliminar la tarea
    client.delete_task(request={"name": task_name})
    print(f"Tarea eliminada: {task_name}")


def create_answer_later_task(to_number: str, from_id: str, token: str):
    create_task(
        "https://us-central1-innate-tempo-448214-e5.cloudfunctions.net/main/send-message",
        json.dumps(
            {
                "to_number": to_number,
                "from_id": from_id,
                "token": token,
                # Crear nuevo endpoint para esto
                "message": "Hola, aún te interesan los productos?",  # generate answer
            }
        ),
    )
