import logging
from contextlib import contextmanager
from traceback import format_exc

import httpx
from pyaml import yaml

from fma._dto import DeployedModelData

logger = logging.getLogger(__name__)


@contextmanager
def httpx_error_handling():
    """Context manager to handle httpx errors"""
    try:
        yield
    except httpx.HTTPStatusError as errh:
        status = errh.response.status_code
        logger.exception(errh.response.text)
        if status == 403:
            print("ERROR: You need to authenticate first! Run `fma login`")
        elif status == 400:
            print("ERROR: Some of the provided arguments were incorrect!")
        elif status == 404:
            print("ERROR: Unavailable")
        else:
            print("ERROR: We encountered an HTTP error: ", errh)
        exit(1)
    except httpx.ConnectError as errc:
        print("ERROR: We are having trouble connecting:", errc)
        exit(1)
    except httpx.ReadTimeout as errt:
        print("ERROR: The request to the model has timed out:", errt)
        exit(1)
    except httpx.RequestError as err:
        print("ERROR: Something went wrong, please try again:", err)
        exit(1)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def load_model_data() -> DeployedModelData:
    try:
        with open("metadata.yaml") as file:
            model_data = DeployedModelData(**yaml.safe_load(file))
    except Exception as e:
        print("Error in loading metadata.yaml")
        logger.exception(f"{format_exc()}")
        exit(1)
    return model_data
