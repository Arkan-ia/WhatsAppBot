from marshmallow import Schema, fields, post_load
from src.application.business.command.business_schema import BusinessSchema
from src.application.lead.command.lead_schema import LeadSchema
from src.domain.message.model.message import Sender, WhatsAppSender


class ContinueConversationCommand(Schema):
    lead_id = fields.Str(required=True)
    business_id = fields.Str(required=True)
    # ADD CONVERSATION?

    @post_load
    def make_command(self, data, **kwargs):
        return data
