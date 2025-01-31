from marshmallow import Schema, fields, post_load


class OriginSchema(Schema):
    type = fields.Str(required=True)


class ConversationSchema(Schema):
    id = fields.Str(required=True)
    expiration_timestamp = fields.Str(required=False)
    origin = fields.Nested(OriginSchema, required=True)


class PricingSchema(Schema):
    billable = fields.Bool(required=True)
    pricing_model = fields.Str(required=True)
    category = fields.Str(required=True)


class StatusSchema(Schema):
    id = fields.Str(required=True)
    status = fields.Str(required=True)
    timestamp = fields.Str(required=True)
    recipient_id = fields.Str(required=True)
    conversation = fields.Nested(ConversationSchema, required=False)
    pricing = fields.Nested(PricingSchema, required=False)


class StatusUpdateSchema(Schema):
    display_phone_number = fields.Str(required=True)
    phone_number_id = fields.Str(required=True)
    statuses = fields.List(fields.Nested(StatusSchema), required=True)
    field = fields.Str(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return data


class MetadataSchema(Schema):
    display_phone_number = fields.Str(required=True)
    phone_number_id = fields.Str(required=True)


class ValueSchema(Schema):
    messaging_product = fields.Str(required=True)
    metadata = fields.Nested(MetadataSchema, required=True)
    statuses = fields.List(fields.Nested(StatusSchema), required=True)


class ChangeSchema(Schema):
    field = fields.Str(required=True)
    value = fields.Nested(ValueSchema, required=True)


class EntrySchema(Schema):
    id = fields.Str(required=True)
    changes = fields.List(fields.Nested(ChangeSchema), required=True)


class StatusChangeSchema(Schema):
    object = fields.Str(required=True)
    entry = fields.List(fields.Nested(EntrySchema), required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return data


class SuccessfullSentMessageSchema(Schema):
    object = fields.Str(required=True)
    entry = fields.List(fields.Nested(EntrySchema), required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return data
