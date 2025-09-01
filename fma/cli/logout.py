from fma._config_manager import config_manager
from .main import cli


@cli.command()
def logout():
    config_manager.remove("auth_token")
    config_manager.remove("profile")
    print("Successfully logged out of your account!")
