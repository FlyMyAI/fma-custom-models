import click

from fma.cli.delete import delete
from fma.cli.deploy import deploy
from .main import cli


@cli.command()
@click.pass_context
def update(ctx):
    """Command to redeploy the model."""
    delete.invoke(ctx)
    deploy.invoke(ctx)
