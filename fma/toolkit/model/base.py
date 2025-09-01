from typing import Any, Dict

from fma._serialization import _serialize_predict_method, _serialize_initialize_method


class FMABaseModel:
    @classmethod
    def _serialize(cls, model_name: str) -> Dict[str, Any]:
        requirements = getattr(cls, "requirements", [])
        initialize_method = getattr(cls, "initialize", None)
        predict_method = getattr(cls, "predict", None)

        if initialize_method is None or predict_method is None:
            raise NotImplementedError(
                "FMA models must implement both " "`initialize` and `predict` methods"
            )

        representation = {"model_name": model_name, "requirements": requirements}
        representation["initialize_method"] = _serialize_initialize_method(
            initialize_method
        )
        method_body, inputs, outputs = _serialize_predict_method(predict_method)
        representation["predict_method"] = method_body
        representation["inputs"] = inputs
        representation["outputs"] = outputs
        return representation
