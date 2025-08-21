import getpass

import httpx

from fma._config_manager import config_manager
from fma._constants import URLS
from fma._utils import httpx_error_handling
from .main import cli


@cli.command()
def login():
    """Login command"""

    username = input("Username: ")
    password = getpass.getpass()

    payload = {
        "username": username,
        "password": password,
    }

    with httpx_error_handling():
        response = httpx.post(URLS["login"], json=payload)
        response.raise_for_status()
        response_data = response.json()
        config_manager.set("auth_token", response_data["access"])
        config_manager.set("profile", response_data["user"])
    print("Login successfull! ✅")
