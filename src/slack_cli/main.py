"""Slack CLI - Main entry point."""

import typer

from . import __version__
from .commands import channel, dm, search, send

app = typer.Typer(
    name="slack",
    help="A CLI tool for searching and browsing Slack workspaces.",
    no_args_is_help=True,
)

app.command(name="search")(search.search)
app.command(name="send")(send.send)
app.command(name="reply")(send.reply)
app.add_typer(channel.app, name="channel")
app.add_typer(dm.app, name="dm")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"slack-cli version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Slack CLI - Search and browse your Slack workspace from the terminal."""
    pass


if __name__ == "__main__":
    app()
