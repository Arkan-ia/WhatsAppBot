from marshmallow import Schema, fields, post_load, ValidationError


class ChatWithCostumerCommand(Schema):
    message = fields.Str(required=True)
    sender = fields.Str(required=True)
    recipient = fields.Str(required=True)
    timestamp = fields.Int(required=True)

    @post_load
    def make_command(self, data, **kwargs):
        return data


class MetaWebhookSchema(Schema):
    object = fields.Str(required=True)
    entry = fields.List(fields.Dict(), required=True)

    @post_load
    def process_entry(self, data, **kwargs):
        print("In process----------->")
        try:
            first_entry = data["entry"][0]
            messaging_event = first_entry["messaging"][0]

            command = ChatWithCostumerCommand().load(
                {
                    "message": messaging_event["message"]["text"],
                    "sender": messaging_event["sender"]["id"],
                    "recipient": messaging_event["recipient"]["id"],
                    "timestamp": messaging_event["timestamp"],
                }
            )

            return command
        except (KeyError, IndexError) as e:
            raise ValidationError(f"Formato inválido del webhook: {e}")
