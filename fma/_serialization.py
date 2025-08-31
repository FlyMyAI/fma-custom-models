import inspect
import textwrap
from typing import Any, Callable, Dict, Self, Tuple, Type

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
    inputs = _parse_io_models(input_class)
    outputs = _parse_io_models(output_class)
    return method_body, inputs, outputs


def _parse_io_models(io_class: BaseModel) -> Dict[str, Any]:
    io_fields_raw = io_class.model_json_schema().get("properties", [])
    io_fields = []
    for io_field_name, io_field_details in io_fields_raw.items():
        field = {"title": io_field_name}
        if type_ := io_field_details.get("type"):
            field["type"] = type_
        elif types := io_field_details.get("anyOf"):
            for type_dict in types:
                if type_ := type_dict.get("type"):
                    field["type"] = type_
                    break
            field["optional"] = True
        io_fields.append(field)
    return {"fields": io_fields}


def _get_method_body(method: Callable) -> str:
    lines, _ = inspect.getsourcelines(method)
    body = "".join(lines[1:])
    return textwrap.dedent(body)
