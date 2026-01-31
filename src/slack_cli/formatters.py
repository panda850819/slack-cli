"""Rich-based output formatters for Slack CLI."""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .client import Channel, Conversation, Message

console = Console()


def format_timestamp(ts: str) -> str:
    """Format Slack timestamp to human-readable format."""
    try:
        dt = datetime.fromtimestamp(float(ts))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return ts


def print_messages(messages: list[Message], title: str = "Messages") -> None:
    """Print messages in a formatted table."""
    if not messages:
        console.print("[dim]No messages found.[/dim]")
        return

    table = Table(title=title, show_lines=True)
    table.add_column("Time", style="dim", width=16)
    table.add_column("Channel", style="cyan", width=15)
    table.add_column("User", style="green", width=15)
    table.add_column("Message", style="white")

    for msg in messages:
        table.add_row(
            format_timestamp(msg.timestamp),
            f"#{msg.channel_name}" if msg.channel_name else msg.channel,
            msg.username,
            Text(msg.text[:200] + "..." if len(msg.text) > 200 else msg.text),
        )

    console.print(table)


def print_search_results(messages: list[Message], query: str) -> None:
    """Print search results with highlighting."""
    if not messages:
        console.print(f"[dim]No results found for '[yellow]{query}[/yellow]'[/dim]")
        return

    console.print(f"\n[bold]Search results for '[yellow]{query}[/yellow]':[/bold]\n")

    for msg in messages:
        header = Text()
        header.append(f"#{msg.channel_name}", style="cyan")
        header.append(" | ", style="dim")
        header.append(msg.username, style="green")
        header.append(" | ", style="dim")
        header.append(format_timestamp(msg.timestamp), style="dim")

        text = msg.text
        if msg.permalink:
            text += f"\n[dim]Link: {msg.permalink}[/dim]"

        console.print(Panel(text, title=str(header), border_style="blue"))


def print_channels(channels: list[Channel]) -> None:
    """Print channels in a formatted table."""
    if not channels:
        console.print("[dim]No channels found.[/dim]")
        return

    table = Table(title="Channels")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="yellow", width=10)
    table.add_column("Members", style="green", justify="right", width=8)
    table.add_column("Topic", style="white")

    for ch in channels:
        channel_type = "Private" if ch.is_private else "Public"
        if ch.is_archived:
            channel_type += " 📦"

        members = str(ch.member_count) if ch.member_count is not None else "-"
        topic = ch.topic[:50] + "..." if len(ch.topic) > 50 else ch.topic

        table.add_row(
            f"#{ch.name}",
            channel_type,
            members,
            topic or "[dim]No topic[/dim]",
        )

    console.print(table)


def print_channel_info(channel: Channel) -> None:
    """Print detailed channel information."""
    info = Text()
    info.append(f"Name: ", style="bold")
    info.append(f"#{channel.name}\n", style="cyan")

    info.append(f"ID: ", style="bold")
    info.append(f"{channel.id}\n", style="dim")

    info.append(f"Type: ", style="bold")
    channel_type = "Private" if channel.is_private else "Public"
    info.append(f"{channel_type}\n", style="yellow")

    if channel.member_count is not None:
        info.append(f"Members: ", style="bold")
        info.append(f"{channel.member_count}\n", style="green")

    if channel.is_archived:
        info.append(f"Status: ", style="bold")
        info.append("Archived 📦\n", style="red")

    if channel.topic:
        info.append(f"\nTopic: ", style="bold")
        info.append(f"{channel.topic}\n")

    if channel.purpose:
        info.append(f"\nPurpose: ", style="bold")
        info.append(f"{channel.purpose}\n")

    console.print(Panel(info, title="Channel Info", border_style="cyan"))


def print_conversations(conversations: list[Conversation]) -> None:
    """Print DM conversations in a formatted table."""
    if not conversations:
        console.print("[dim]No conversations found.[/dim]")
        return

    table = Table(title="Direct Messages")
    table.add_column("User", style="green")
    table.add_column("Username", style="cyan")
    table.add_column("ID", style="dim")

    for conv in conversations:
        table.add_row(
            conv.user_display_name or conv.user_name,
            f"@{conv.user_name}",
            conv.user_id,
        )

    console.print(table)


def print_dm_history(messages: list[Message], user_name: str) -> None:
    """Print DM history with a user."""
    if not messages:
        console.print(f"[dim]No messages with {user_name}.[/dim]")
        return

    console.print(f"\n[bold]Conversation with [green]{user_name}[/green]:[/bold]\n")

    for msg in reversed(messages):
        time_str = format_timestamp(msg.timestamp)
        console.print(f"[dim]{time_str}[/dim] [green]{msg.username}[/green]:")
        console.print(f"  {msg.text}\n")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]Error:[/red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_sent_message(channel: str, timestamp: str, thread_ts: str | None = None) -> None:
    """Print confirmation of a sent message."""
    time_str = format_timestamp(timestamp)
    if thread_ts:
        console.print(f"[green]✓[/green] Reply sent to thread in [cyan]#{channel}[/cyan] at {time_str}")
    else:
        console.print(f"[green]✓[/green] Message sent to [cyan]#{channel}[/cyan] at {time_str}")
