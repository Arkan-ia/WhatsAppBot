class ChatMessage:
    def __init__(self, role, content, **kwargs):
        self.role = role
        self.content = content

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }
