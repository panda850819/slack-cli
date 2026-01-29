"""Search command for Slack CLI."""

from typing import Annotated

import typer

from ..client import SlackClient
from ..formatters import print_error, print_search_results


def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    channel: str | None = typer.Option(
        None,
        "--channel",
        "-c",
        help="Limit search to a specific channel (name or ID)",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Maximum number of results",
    ),
) -> None:
    """Search messages in the workspace."""
    try:
        client = SlackClient()
        messages = client.search_messages(query, channel=channel, limit=limit)
        print_search_results(messages, query)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)
