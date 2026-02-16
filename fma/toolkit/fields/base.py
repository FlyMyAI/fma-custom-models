from typing import Any

from pydantic_core import core_schema


class FMABaseField:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.str_schema()
