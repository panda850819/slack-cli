"""Slack API client wrapper."""

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()


@dataclass
class Message:
    """Represents a Slack message."""

    text: str
    user: str
    username: str
    channel: str
    channel_name: str
    timestamp: str
    permalink: str | None = None


@dataclass
class Channel:
    """Represents a Slack channel."""

    id: str
    name: str
    is_private: bool
    is_archived: bool
    topic: str
    purpose: str
    member_count: int | None = None


@dataclass
class User:
    """Represents a Slack user."""

    id: str
    name: str
    real_name: str
    display_name: str
    is_bot: bool


@dataclass
class Conversation:
    """Represents a DM conversation."""

    id: str
    user_id: str
    user_name: str
    user_display_name: str


class SlackClient:
    """Wrapper for Slack Web API."""

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("SLACK_CLI_TOKEN")
        if not self.token:
            raise ValueError(
                "Slack token not found. Set SLACK_CLI_TOKEN environment variable."
            )
        self.client = WebClient(token=self.token)
        self._user_cache: dict[str, User] = {}
        self._channel_cache: dict[str, Channel] = {}

    def _get_user(self, user_id: str) -> User:
        """Get user info with caching."""
        if user_id in self._user_cache:
            return self._user_cache[user_id]

        try:
            response = self.client.users_info(user=user_id)
            user_data = response["user"]
            user = User(
                id=user_data["id"],
                name=user_data.get("name", ""),
                real_name=user_data.get("real_name", ""),
                display_name=user_data.get("profile", {}).get("display_name", ""),
                is_bot=user_data.get("is_bot", False),
            )
            self._user_cache[user_id] = user
            return user
        except SlackApiError:
            return User(
                id=user_id,
                name="unknown",
                real_name="Unknown User",
                display_name="",
                is_bot=False,
            )

    def _get_channel(self, channel_id: str) -> Channel:
        """Get channel info with caching."""
        if channel_id in self._channel_cache:
            return self._channel_cache[channel_id]

        try:
            response = self.client.conversations_info(channel=channel_id)
            channel_data = response["channel"]
            channel = Channel(
                id=channel_data["id"],
                name=channel_data.get("name", channel_id),
                is_private=channel_data.get("is_private", False),
                is_archived=channel_data.get("is_archived", False),
                topic=channel_data.get("topic", {}).get("value", ""),
                purpose=channel_data.get("purpose", {}).get("value", ""),
                member_count=channel_data.get("num_members"),
            )
            self._channel_cache[channel_id] = channel
            return channel
        except SlackApiError:
            return Channel(
                id=channel_id,
                name=channel_id,
                is_private=False,
                is_archived=False,
                topic="",
                purpose="",
            )

    def _resolve_channel_id(self, channel: str) -> str:
        """Resolve channel name to ID if needed."""
        if channel.startswith("C") or channel.startswith("G"):
            return channel

        channels = self.list_channels(include_private=True)
        for ch in channels:
            if ch.name == channel or ch.name == channel.lstrip("#"):
                return ch.id
        return channel

    def _resolve_user_id(self, user: str) -> str:
        """Resolve username to user ID if needed."""
        if user.startswith("U"):
            return user

        users = self.list_users()
        user_clean = user.lstrip("@")
        for u in users:
            if u.name == user_clean or u.display_name == user_clean:
                return u.id
        return user

    def search_messages(
        self,
        query: str,
        channel: str | None = None,
        limit: int = 20,
    ) -> list[Message]:
        """Search messages in the workspace."""
        search_query = query
        if channel:
            channel_id = self._resolve_channel_id(channel)
            channel_info = self._get_channel(channel_id)
            search_query = f"in:#{channel_info.name} {query}"

        try:
            response = self.client.search_messages(
                query=search_query,
                count=limit,
                sort="timestamp",
                sort_dir="desc",
            )
        except SlackApiError as e:
            raise RuntimeError(f"Search failed: {e.response['error']}")

        messages = []
        for match in response.get("messages", {}).get("matches", []):
            user_id = match.get("user", "")
            user = self._get_user(user_id) if user_id else None
            channel_info = match.get("channel", {})

            messages.append(
                Message(
                    text=match.get("text", ""),
                    user=user_id,
                    username=user.display_name or user.real_name if user else "Unknown",
                    channel=channel_info.get("id", ""),
                    channel_name=channel_info.get("name", ""),
                    timestamp=match.get("ts", ""),
                    permalink=match.get("permalink"),
                )
            )
        return messages

    def list_channels(
        self,
        include_private: bool = False,
        include_archived: bool = False,
    ) -> list[Channel]:
        """List channels in the workspace."""
        types = ["public_channel"]
        if include_private:
            types.append("private_channel")

        channels = []
        cursor = None

        while True:
            try:
                response = self.client.conversations_list(
                    types=",".join(types),
                    exclude_archived=not include_archived,
                    limit=200,
                    cursor=cursor,
                )
            except SlackApiError as e:
                raise RuntimeError(f"Failed to list channels: {e.response['error']}")

            for ch in response.get("channels", []):
                channel = Channel(
                    id=ch["id"],
                    name=ch.get("name", ""),
                    is_private=ch.get("is_private", False),
                    is_archived=ch.get("is_archived", False),
                    topic=ch.get("topic", {}).get("value", ""),
                    purpose=ch.get("purpose", {}).get("value", ""),
                    member_count=ch.get("num_members"),
                )
                channels.append(channel)
                self._channel_cache[channel.id] = channel

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return channels

    def get_channel_info(self, channel: str) -> Channel:
        """Get detailed info about a channel."""
        channel_id = self._resolve_channel_id(channel)
        return self._get_channel(channel_id)

    def get_channel_history(
        self,
        channel: str,
        limit: int = 50,
    ) -> list[Message]:
        """Get message history from a channel."""
        channel_id = self._resolve_channel_id(channel)
        channel_info = self._get_channel(channel_id)

        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit,
            )
        except SlackApiError as e:
            raise RuntimeError(f"Failed to get history: {e.response['error']}")

        messages = []
        for msg in response.get("messages", []):
            user_id = msg.get("user", "")
            user = self._get_user(user_id) if user_id else None

            messages.append(
                Message(
                    text=msg.get("text", ""),
                    user=user_id,
                    username=user.display_name or user.real_name if user else "Bot",
                    channel=channel_id,
                    channel_name=channel_info.name,
                    timestamp=msg.get("ts", ""),
                )
            )
        return messages

    def list_users(self) -> list[User]:
        """List all users in the workspace."""
        users = []
        cursor = None

        while True:
            try:
                response = self.client.users_list(limit=200, cursor=cursor)
            except SlackApiError as e:
                raise RuntimeError(f"Failed to list users: {e.response['error']}")

            for u in response.get("members", []):
                if u.get("deleted"):
                    continue
                user = User(
                    id=u["id"],
                    name=u.get("name", ""),
                    real_name=u.get("real_name", ""),
                    display_name=u.get("profile", {}).get("display_name", ""),
                    is_bot=u.get("is_bot", False),
                )
                users.append(user)
                self._user_cache[user.id] = user

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return users

    def list_dm_conversations(self) -> list[Conversation]:
        """List all DM conversations."""
        try:
            response = self.client.conversations_list(
                types="im",
                limit=200,
            )
        except SlackApiError as e:
            raise RuntimeError(f"Failed to list DMs: {e.response['error']}")

        conversations = []
        for conv in response.get("channels", []):
            user_id = conv.get("user", "")
            user = self._get_user(user_id) if user_id else None

            conversations.append(
                Conversation(
                    id=conv["id"],
                    user_id=user_id,
                    user_name=user.name if user else "Unknown",
                    user_display_name=(
                        user.display_name or user.real_name if user else "Unknown"
                    ),
                )
            )
        return conversations

    def get_dm_history(self, user: str, limit: int = 50) -> list[Message]:
        """Get DM history with a user."""
        user_id = self._resolve_user_id(user)

        try:
            response = self.client.conversations_open(users=[user_id])
            channel_id = response["channel"]["id"]
        except SlackApiError as e:
            raise RuntimeError(f"Failed to open DM: {e.response['error']}")

        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit,
            )
        except SlackApiError as e:
            raise RuntimeError(f"Failed to get DM history: {e.response['error']}")

        target_user = self._get_user(user_id)
        messages = []
        for msg in response.get("messages", []):
            msg_user_id = msg.get("user", "")
            msg_user = self._get_user(msg_user_id) if msg_user_id else None

            messages.append(
                Message(
                    text=msg.get("text", ""),
                    user=msg_user_id,
                    username=(
                        msg_user.display_name or msg_user.real_name
                        if msg_user
                        else "Unknown"
                    ),
                    channel=channel_id,
                    channel_name=f"DM with {target_user.display_name or target_user.real_name}",
                    timestamp=msg.get("ts", ""),
                )
            )
        return messages
