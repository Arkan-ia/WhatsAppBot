class ChatMessage:
    def __init__(self, role, content, tool_calls=None, tool_call_id=None, function_name=None, function_response=None, **kwargs):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls
        self.tool_call_id = tool_call_id
        self.function_name = function_name
        self.function_response = function_response

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id,
            "function_name": self.function_name,
            "function_response": self.function_response
        }
