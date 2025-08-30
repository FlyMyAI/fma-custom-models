import importlib.util
import os
from pprint import pprint

from fma._messages import DEPLOY_ERROR_MESSAGE
from .main import cli


@cli.command()
def deploy():
    """Deploy command."""

    print("Calling deploy!")
    contents = os.listdir(".")
    folders = [item for item in contents if os.path.isdir(item)]
    if len(folders) == 0:
        print(DEPLOY_ERROR_MESSAGE)
        exit()
    model_name = folders[0]
    print(f"{model_name = }")
    spec = importlib.util.spec_from_file_location("model", f"{model_name}/model.py")
    if spec is None:
        print(DEPLOY_ERROR_MESSAGE)
        exit()
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model_class = module.Model
    print("Import successfull!!!\n")
    pprint(model_class._serialize())
