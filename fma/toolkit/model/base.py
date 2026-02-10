from typing import Any, Dict

from fma._serialization import (
    serialize_predict_method,
    serialize_initialize_method,
)


class FMABaseModel:
    NODE_METHODS = set()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        node_methods = set()

        for base in cls.__mro__:
            for attr in base.__dict__.values():
                if getattr(attr, "__fma_node_method__", False):
                    node_methods.add(attr)

        cls.NODE_METHODS = node_methods

    @classmethod
    def serialize(cls, model_name: str) -> Dict[str, Any]:
        requirements = getattr(cls, "requirements", [])
        initialize_method = getattr(cls, "initialize", None)
        predict_method = getattr(cls, "predict", None)

        if initialize_method is None or predict_method is None:
            raise NotImplementedError(
                "FMA models must implement both " "`initialize` and `predict` methods"
            )

        representation = {"model_name": model_name, "requirements": requirements}
        representation["initialize_method"] = serialize_initialize_method(
            initialize_method
        )
        method_body, inputs, outputs = serialize_predict_method(predict_method)
        representation["predict_method"] = method_body
        # TODO: add extra method serialization
        representation["inputs"] = inputs
        representation["outputs"] = outputs
        return representation
