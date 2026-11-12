"""Telegram login and media transfer, with protected content skipped."""

from __future__ import annotations

import asyncio
import re

import keyring
from rich.console import Console
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User

from telegram_dumper.protection import has_content_protection
from telegram_dumper.source import TelegramSource


MEDIA_CATEGORIES = ("photo", "video", "audio", "voice", "document")


def _safe_name(name: str | None, message_id: int) -> str:
    candidate = (name or f"telegram-{message_id}").replace("/", "_").replace("\\", "_")
    candidate = re.sub(r"[^\w.() -]", "_", candidate, flags=re.UNICODE).strip(" .")
    return candidate[:180] or f"telegram-{message_id}"


class TelegramDownloader:
    def __init__(self, console: Console) -> None:
        try:
            self.api_id = int(os.environ["TELEGRAM_API_ID"])
            self.api_hash = os.environ["TELEGRAM_API_HASH"]
        except (KeyError, ValueError) as exc:
            raise RuntimeError(
                "Set TELEGRAM_API_ID and TELEGRAM_API_HASH from my.telegram.org."
            ) from exc
        if not self.api_hash:
            raise RuntimeError("TELEGRAM_API_HASH cannot be empty.")
        self.console = console
        try:
            session = keyring.get_password("telegram-dumper", str(self.api_id)) or ""
        except Exception as exc:
            raise RuntimeError(
                "The system credential store is unavailable; refusing to keep an unencrypted session."
            ) from exc
        self.client = TelegramClient(StringSession(session), self.api_id, self.api_hash)

    async def run(
        self,
        source: TelegramSource,
        output_dir: Path,
        categories: set[str],
        limit: int | None = None,
    ) -> tuple[int, int]:
        output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        await self.client.start()
        try:
            try:
                keyring.set_password(
                    "telegram-dumper", str(self.api_id), self.client.session.save()
                )
            except Exception as exc:
                raise RuntimeError(
                    "Could not save the Telegram session to the system credential store."
                ) from exc

            if source.peer.lstrip("-").isdigit():
                chat = None
                async for dialog in self.client.iter_dialogs():
                    if dialog.id == int(source.peer):
                        chat = dialog.entity
                        break
                if chat is None:
                    raise RuntimeError(
                        "This private message link is not in your Telegram dialogs. "
                        "Open the chat in Telegram and make sure this account has access."
                    )
            else:
                chat = await self.client.get_entity(source.peer)
            private_flags = None
            if isinstance(chat, User):
                try:
                    full = await self.client(GetFullUserRequest(chat))
                    private_flags = full.full_user
                except Exception as exc:
                    raise RuntimeError(
                        "Could not verify private-chat protection; refusing to download from this chat."
                    ) from exc

            messages = [source.message_id] if source.message_id is not None else None
            downloaded = skipped = 0
            async with Progress(
                TextColumn("[bold cyan]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TimeRemainingColumn(),
                console=self.console,
            ) as progress:
                task = progress.add_task("Scanning Telegram", total=None)
                async for message in self.client.iter_messages(chat, ids=messages, limit=limit):
                    progress.update(task, advance=1)
                    if not message.media:
                        continue
                    if has_content_protection(chat, message, private_flags):
                        self.console.print(
                            f"[yellow]Skipped protected message {message.id}[/yellow]"
                        )
                        skipped += 1
                        continue

                    file_info = message.file
                    mime = (getattr(file_info, "mime_type", None) or "").lower()
                    if message.photo:
                        category = "photo"
                    elif message.voice:
                        category = "voice"
                    elif message.audio:
                        category = "audio"
                    elif mime.startswith("video/") or message.video:
                        category = "video"
                    else:
                        category = "document"
                    if "all" not in categories and category not in categories:
                        continue

                    default_name = f"telegram-{message.id}{getattr(file_info, 'ext', '') or ''}"
                    filename = _safe_name(getattr(file_info, "name", None) or default_name, message.id)
                    target = output_dir / filename
                    if target.exists():
                        self.console.print(f"[dim]Skipped existing file {filename}[/dim]")
                        skipped += 1
                        continue
                    transfer = progress.add_task(filename, total=getattr(file_info, "size", None))

                    def update(current: int, total: int) -> None:
                        progress.update(transfer, completed=current, total=total)

                    try:
                        result = await self.client.download_media(
                            message, file=str(target), progress_callback=update
                        )
                        if result:
                            downloaded += 1
                            self.console.print(f"[green]Saved[/green] {target}")
                        else:
                            skipped += 1
                    finally:
                        progress.remove_task(transfer)
            return downloaded, skipped
        finally:
            await self.client.disconnect()


def run_download(
    source: TelegramSource,
    output_dir: Path,
    categories: set[str],
    limit: int | None = None,
) -> tuple[int, int]:
    console = Console()
    downloader = TelegramDownloader(console)
    return asyncio.run(downloader.run(source, output_dir, categories, limit))
