"""Resolve supported Telegram URLs without attempting to join inaccessible chats."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import urlparse


_TELEGRAM_HOSTS = {"t.me", "telegram.me", "www.t.me", "www.telegram.me"}


@dataclass(frozen=True)
class TelegramSource:
    peer: str
    message_id: int | None = None


def parse_source(value: str) -> TelegramSource:
    """Parse a public chat link or a direct message link.

    Invite links and web preview URLs are intentionally rejected: the user must already
    have access through their Telegram account.
    """
    candidate = value.strip()
    parsed = urlparse(candidate if "://" in candidate else f"https://{candidate}")
    if parsed.scheme != "https" or parsed.hostname not in _TELEGRAM_HOSTS:
        raise ValueError("Use an https://t.me/... or https://telegram.me/... link.")

    parts = [part for part in parsed.path.split("/") if part]
    if parts and parts[0] == "s":
        parts = parts[1:]
    if parts and parts[0] == "c":
        if len(parts) not in {2, 3} or not parts[1].isdigit():
            raise ValueError("Private channel links must look like t.me/c/<channel>/<message>.")
        peer = int(f"-100{parts[1]}")
        message_id = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else None
        if len(parts) == 3 and message_id is None:
            raise ValueError("The message ID in this link must be a number.")
        return TelegramSource(str(peer), message_id)

    if not parts or parts[0].startswith(("+", "joinchat")):
        raise ValueError("Invite links are not joined automatically. Open the chat in Telegram first.")
    username = parts[0]
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", username):
        raise ValueError("The Telegram link does not contain a supported public username.")
    message_id: int | None = None
    if len(parts) >= 2:
        if not parts[1].isdigit():
            raise ValueError("The message ID in this link must be a number.")
        message_id = int(parts[1])
    return TelegramSource(username, message_id)
