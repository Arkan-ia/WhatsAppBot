from typing import Dict


class CoreError(Exception):
    def __init__(self, message: str, code: int, detailed_message: str):
        self.message = message or "An internal error has occurred"
        self.code = code
        self.detailed_message = detailed_message
        super().__init__(self.message)

    def __str__(self):
        return self.message
