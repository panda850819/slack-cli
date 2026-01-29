"""Channel commands for Slack CLI."""

from typing import Annotated

import typer

from ..client import SlackClient
from ..formatters import (
    print_channel_info,
    print_channels,
    print_error,
    print_messages,
)

app = typer.Typer(help="Channel operations.")


@app.command("list")
def list_channels(
    include_private: bool = typer.Option(
        False,
        "--private",
        "-p",
        help="Include private channels",
    ),
    include_archived: bool = typer.Option(
        False,
        "--archived",
        "-a",
        help="Include archived channels",
    ),
    channel_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by type: public, private",
    ),
) -> None:
    """List channels in the workspace."""
    try:
        client = SlackClient()

        if channel_type == "private":
            include_private = True

        channels = client.list_channels(
            include_private=include_private,
            include_archived=include_archived,
        )

        if channel_type == "private":
            channels = [ch for ch in channels if ch.is_private]
        elif channel_type == "public":
            channels = [ch for ch in channels if not ch.is_private]

        print_channels(channels)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("history")
def channel_history(
    channel: Annotated[str, typer.Argument(help="Channel name or ID")],
    limit: int = typer.Option(
        50,
        "--limit",
        "-n",
        help="Number of messages to retrieve",
    ),
) -> None:
    """Get message history from a channel."""
    try:
        client = SlackClient()
        messages = client.get_channel_history(channel, limit=limit)
        channel_info = client.get_channel_info(channel)
        print_messages(messages, title=f"History of #{channel_info.name}")
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("info")
def channel_info(
    channel: Annotated[str, typer.Argument(help="Channel name or ID")],
) -> None:
    """Get detailed information about a channel."""
    try:
        client = SlackClient()
        info = client.get_channel_info(channel)
        print_channel_info(info)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)
