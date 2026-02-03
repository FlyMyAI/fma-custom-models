import importlib.util
import json
import logging
import os
from pprint import pprint

import httpx

from fma.auth import check_authorization
from fma._config_manager import config_manager
from fma._constants import URLS
from fma._messages import DEPLOY_ERROR_MESSAGE
from fma._utils import httpx_error_handling
from .main import cli


@cli.command()
def deploy():
    """Deploy command."""

    check_authorization()
    module, model_name = _import_module()
    model_class = module.Model
    model_payload = model_class._serialize(model_name)
    headers = {
        "Authorization": f"Bearer {config_manager.get('auth_token')}",
        "Content-Type": "application/json",
    }
    logging.info(f"{model_payload = }")
    with httpx_error_handling():
        response = httpx.post(URLS["deploy"], json=model_payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
    print(f"Successfully deployed model {model_name}! ✅")


def _import_module():
    contents = os.listdir(".")
    folders = [item for item in contents if os.path.isdir(item)]
    if len(folders) == 0:
        print(DEPLOY_ERROR_MESSAGE)
        exit(1)
    model_name = folders[0]
    module_path = f"{model_name}/model.py"
    if not os.path.exists(module_path):
        print(DEPLOY_ERROR_MESSAGE)
        exit(1)
    spec = importlib.util.spec_from_file_location("model", module_path)
    if spec is None:
        print(DEPLOY_ERROR_MESSAGE)
        exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module, model_name
