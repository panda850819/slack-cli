# Slack CLI

A command-line interface for searching and browsing Slack workspaces.

## Features

- **Search**: Full-text search across messages
- **Channels**: List channels, view history, get channel info
- **Direct Messages**: List DM conversations, view message history

## Installation

```bash
cd ~/site/projects/slack-cli
uv pip install -e .
```

## Configuration

Set your Slack token as an environment variable:

```bash
export SLACK_CLI_TOKEN=xoxp-your-token-here
```

Or create a `.env` file based on `.env.example`.

### Token Types

- **User Token (xoxp-)**: Full access including DM search and private channels
- **Bot Token (xoxb-)**: Limited access to channels the bot is invited to

## Usage

```bash
# Search messages
slack search "keyword"
slack search "keyword" --channel general
slack search "keyword" --limit 20

# Channels
slack channel list
slack channel list --type private
slack channel history <channel-name-or-id>
slack channel history <channel> --limit 50
slack channel info <channel-name-or-id>

# Direct Messages
slack dm list
slack dm history <user-name-or-id>
slack dm history <user> --limit 50
```

## Required Slack Scopes

For full functionality, your token needs these scopes:

- `search:read` - Search messages
- `channels:read` - List public channels
- `channels:history` - Read public channel history
- `groups:read` - List private channels
- `groups:history` - Read private channel history
- `im:read` - List direct messages
- `im:history` - Read DM history
- `users:read` - List users
