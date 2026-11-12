"""Fail-closed checks for Telegram content protection flags."""

from __future__ import annotations


def has_content_protection(chat: object, message: object, private_chat: object | None = None) -> bool:
    """Return true when Telegram marks the chat or message as protected.

    Telegram documents that chat-wide protected content must be treated as non-downloadable
    even when individual message objects do not carry ``noforwards``.
    """
    if bool(getattr(message, "noforwards", False)):
        return True
    if bool(getattr(chat, "noforwards", False)):
        return True
    if private_chat is not None and (
        bool(getattr(private_chat, "noforwards_my_enabled", False))
        or bool(getattr(private_chat, "noforwards_peer_enabled", False))
    ):
        return True
    return False
