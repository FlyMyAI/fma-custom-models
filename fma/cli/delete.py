import logging

import click
import httpx

from fma.auth import check_authorization
from fma._constants import URLS
from fma._config_manager import config_manager
from fma._utils import httpx_error_handling, load_model_data
from .main import cli

logger = logging.getLogger(__name__)


@cli.command()
def delete():
    """Command to delete current model deployment."""
    check_authorization()

    model_data = load_model_data()
    headers = {
        "Authorization": f"Bearer {config_manager.get('auth_token')}",
        "Content-Type": "application/json",
    }
    with httpx_error_handling():
        response = httpx.delete(URLS["delete"] % model_data.model_name, headers=headers)
        response.raise_for_status()
    click.echo("Model deleted successfully! ✅")
