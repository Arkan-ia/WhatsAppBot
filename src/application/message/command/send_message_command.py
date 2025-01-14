from marshmallow import Schema, fields


class SendMessageCommand(Schema):
    token: str = fields.Str(required=True)
    to: str = fields.Str(required=True)
    message: str = fields.Str(required=True)
    from_id: str = fields.Str(required=True)
