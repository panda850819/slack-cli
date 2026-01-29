"""DM commands for Slack CLI."""

from typing import Annotated

import typer

from ..client import SlackClient
from ..formatters import print_conversations, print_dm_history, print_error

app = typer.Typer(help="Direct message operations.")


@app.command("list")
def list_dms() -> None:
    """List all DM conversations."""
    try:
        client = SlackClient()
        conversations = client.list_dm_conversations()
        print_conversations(conversations)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("history")
def dm_history(
    user: Annotated[str, typer.Argument(help="Username or user ID")],
    limit: int = typer.Option(
        50,
        "--limit",
        "-n",
        help="Number of messages to retrieve",
    ),
) -> None:
    """Get message history with a user."""
    try:
        client = SlackClient()
        messages = client.get_dm_history(user, limit=limit)

        user_name = user
        if messages:
            user_name = messages[0].channel_name.replace("DM with ", "")

        print_dm_history(messages, user_name)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)
