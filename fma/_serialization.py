import inspect
import textwrap
from typing import Any, Callable, Dict, Self, Tuple

from pydantic import BaseModel

T = Dict[str, Any]


def _serialize_initialize_method(method: Callable[[Any], Any]) -> str:
    return _get_method_body(method)


def _serialize_predict_method(
    method: Callable[[Any, BaseModel], BaseModel],
) -> Tuple[str, T, T]:
    method_body = _get_method_body(method)
    annotations = method.__annotations__
    if (input_class := annotations.get("input")) is None:
        raise ValueError(
            "You should specify `input` argument for predict method with type annotation"
        )
    if (output_class := annotations.get("return")) is None:
        raise ValueError("You should specify return type annotation for predict method")
    inputs = input_class.model_json_schema()
    outputs = output_class.model_json_schema()
    return method_body, inputs, outputs


def _get_method_body(method: Callable) -> str:
    lines, _ = inspect.getsourcelines(method)
    body = "".join(lines[1:])
    return textwrap.dedent(body)
