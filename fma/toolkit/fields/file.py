from typing import Any

from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue

from .base import FMABaseField


class File(FMABaseField):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, _handler: Any
    ) -> JsonSchemaValue:
        return {"type": "file"}
