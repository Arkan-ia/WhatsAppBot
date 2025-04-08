import argparse
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Define Firebase JSON path
firebase_json_path = "src/infrastructure/shared/storage/firebase.json"

# Initialize Firebase with service account
try:
    firebase_admin.get_app()
except ValueError:
    # Use the JSON service account file
    if os.path.exists(firebase_json_path):
        cred = credentials.Certificate(firebase_json_path)
        firebase_admin.initialize_app(cred)
    else:
        print(
            f"Warning: Service account file {firebase_json_path} not found. Using default credentials."
        )
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

# Get Firestore database instance
db = firestore.client()


def get_all_messages_by_phone(phone_number, business_id=None):
    """Gets all messages for a specific phone number across all businesses or a specific one."""
    try:
        # Query all messages with this phone number
        messages_query = db.collection_group("messages").where(
            "phone_number", "==", phone_number
        )

        # If business ID is specified, filter by it
        if business_id:
            messages_query = messages_query.where("ws_id", "==", business_id)

        # Get all matching messages
        messages = messages_query.get()

        print(f"Found {len(messages)} messages for {phone_number}")
        return messages

    except Exception as e:
        print(f"Error retrieving messages for {phone_number}: {str(e)}")
        raise


def delete_all_messages_by_phone(phone_number, business_id=None, confirm=True):
    """Deletes all messages for a specific phone number, optionally filtered by business ID."""
    messages = get_all_messages_by_phone(phone_number, business_id)

    if not messages:
        print("No messages found to delete.")
        return

    # Show some message samples
    print("Sample messages:")
    for i, msg in enumerate(messages[:3]):
        msg_data = msg.to_dict()
        print(
            f"{i+1}. Role: {msg_data.get('role')}, Content: {msg_data.get('content')[:50]}..."
        )

    # Confirm deletion
    if confirm:
        confirmation = input(
            f"\nAre you sure you want to delete all {len(messages)} messages? (y/n): "
        )
        if confirmation.lower() != "y":
            print("Deletion cancelled.")
            return

    # Delete messages
    deleted_count = 0
    for message in messages:
        message.reference.delete()
        deleted_count += 1

        # Show progress for large deletions
        if deleted_count % 100 == 0:
            print(f"Deleted {deleted_count}/{len(messages)} messages...")

    print(f"Successfully deleted {deleted_count} messages for {phone_number}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get and delete messages for a phone number"
    )
    parser.add_argument(
        "phone_number", help="Phone number to find messages for (format: 571234567890)"
    )
    parser.add_argument("--business_id", help="Optional business ID to filter messages")
    parser.add_argument(
        "--no-confirm", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    delete_all_messages_by_phone(
        args.phone_number, args.business_id, not args.no_confirm
    )
