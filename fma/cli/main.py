import logging
import click


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Running in debug mode")
    else:
        logging.basicConfig(level=logging.CRITICAL + 1)
