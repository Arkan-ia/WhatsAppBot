from marshmallow import Schema, post_load, fields


class LeadSchema(Schema):
    name = fields.Str(required=True)
    phone_number = fields.Str(required=True)

    @post_load
    def make_sender(self, data, **kwargs):
        return data
