import os

import click

from .main import cli
from fma._constants import MODEL_TEMPLATE


@cli.command()
@click.argument("model_name")
def init(model_name):
    """Command for model project intialization.
    
Expected folder structure:
<model_name>/
    | model.py
metadata.yaml"""
    print(f"{model_name =}")
    _validated_model_name(model_name)
    os.mkdir(model_name)

    model_file_path = f"{model_name}/model.py"

    with open(model_file_path, "w") as file:
        file.write(MODEL_TEMPLATE)

    open("metadata.yaml", "w").close()


def _validated_model_name(model_name: str):
    pass
