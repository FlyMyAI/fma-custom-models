import os

import click

from fma._config_manager import config_manager


def get_agent_client():
    """Create an AgentClient from config or environment."""
    from flymyai import AgentClient

    api_key = os.environ.get("FLYMYAI_API_KEY") or config_manager.get("api_key")
    if not api_key:
        click.echo(
            "Error: API key not set.\n"
            "  Run:  fma api-key set <your-key>\n"
            "  Or:   export FLYMYAI_API_KEY=fly-...",
            err=True,
        )
        raise SystemExit(1)

    base_url = (
        os.environ.get("FLYMYAI_DSN")
        or config_manager.get("agent_base_url")
        or "https://api.flymy.ai"
    )
    return AgentClient(api_key=api_key, base_url=base_url)
