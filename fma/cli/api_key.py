import click

from fma._config_manager import config_manager
from .main import cli


@cli.group("api-key")
def api_key_group():
    """Manage your FlyMy.AI API key."""


@api_key_group.command("set")
@click.argument("key")
def set_key(key):
    """Save an API key for agent commands."""
    config_manager.set("api_key", key)
    masked = key[:6] + "..." + key[-4:] if len(key) > 12 else "***"
    click.echo(f"API key saved: {masked}")


@api_key_group.command("show")
def show_key():
    """Show the currently stored API key."""
    key = config_manager.get("api_key")
    if not key:
        click.echo("No API key stored. Run: fma api-key set <key>")
        return
    masked = key[:6] + "..." + key[-4:]
    click.echo(masked)
