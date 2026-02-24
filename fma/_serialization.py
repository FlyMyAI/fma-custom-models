import inspect
import textwrap
import typing
from typing import Any, Callable, Dict, Tuple

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from fma.toolkit.fields.audio import Audio
from fma.toolkit.fields.image import Image
from fma.toolkit.fields.file import File

T = Dict[str, Any]


def serialize_initialize_method(method: Callable[[Any], Any]) -> str:
    return _get_method_body(method)


def serialize_predict_method(
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
    io_fields = []
    for field_name, field_info in io_class.model_fields.items():
        field = {"title": field_name}
        field["type"], field["optional"], default_value = _get_field_type_data(field_info)
        if default_value is not None:
            field["default"] = default_value
        io_fields.append(field)
    return {"fields": io_fields}


def _get_field_type_data(field_info) -> Tuple[str, bool, Any]:
    annotation = field_info.annotation
    if _is_union(annotation):
        type_ = list(annotation.__args__)[0]
        optional = True
    else:
        type_ = annotation
        optional = False

    default_value = None
    if (default := field_info.default) != PydanticUndefined:
        default_value = default

    if type_ is str:
        type_string = "string"
    elif type_ is int:
        type_string = "int"
    elif type_ is float:
        type_string = "float"
    elif type_ is bool:
        type_string = "bool"
    elif type_ is Image:
        type_string = "image"
    elif type_ is File:
        type_string = "file"
    elif type_ is Audio:
        type_string = "audio"
    else:
        raise ValueError(f"Type {type_} is not supported")
    return type_string, optional, default_value


def _is_union(x):
    return isinstance(x, typing._UnionGenericAlias)


def _get_method_body(method: Callable) -> str:
    lines, _ = inspect.getsourcelines(method)
    body = "".join(lines[1:])
    return textwrap.dedent(body)
