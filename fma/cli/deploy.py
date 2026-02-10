import importlib.util
import logging
import os

import click
import httpx
from pyaml import yaml

from fma.auth import check_authorization
from fma._config_manager import config_manager
from fma._constants import URLS
from fma._dto import DeployedModelData
from fma._messages import DEPLOY_ERROR_MESSAGE
from fma._utils import httpx_error_handling
from .main import cli

logger = logging.getLogger(__name__)


@cli.command()
def deploy():
    """Deploy command."""

    check_authorization()
    module, model_name = _import_module()
    model_class = module.Model
    model_payload = model_class.serialize(model_name)
    headers = {
        "Authorization": f"Bearer {config_manager.get('auth_token')}",
        "Content-Type": "application/json",
    }
    logging.info(f"{model_payload = }")
    with httpx_error_handling():
        response = httpx.post(URLS["deploy"], json=model_payload, headers=headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            if str(response.status_code).startswith("4"):
                click.echo(response.json())
                click.echo("Try running `fma update`")
            raise
        model_data = DeployedModelData(**response.json())

    with open("metadata.yaml", "w+") as file:
        yaml.dump(model_data.model_dump(), file)

    click.echo(
        f"Successfully deployed model {model_name}! ✅\n"
        "Model data was saved in metadata.yaml file"
    )


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
