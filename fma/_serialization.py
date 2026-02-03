import inspect
import textwrap
import typing
from typing import Any, Callable, Dict, Self, Tuple, Type, Union

from pydantic import BaseModel

from fma.toolkit.fields.image import Image
from fma.toolkit.fields.file import File

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
    for field_name, field_info in io_class.model_fields.items():
        field = {"title": field_name}
        field["type"], field["optional"] = _get_field_type_data(field_info.annotation)
        io_fields.append(field)
    # for io_field_name, io_field_details in io_fields_raw.items():
    #     field = {"title": io_field_name}
    #     if type_ := io_field_details.get("type"):
    #         field["type"] = type_
    #     elif types := io_field_details.get("anyOf"):
    #         for type_dict in types:
    #             if type_ := type_dict.get("type"):
    #                 field["type"] = type_
    #                 break
    #         field["optional"] = True
    #     io_fields.append(field)
    return {"fields": io_fields}


def _get_field_type_data(annotation) -> Tuple[str, bool]:
    if _is_union(annotation):
        type_ = list(annotation.__args__)[0]
        optional = True
    else:
        type_ = annotation
        optional = False

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
    else:
        raise ValueError(f"Type {type_} is not supported")
    return type_string, optional


def _is_union(x):
    return isinstance(x, typing._UnionGenericAlias)


def _get_method_body(method: Callable) -> str:
    lines, _ = inspect.getsourcelines(method)
    body = "".join(lines[1:])
    return textwrap.dedent(body)
