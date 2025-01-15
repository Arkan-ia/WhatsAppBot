from typing import Any, Dict, List

from marshmallow import Schema, fields
from pandas import ExcelFile
from pydantic import FilePath


class SendMassiveMessageCommand(Schema):
    file = fields.Raw(required=True)
    token: str = fields.Str(required=True)
    from_id: str = fields.Str(required=True)
    message: str = fields.Str(required=False)
    template: str = fields.Str(required=False)
    language_code: str = fields.Str(required=False)
    parameters: List[Dict[str, Any]] = fields.List(
        fields.Dict(keys=fields.Str(), values=fields.Raw()), required=False
    )
