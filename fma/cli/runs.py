import json

import click

from .main import cli
from ._agent_client import get_agent_client


@cli.group()
def runs():
    """Inspect and manage agent runs."""


@runs.command("list")
@click.option("--limit", default=20, type=int, help="Max results")
def list_runs(limit):
    """List recent runs."""
    client = get_agent_client()
    items = client.runs.list()[:limit]
    if not items:
        click.echo("No runs found.")
        return
    for r in items:
        status_color = {
            "completed": "green",
            "failed": "red",
            "cancelled": "yellow",
            "running": "cyan",
            "pending": "white",
        }.get(str(r.status).split(".")[-1], "white")
        click.echo(
            f"  #{r.id:<6d}  "
            f"{click.style(str(r.status).split('.')[-1], fg=status_color):<20s}  "
            f"{str(r.created_at)[:19]}"
        )


@runs.command("get")
@click.argument("run_id", type=int)
@click.option("--json-output", "as_json", is_flag=True, help="Output as JSON")
def get_run(run_id, as_json):
    """Show run details and logs."""
    client = get_agent_client()
    run = client.runs.get(run_id)
    if as_json:
        click.echo(json.dumps(run.model_dump(), indent=2, default=str))
        return
    click.echo(f"Run:     #{run.id}")
    click.echo(f"Status:  {run.status}")
    click.echo(f"Prompt:  {run.original_prompt[:100]}{'...' if len(run.original_prompt) > 100 else ''}")
    if run.error:
        click.echo(click.style(f"Error:   {run.error}", fg="red"))
    if run.logs:
        click.echo(f"\nLogs ({len(run.logs)}):")
        for log in run.logs:
            label = str(log.type).split(".")[-1]
            click.echo(f"  [{label}] {log.message}")
    if run.output:
        click.echo(click.style("\nResult:", bold=True))
        click.echo(json.dumps(run.output, indent=2, ensure_ascii=False))


@runs.command("cancel")
@click.argument("run_id", type=int)
def cancel(run_id):
    """Cancel a running execution."""
    client = get_agent_client()
    client.runs.cancel(run_id)
    click.echo(f"Run #{run_id} cancelled.")


@runs.command("wait")
@click.argument("run_id", type=int)
@click.option("--timeout", default=300, type=int, help="Timeout in seconds (default: 300)")
@click.option("--poll", default=2.0, type=float, help="Poll interval in seconds (default: 2)")
def wait_run(run_id, timeout, poll):
    """Wait for a run to complete and print the result."""
    client = get_agent_client()
    click.echo(f"Waiting for run #{run_id}...")
    try:
        result = client.runs.wait(run_id, timeout=timeout, poll_interval=poll)
    except TimeoutError:
        click.echo(click.style(f"Timed out after {timeout}s.", fg="yellow"))
        raise SystemExit(1)
    click.echo(f"Status: {result.status}")
    if result.error:
        click.echo(click.style(f"Error: {result.error}", fg="red"))
    if result.output:
        click.echo(json.dumps(result.output, indent=2, ensure_ascii=False))


@runs.command("logs")
@click.argument("run_id", type=int)
def show_logs(run_id):
    """Show execution logs for a run."""
    client = get_agent_client()
    run = client.runs.get(run_id)
    if not run.logs:
        click.echo("No logs yet.")
        return
    for log in run.logs:
        label = str(log.type).split(".")[-1]
        ts = str(log.created_at)[11:19]
        click.echo(f"  {ts}  [{label}] {log.message}")
        if log.data and isinstance(log.data, dict):
            for k, v in log.data.items():
                click.echo(f"           {k}: {json.dumps(v, ensure_ascii=False)[:120]}")
