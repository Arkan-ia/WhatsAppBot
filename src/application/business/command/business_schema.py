from marshmallow import Schema, post_load, fields


class BusinessSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)

    @post_load
    def make_sender(self, data, **kwargs):
        return data
