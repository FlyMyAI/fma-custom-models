import logging
from traceback import format_exc

import click
import httpx

from fma.auth import check_authorization
from fma._config_manager import config_manager
from fma._constants import URLS
from fma._dto import HardwareLogs
from fma._utils import httpx_error_handling, load_model_data
from .main import cli

logger = logging.getLogger(__name__)


@cli.command()
@click.option("--output-file", help="Optional username")
def logs(output_file: str | None = None):
    """Command to fetch current model start logs."""
    check_authorization()

    model_data = load_model_data()
    headers = {
        "Authorization": f"Bearer {config_manager.get('auth_token')}",
        "Content-Type": "application/json",
    }
    with httpx_error_handling():
        response = httpx.get(URLS["logs"] % model_data.model_name, headers=headers)
        response.raise_for_status()
        logs_data = HardwareLogs(**response.json())
    try:
        response = httpx.get(logs_data.link)
        response.raise_for_status()
    except httpx.HTTPStatusError:
        click.echo(
            "Logs are not available. This could happen because project started succesfully."
        )
        exit()

    logs_text = response.text
    if output_file is not None:
        with open(output_file, "w+") as file:
            file.write(logs_text)
        print(f"Logs were save into {output_file}.")
    else:
        print(f"Logs for {model_data.model_name}: \n", logs_text)
