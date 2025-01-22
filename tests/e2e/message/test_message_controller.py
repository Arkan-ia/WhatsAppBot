import io
from unittest.mock import MagicMock

import pandas as pd
from ward import test, fixture, using
from main import app


from src.domain.message.port.message_repository import MessageRepository
from src.domain.message.service.send_single import SendSingleMesageService
from src.infrastructure.message.adapter.message_adapter import (
    MessageRepositoryMock,
)
from tests.e2e.e2e_fixtures import client

common_tags = ["e2e", "message", "controller"]


@fixture
def mock_body():
    return {
        "from_id": "Business 123456789012",
        "to": "123",
        "message": "Hello world!",
        "token": "Bearer token123456789",
    }


@fixture
def mock_massive_body():
    return {
        "from_id": "Business 123456789012",
        "token": "Bearer token123456789",
        "language_code": "es",
        "message": "Hello world!",
        "template": "template123456789012",
        "parameters": """
        [
            {
                "type": "image",
                "image": {
                    "link": "https://firebasestorage.googleapis.com/v0/b/arcania-c4669.appspot.com/o/ganeexcel1.jpg?alt=media&token=8c3e0644-13b7-49fd-9f66-4c7b303a149e"
                }
            }
        ]
        """,
    }


@test(
    "It should send a single message attaching POST /message",
    tags=common_tags + ["/message"],
)
@using(client=client, mock_body=mock_body)
def _(client, mock_body):
    # Mocks
    MessageRepositoryMock.send_single_message.return_value = {
        "status": "success",
        "message": f"Message sent to {mock_body['to']} from {mock_body['from_id']}",
    }

    # Act
    response = client.post("/message", json=mock_body)

    # Assert
    assert response.status_code == 200
    assert "success" in response.text
    assert "Message sent to 123 from Business 123456789012" in response.text


@test(
    "It should fail sending a single message attaching POST /message",
    tags=common_tags + ["/message"],
)
@using(client=client, mock_body=mock_body)
def _(client, mock_body):
    # Mocks
    MessageRepositoryMock.send_single_message.return_value = {
        "status": "error",
        "message": f"Error sending message to {mock_body['to']} from {mock_body['from_id']}",
    }

    # Act
    response = client.post("/message", json=mock_body)

    # Assert
    assert response.status_code == 200
    assert "error" in response.text
    assert "Error sending message to 123 from Business 123456789012" in response.text


@test(
    "It should fail because file is required in POST /message/massive",
    tags=common_tags + ["/message/massive"],
)
@using(client=client)
def _(client):
    # Act
    response = client.post("/message/massive")

    # Assert
    assert response.status_code == 400
    assert "error" in response.text
    assert "File is required" in response.text


@test(
    "It should fail because parameters are mal formed in POST /message/massive",
    tags=common_tags + ["/message/massive"],
)
@using(client=client)
def _(client):
    # Arrange
    file_content = b"Some Excel data here"
    excel_file = io.BytesIO(file_content)
    excel_file.name = "test.xlsx"
    form = {
        "token": "Bearer token123456789",
        "message": "Hello world!",
        "from_id": "Business 123456789012",
        "parameters": "malformed",
        "template": "test",
        "language_code": "es",
        "file": (excel_file, "test.xlsx"),
    }

    # Act
    response = client.post(
        "/message/massive", content_type="multipart/form-data", data=form
    )

    # Assert
    assert response.status_code == 400
    assert "error" in response.text
    assert "Invalid JSON format for 'parameters'" in response.text


@test(
    "It should send a massive message from template attaching POST /message/massive",
    tags=common_tags + ["/message/massive"],
)
@using(client=client, mock_massive_body=mock_massive_body)
def _(client, mock_massive_body):
    # Arrange
    data = {"userid": [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)

    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    form = mock_massive_body.copy()
    form["file"] = (excel_file, "test.xlsx")

    expected_details = [
        {
            "message": f"Error sending message to 1 from Business 123456789012",
            "status": "error",
        },
        {
            "message": f"Message sent to 2 from Business 123456789012",
            "status": "success",
        },
        {
            "message": f"Message sent to 3 from Business 123456789012",
            "status": "success",
        },
        {
            "message": f"Message sent to 4 from Business 123456789012",
            "status": "success",
        },
        {
            "message": f"Message sent to 5 from Business 123456789012",
            "status": "success",
        },
    ]

    # Mocks
    MessageRepositoryMock.get_template_data.return_value = "template data"
    MessageRepositoryMock.send_massive_message.return_value = {
        "status": "ok",
        "message": "Mensajes enviados con éxito a 5 usuarios, 0 errores",
        "details": [
            {
                "message": f"Error sending message to 1 from {form['from_id']}",
                "status": "error",
            },
            {
                "message": f"Message sent to 2 from {form['from_id']}",
                "status": "success",
            },
            {
                "message": f"Message sent to 3 from {form['from_id']}",
                "status": "success",
            },
            {
                "message": f"Message sent to 4 from {form['from_id']}",
                "status": "success",
            },
            {
                "message": f"Message sent to 5 from {form['from_id']}",
                "status": "success",
            },
        ],
    }

    # Act
    response = client.post(
        "/message/massive", content_type="multipart/form-data", data=form
    )

    # Assert
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert (
        response.json["message"]
        == "Mensajes enviados con éxito a 5 usuarios, 0 errores"
    )
    assert response.json["details"] == expected_details


@test(
    "It should send a massive message attaching POST /message/massive",
    tags=common_tags + ["/message/massive"],
)
@using(client=client, mock_massive_body=mock_massive_body)
def _(client, mock_massive_body):
    # Arrange
    data = {"userid": [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    expected_details = [
        {
            "message": f"Error sending message to 1 from Business 123456789012",
            "status": "error",
        },
        {
            "message": f"Message sent to 2 from Business 123456789012",
            "status": "success",
        },
        {
            "message": f"Message sent to 3 from Business 123456789012",
            "status": "success",
        },
        {
            "message": f"Message sent to 4 from Business 123456789012",
            "status": "success",
        },
        {
            "message": f"Message sent to 5 from Business 123456789012",
            "status": "success",
        },
    ]

    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    form = mock_massive_body.copy()
    form["file"] = (excel_file, "test.xlsx")
    form["template"] = ""

    # Mocks
    MessageRepositoryMock.get_template_data.return_value = "template data"
    MessageRepositoryMock.send_massive_message.return_value = {
        "status": "ok",
        "message": "Mensajes enviados con éxito a 5 usuarios, 0 errores",
        "details": [
            {
                "message": f"Error sending message to 1 from {form['from_id']}",
                "status": "error",
            },
            {
                "message": f"Message sent to 2 from {form['from_id']}",
                "status": "success",
            },
            {
                "message": f"Message sent to 3 from {form['from_id']}",
                "status": "success",
            },
            {
                "message": f"Message sent to 4 from {form['from_id']}",
                "status": "success",
            },
            {
                "message": f"Message sent to 5 from {form['from_id']}",
                "status": "success",
            },
        ],
    }

    # Act
    response = client.post(
        "/message/massive", content_type="multipart/form-data", data=form
    )

    # Assert
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert (
        response.json["message"]
        == "Mensajes enviados con éxito a 5 usuarios, 0 errores"
    )
    assert response.json["details"] == expected_details
