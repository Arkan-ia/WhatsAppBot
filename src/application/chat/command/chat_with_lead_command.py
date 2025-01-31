from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from src.application.business.command.business_schema import BusinessSchema
from src.application.lead.command.lead_schema import LeadSchema
from src.domain.message.model.message import Sender, WhatsAppSender


class ChatWithLeadCommand(Schema):
    message_content = fields.Str(required=True)
    message_type = fields.Str(required=True)
    business = fields.Nested(lambda: BusinessSchema(), required=True, unknown=EXCLUDE)
    lead = fields.Nested(lambda: LeadSchema(), required=True, unknown=EXCLUDE)
    message_id = fields.Str(required=False)

    @post_load
    def make_command(self, data, **kwargs):
        return data


class MetaWebhookSchema(Schema):
    object = fields.Str(required=True)
    entry = fields.List(fields.Dict(), required=True)

    @post_load
    def process_entry(self, data, **kwargs):
        try:
            first_entry = data["entry"][0]
            changes_event = first_entry["changes"][0]
            value = changes_event["value"]
            message = value["messages"][0]
            contact = value["contacts"][0]

            business_data = {
                "id": value["metadata"]["phone_number_id"],
                "name": value["metadata"]["display_phone_number"],
            }

            lead_data = {
                "phone_number": contact["wa_id"],
                "name": contact["profile"]["name"],
            }

            command = ChatWithLeadCommand().load(
                {
                    "message_content": message["text"]["body"],
                    "message_type": message["type"],
                    "business": BusinessSchema().load(business_data),
                    "lead": LeadSchema().load(lead_data),
                    "message_id": message["id"],
                }
            )

            return command
        except (KeyError, IndexError) as e:
            raise ValidationError(f"Invalid format: {e}")
