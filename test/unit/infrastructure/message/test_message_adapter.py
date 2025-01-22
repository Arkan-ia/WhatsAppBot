from ward import skip, test, fixture, using
from unittest.mock import MagicMock, PropertyMock
from src.domain.message.model.message import (
    Message,
    Sender,
    TextMessage,
    WhatsAppSender,
)
from src.infrastructure.message.adapter.message_adapter import (
    MessageWhatsAppApiAdapter,
)

common_tags = ["unit", "infrastructure", "message", "adapter"]


@fixture
def common_message():
    sender: Sender = WhatsAppSender()
    sender.from_identifier = "Business 123456789012"
    sender.from_token = "Bearer token123456789"
    message: Message = TextMessage()
    message.sender = sender
    message.content = "Hello world!"
    message.to = "123456789012"
    return message


@fixture
def mock_dependencies():
    # Mock dependencies
    messaging_manager = MagicMock()
    logger = MagicMock()
    no_rel_db = MagicMock()
    return messaging_manager, logger, no_rel_db


@fixture
@using(mock_dependencies=mock_dependencies)
def message_adapter(mock_dependencies):
    messaging_manager, logger, no_rel_db = mock_dependencies
    return MessageWhatsAppApiAdapter(
        messaging_manager=messaging_manager, logger=logger, no_rel_db=no_rel_db
    )


@test("send_single_message should send a valid message successfully", tags=common_tags)
@using(message_adapter=message_adapter, common_message=common_message)
def _(message_adapter, common_message):
    # Arrange
    message: Message = common_message

    # Mocks
    message_adapter.save_message = MagicMock()
    message_adapter._MessageWhatsAppApiAdapter__validate_to = MagicMock()

    # Act
    result = message_adapter.send_single_message(message)

    # Assert
    assert result["status"] == "success"
    assert "Message sent to 123456789012" in result["message"]
    message_adapter._MessageWhatsAppApiAdapter__validate_to.assert_called_once_with(
        "123456789012"
    )
    message_adapter.save_message.assert_called_once()


@test(
    "send_single_message should return an error for invalid recipient", tags=common_tags
)
@using(message_adapter=message_adapter)
def _(message_adapter):
    # Arrange
    sender: Sender = WhatsAppSender()
    sender.from_identifier = "Business 123456789012"
    sender.from_token = "Bearer token123456789"
    message: Message = TextMessage()
    message.sender = sender
    message.content = "Hello world!"
    message.to = "123"

    # Act
    result = message_adapter.send_single_message(message)

    # Assert
    assert (
        "Error sending message to 123 from Business 123456789012" in result["message"]
    )
    assert result["status"] == "error"


@test(
    "save_message should raise an exception if business is not found", tags=common_tags
)
@using(message_adapter=message_adapter, common_message=common_message)
def _(message_adapter, common_message):
    # Arrange
    message: Message = common_message

    # Mocks
    mock_storage = MagicMock()
    mock_business_ref_collection = MagicMock()
    mock_business_ref_where = MagicMock()
    mock_business_ref_limit = MagicMock()

    mock_storage.getRawCollection.return_value = mock_business_ref_collection
    mock_business_ref_collection.where.return_value = mock_business_ref_where
    mock_business_ref_where.limit.return_value = mock_business_ref_limit

    mock_business_ref_limit.get.return_value = []

    message_adapter._MessageWhatsAppApiAdapter__storage = mock_storage

    # Act & Assert
    try:
        message_adapter.save_message(message, "assistant", "whatsapp")
        assert False, "Expected an exception to be raised"
    except Exception as e:
        assert str(e) == "Business with ref 123456789012 was not found"


@test(
    "save_message should raise an exception if contact_ref is not found",
    tags=common_tags,
)
@using(message_adapter=message_adapter, common_message=common_message)
def _(message_adapter, common_message):
    # Arrange
    message: Message = common_message

    # Mocks
    mock_storage = MagicMock()
    mock_business_ref_collection = MagicMock()
    mock_business_ref_where = MagicMock()
    mock_business_ref_limit = MagicMock()
    mock_business_ref_reference = MagicMock()

    mock_business_doc = MagicMock()
    mock_business_doc_collection = MagicMock()

    mock_storage.getRawCollection.return_value = mock_business_ref_collection
    mock_business_ref_collection.where.return_value = mock_business_ref_where
    mock_business_ref_where.limit.return_value = mock_business_ref_limit

    mock_business_ref_limit.get.return_value = [mock_business_ref_reference]
    mock_business_ref_reference.configure_mock(reference=mock_business_doc)
    mock_business_doc.collection.return_value = mock_business_doc_collection
    mock_business_doc_collection.document.return_value = None

    message_adapter._MessageWhatsAppApiAdapter__storage = mock_storage

    # Act & Assert
    try:
        message_adapter.save_message(message, "assistant", "whatsapp")
        assert False, "Expected an exception to be raised"
    except Exception as e:
        assert (
            str(e)
            == "Contact with ref 123456789012 was not found in business Business 123456789012"
        )


@test("save_message should create a new contact if not exists", tags=common_tags)
@using(message_adapter=message_adapter, common_message=common_message)
def _(message_adapter, common_message):
    # Arrange
    message: Message = common_message

    # Mocks
    mock_storage = MagicMock()
    mock_business_ref_collection = MagicMock()
    mock_business_ref_where = MagicMock()
    mock_business_ref_limit = MagicMock()
    mock_business_ref_reference = MagicMock()

    mock_business_doc = MagicMock()
    mock_business_doc_collection = MagicMock()
    mock_business_doc_document = MagicMock()
    mock_business_doc_get = MagicMock()

    mock_storage.getRawCollection.return_value = mock_business_ref_collection
    mock_business_ref_collection.where.return_value = mock_business_ref_where
    mock_business_ref_where.limit.return_value = mock_business_ref_limit

    mock_business_ref_limit.get.return_value = [mock_business_ref_reference]
    mock_business_ref_reference.configure_mock(reference=mock_business_doc)
    mock_business_doc.collection.return_value = mock_business_doc_collection
    mock_business_doc_collection.document.return_value = mock_business_doc_document
    mock_business_doc_document.get.return_value = mock_business_doc_get
    mock_business_doc_get.configure_mock(exists=False)

    message_adapter._MessageWhatsAppApiAdapter__storage = mock_storage

    # Act
    message_adapter.save_message(message, "assistant", "whatsapp")

    # Assert
    mock_business_doc_document.set.assert_called()
    mock_business_doc_document.set.assert_any_call({"ws_id": "123456789012"})
