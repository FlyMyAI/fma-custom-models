import json

import click

from .main import cli
from ._agent_client import get_agent_client


@cli.group()
def agents():
    """Create, manage, and run agents."""


@agents.command("create")
@click.option("--name", required=True, help="Agent name")
@click.option("--goal", required=True, help="Agent goal / instructions")
@click.option("--tools", default=None, help="Comma-separated tool IDs (e.g. 1,3,7)")
def create(name, goal, tools):
    """Create a new agent."""
    client = get_agent_client()
    tool_ids = [int(t.strip()) for t in tools.split(",")] if tools else None
    agent = client.agents.create(name=name, goal=goal, tools=tool_ids)
    click.echo(f"Agent created: {agent.id}")
    click.echo(f"  Name:   {agent.name}")
    click.echo(f"  Status: {agent.status}")


@agents.command("list")
def list_agents():
    """List your agents."""
    client = get_agent_client()
    agents_list = client.agents.list()
    if not agents_list:
        click.echo("No agents found.")
        return
    for a in agents_list:
        click.echo(f"  {a.uuid[:8]}...  {a.name:<30s}  [{a.status}]")


@agents.command("get")
@click.argument("agent_id")
@click.option("--json-output", "as_json", is_flag=True, help="Output as JSON")
def get_agent(agent_id, as_json):
    """Show agent details."""
    client = get_agent_client()
    agent = client.agents.get(agent_id)
    if as_json:
        click.echo(json.dumps(agent.model_dump(), indent=2, default=str))
        return
    click.echo(f"ID:      {agent.uuid}")
    click.echo(f"Name:    {agent.name}")
    click.echo(f"Status:  {agent.status}")
    click.echo(f"Goal:    {agent.goal[:120]}{'...' if len(agent.goal) > 120 else ''}")
    tools = agent.available_tools
    if tools:
        click.echo(f"Tools:   {len(tools)} attached")
        for t in tools:
            if isinstance(t, dict):
                name = t.get("mcp_tool", "?")
                configured = t.get("is_configured", "?")
                click.echo(f"  - {name} (configured={configured})")
            else:
                click.echo(f"  - ID {t}")


@agents.command("update")
@click.argument("agent_id")
@click.option("--name", default=None, help="New name")
@click.option("--goal", default=None, help="New goal / instructions")
@click.option("--tools", default=None, help="New tool IDs (comma-separated)")
def update(agent_id, name, goal, tools):
    """Update an agent (PATCH)."""
    client = get_agent_client()
    kwargs = {}
    if name:
        kwargs["name"] = name
    if goal:
        kwargs["goal"] = goal
    if tools:
        kwargs["available_tools"] = [int(t.strip()) for t in tools.split(",")]
    if not kwargs:
        click.echo("Nothing to update. Pass --name, --goal, or --tools.")
        return
    agent = client.agents.update(agent_id, **kwargs)
    click.echo(f"Updated: {agent.name} [{agent.status}]")


@agents.command("delete")
@click.argument("agent_id")
def delete(agent_id):
    """Delete (archive) an agent."""
    client = get_agent_client()
    client.agents.delete(agent_id)
    click.echo("Deleted.")


@agents.command("run")
@click.argument("agent_id")
@click.option("--stream", is_flag=True, help="Stream execution events in real-time")
@click.option("--wait", "do_wait", is_flag=True, help="Wait for completion and print result")
@click.option("--timeout", default=300, type=int, help="Timeout in seconds (default: 300)")
def run_agent(agent_id, stream, do_wait, timeout):
    """Run an agent and optionally stream/wait for results."""
    client = get_agent_client()
    execution = client.runs.create(agent_id=agent_id)
    click.echo(f"Run #{execution.id} started")

    if stream:
        click.echo("")
        for event in client.runs.stream_events(execution.id, timeout=timeout):
            _print_event(event)
        click.echo("")
        result = client.runs.get(execution.id)
        _print_result(result)
    elif do_wait:
        click.echo("Waiting...")
        result = client.runs.wait(execution.id, timeout=timeout)
        _print_result(result)
    else:
        click.echo(f"Status: {execution.status}")
        click.echo(f"\nTo watch:  fma agents run {agent_id} --stream")
        click.echo(f"To wait:   fma runs wait {execution.id}")


# ── formatting helpers ───────────────────────────────────────────────────────

_EVENT_STYLES = {
    "declared_functions": ("functions", "cyan"),
    "tool_called": ("tool", "green"),
    "tool_call_exception": ("error", "red"),
    "task_cancelled": ("cancelled", "yellow"),
}


def _print_event(event):
    label, color = _EVENT_STYLES.get(
        str(event.type).split(".")[-1],
        (str(event.type).split(".")[-1], "white"),
    )
    click.echo(f"  [{click.style(label, fg=color):>18s}]  {event.message}")


def _print_result(result):
    click.echo(f"Status: {result.status}")
    if result.error:
        click.echo(click.style(f"Error: {result.error}", fg="red"))
    if result.output:
        click.echo(click.style("Result:", bold=True))
        click.echo(json.dumps(result.output, indent=2, ensure_ascii=False))
