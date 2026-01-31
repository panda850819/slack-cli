"""Send commands for Slack CLI."""

import re
from typing import Annotated

import typer

from ..client import SlackClient
from ..formatters import print_error, print_sent_message

app = typer.Typer(help="Send messages to Slack.")


def parse_slack_url(url: str) -> tuple[str, str] | None:
    """Parse a Slack message URL to extract channel ID and thread timestamp.

    Args:
        url: Slack message URL like https://workspace.slack.com/archives/C0123ABC/p1769571017954789

    Returns:
        Tuple of (channel_id, thread_ts) or None if not a valid URL
    """
    pattern = r"https?://[^/]+/archives/([A-Z0-9]+)/p(\d+)"
    match = re.match(pattern, url)
    if match:
        channel_id = match.group(1)
        ts_raw = match.group(2)
        thread_ts = f"{ts_raw[:10]}.{ts_raw[10:]}"
        return channel_id, thread_ts
    return None


@app.command("send")
def send(
    channel: Annotated[str, typer.Argument(help="Channel name or ID (e.g., #general or C0123ABC)")],
    message: Annotated[str, typer.Argument(help="Message text to send")],
    thread: str | None = typer.Option(
        None,
        "--thread",
        "-t",
        help="Thread timestamp to reply to",
    ),
) -> None:
    """Send a message to a channel."""
    try:
        client = SlackClient()
        channel_id, ts = client.send_message(channel, message, thread_ts=thread)
        channel_info = client.get_channel_info(channel_id)
        print_sent_message(channel_info.name, ts, thread_ts=thread)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("reply")
def reply(
    url: Annotated[str, typer.Argument(help="Slack message URL to reply to")],
    message: Annotated[str, typer.Argument(help="Reply message text")],
) -> None:
    """Reply to a thread using a Slack message URL.

    Example:
        slack reply "https://workspace.slack.com/archives/C0123ABC/p1769571017954789" "My reply"
    """
    parsed = parse_slack_url(url)
    if not parsed:
        print_error(f"Invalid Slack URL: {url}")
        raise typer.Exit(1)

    channel_id, thread_ts = parsed

    try:
        client = SlackClient()
        result_channel, ts = client.send_message(channel_id, message, thread_ts=thread_ts)
        channel_info = client.get_channel_info(result_channel)
        print_sent_message(channel_info.name, ts, thread_ts=thread_ts)
    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)
