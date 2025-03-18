import json
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel


class ToolCall(BaseModel):
    name: str
    idd: str
    arguments: Optional[Dict[str, Any]]
    typee: Optional[Literal["tool", "function"]]

    def __str__(self):
        return f"ToolCall(name={self.name}, id={self.idd}, arguments={self.arguments})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function": {
                "name": self.name,
                "arguments": json.dumps(self.arguments),
            },
            "id": self.idd,
            "type": self.typee,
        }
