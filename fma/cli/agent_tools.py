import json

import click

from .main import cli
from ._agent_client import get_agent_client


@cli.group("tools")
def tools_group():
    """Browse, add, and configure MCP tools."""


@tools_group.command("available")
@click.option("--filter", "category", default=None, help="Filter by category")
def available(category):
    """Show available tools from the catalog."""
    client = get_agent_client()
    items = client.tools.available()
    if category:
        items = [t for t in items if category.lower() in [c.lower() for c in t.categories]]
    if not items:
        click.echo("No tools found.")
        return
    for t in items:
        cats = ", ".join(t.categories)
        click.echo(f"  {t.name:<25s} {t.type:<15s} {cats}")


@tools_group.command("list")
def list_tools():
    """Show your configured tools."""
    client = get_agent_client()
    items = client.tools.list()
    if not items:
        click.echo("No tools configured. Run: fma tools add <name>")
        return
    for t in items:
        status = click.style("ready", fg="green") if t.is_configured else click.style("needs config", fg="yellow")
        click.echo(f"  #{t.id:<4d} {t.mcp_tool:<25s} {status}")


@tools_group.command("add")
@click.argument("name")
def add(name):
    """Add a tool from the catalog."""
    client = get_agent_client()
    tool = client.tools.create(mcp_tool=name)
    click.echo(f"Tool added: #{tool.id} {tool.mcp_tool}")
    if not tool.is_configured:
        step = tool.next_configuration_step
        if step:
            click.echo(f"\nNeeds configuration:")
            click.echo(f"  {step.get('description', '?')}")
            click.echo(f"\nRun: fma tools configure {tool.id}")


@tools_group.command("configure")
@click.argument("tool_id", type=int)
@click.option("--response", default=None, help="JSON response for the current config step")
def configure(tool_id, response):
    """Walk through tool configuration steps."""
    client = get_agent_client()
    tool = client.tools.get(tool_id)

    if tool.is_configured:
        click.echo(f"Tool #{tool_id} ({tool.mcp_tool}) is already configured.")
        return

    step = tool.next_configuration_step
    if not step:
        click.echo("No configuration steps remaining.")
        return

    click.echo(f"Tool: {tool.mcp_tool}")
    click.echo(f"Step: {step.get('description', '?')}")
    click.echo(f"Type: {step.get('step_type', '?')}")

    if step.get("vars_from_user_schema"):
        schema = step["vars_from_user_schema"]
        props = schema.get("properties", {})
        required = schema.get("required", [])
        click.echo("\nRequired fields:")
        for name, spec in props.items():
            req = "*" if name in required else " "
            click.echo(f"  {req} {name}: {spec.get('title', spec.get('type', '?'))}")

    if response:
        data = json.loads(response)
    else:
        # Interactive: prompt for each field
        data = {}
        if step.get("vars_from_user_schema"):
            props = step["vars_from_user_schema"].get("properties", {})
            for field_name, spec in props.items():
                title = spec.get("title", field_name)
                value = click.prompt(f"  {title}")
                data[field_name] = value

    if data:
        tool = client.tools.provide_config(tool_id, user_response=data)
        if tool.is_configured:
            click.echo(click.style("\nTool configured!", fg="green"))
        else:
            next_step = tool.next_configuration_step
            if next_step:
                click.echo(f"\nNext step: {next_step.get('description', '?')}")
                click.echo(f"Run: fma tools configure {tool_id}")


@tools_group.command("call")
@click.argument("tool_id", type=int)
@click.option("--action", required=True, help="Action name")
@click.option("--args", "arguments", default="{}", help="Arguments as JSON")
def call_tool(tool_id, action, arguments):
    """Call a tool action directly."""
    client = get_agent_client()
    args = json.loads(arguments)
    result = client.tools.call(tool_id, action=action, arguments=args)
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@tools_group.command("remove")
@click.argument("tool_id", type=int)
def remove(tool_id):
    """Remove a configured tool."""
    client = get_agent_client()
    client.tools.delete(tool_id)
    click.echo(f"Tool #{tool_id} removed.")
