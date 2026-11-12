"""Telegram login and media transfer, with protected content skipped."""

from __future__ import annotations

import asyncio
import os
import re
import sys
import unicodedata
import webbrowser
from pathlib import Path

import keyring
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn
from rich.prompt import Confirm, Prompt
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User

from telegram_dumper.accounts import AccountRegistry, restrict_permissions
from telegram_dumper.protection import has_content_protection
from telegram_dumper.source import TelegramSource


MEDIA_CATEGORIES = ("photo", "video", "audio", "voice", "document")
CATEGORY_FOLDERS = {
    "photo": "фото",
    "video": "видео",
    "audio": "аудио",
    "voice": "аудио/голосовые-сообщения",
    "document": "файлы",
}
API_CREDENTIALS_URL = "https://my.telegram.org/apps"
API_KEYRING_SERVICE = "telegram-dumper-api"
SESSION_KEYRING_SERVICE = "telegram-dumper-session"


def _api_credentials(console: Console, preferred_api_id: str | None) -> tuple[int, str]:
    environment_api_id = os.environ.get("TELEGRAM_API_ID", "").strip()
    environment_api_hash = os.environ.get("TELEGRAM_API_HASH", "").strip()
    if environment_api_hash and not environment_api_id:
        raise RuntimeError(
            "Set TELEGRAM_API_ID together with TELEGRAM_API_HASH so the API hash is stored under the correct application ID."
        )
    if preferred_api_id and environment_api_id and environment_api_id != preferred_api_id:
        raise RuntimeError(
            "The selected account uses a different API ID. Unset TELEGRAM_API_ID or select an account registered to that API ID."
        )
    api_id_text = preferred_api_id or environment_api_id
    try:
        if not api_id_text:
            api_id_text = keyring.get_password(API_KEYRING_SERVICE, "active-api-id") or ""
        api_hash = environment_api_hash
        if api_id_text and not api_hash:
            api_hash = keyring.get_password(API_KEYRING_SERVICE, api_id_text) or ""
    except Exception as exc:
        raise RuntimeError(
            "The system credential store is unavailable; refusing to handle API credentials without it."
        ) from exc

    if not api_id_text or not api_hash:
        if not sys.stdin.isatty():
            raise RuntimeError(
                "Telegram API credentials are missing. Run `telegram-dumper` in an interactive "
                "terminal to open the setup page and save them, or set TELEGRAM_API_ID and "
                "TELEGRAM_API_HASH."
            )
        console.print(
            Panel(
                "This client uses Telegram's MTProto API to read chats available to your account.\n"
                "Get an API ID and API hash from [link=https://my.telegram.org/apps]my.telegram.org/apps[/link].\n"
                "The hash is entered privately and saved in the system credential store.",
                title="[bold cyan]Telegram API setup[/bold cyan]",
                border_style="cyan",
                expand=False,
            )
        )
        if Confirm.ask("Open the Telegram API setup page in your browser?", default=True):
            try:
                opened = webbrowser.open(API_CREDENTIALS_URL)
            except Exception:
                opened = False
            if not opened:
                console.print(
                    f"Open this link manually: [link={API_CREDENTIALS_URL}]"
                    f"{API_CREDENTIALS_URL}[/link]"
                )
        if not api_id_text:
            api_id_text = Prompt.ask("API ID").strip()

    try:
        api_id = int(api_id_text)
    except ValueError as exc:
        raise RuntimeError("The Telegram API ID must be an integer.") from exc
    if api_id <= 0:
        raise RuntimeError("The Telegram API ID must be greater than zero.")
    if not api_hash and sys.stdin.isatty():
        api_hash = Prompt.ask("API hash", password="*").strip()
    if not api_hash:
        raise RuntimeError("The Telegram API hash cannot be empty.")

    try:
        keyring.set_password(API_KEYRING_SERVICE, "active-api-id", str(api_id))
        keyring.set_password(API_KEYRING_SERVICE, str(api_id), api_hash)
    except Exception as exc:
        raise RuntimeError(
            "Could not save Telegram API credentials to the system credential store."
        ) from exc
    return api_id, api_hash


def _safe_name(name: str | None, message_id: int) -> str:
    basename = (name or f"telegram-{message_id}").replace("\\", "/").rsplit("/", 1)[-1]
    suffix = "".join(Path(basename).suffixes).casefold()
    stem = basename[: -len(suffix)] if suffix else basename
    safe_stem = _kebab_case(stem) or f"telegram-{message_id}"
    safe_suffix = re.sub(r"[^a-z0-9.+_-]", "", suffix)
    maximum_stem_length = max(1, 180 - len(safe_suffix))
    safe_stem = safe_stem[:maximum_stem_length].strip("-") or f"telegram-{message_id}"
    return f"{safe_stem}{safe_suffix}"


def _kebab_case(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    candidate = re.sub(r"[^\w]+", "-", normalized, flags=re.UNICODE).strip("-_")
    candidate = re.sub(r"[-_]+", "-", candidate)
    return candidate[:140].strip("-")


def _chat_folder_name(chat: object, fallback: str) -> str:
    label = getattr(chat, "title", None)
    if not label:
        label = " ".join(
            part
            for part in (getattr(chat, "first_name", None), getattr(chat, "last_name", None))
            if part
        )
    if not label:
        label = getattr(chat, "username", None) or fallback
    chat_id = getattr(chat, "id", None)
    safe_label = _kebab_case(str(label)) or "telegram-chat"
    if chat_id is not None:
        safe_label = f"{safe_label}-{abs(int(chat_id))}"
    return safe_label[:160].strip("-")


class TelegramDownloader:
    def __init__(self, console: Console, account_id: str | None = None) -> None:
        self.console = console
        self.registry = AccountRegistry()
        saved_account = self.registry.get(account_id) if account_id else self.registry.active()
        if account_id and saved_account is None:
            raise RuntimeError(f"No saved Telegram account has ID {account_id}.")
        self.selected_account_id = (
            str(saved_account["account_id"]) if saved_account is not None else None
        )
        preferred_api_id = str(saved_account["api_id"]) if saved_account is not None else None
        self.api_id, self.api_hash = _api_credentials(console, preferred_api_id)
        try:
            session_key = f"{self.api_id}:{self.selected_account_id}" if self.selected_account_id else ""
            session = (
                keyring.get_password(SESSION_KEYRING_SERVICE, session_key) or ""
                if session_key
                else ""
            )
        except Exception as exc:
            raise RuntimeError(
                "The system credential store is unavailable; refusing to keep an unencrypted session."
            ) from exc
        self.client = TelegramClient(StringSession(session), self.api_id, self.api_hash)
        self.has_saved_session = bool(session)

    async def run(
        self,
        source: TelegramSource,
        output_dir: Path,
        categories: set[str],
        limit: int | None = None,
        extensions: list[str] | None = None,
    ) -> tuple[int, int]:
        output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not self.has_saved_session and not sys.stdin.isatty():
            raise RuntimeError(
                "This Telegram account has no saved login session. Run the command in an interactive terminal to sign in."
            )
        if not self.has_saved_session:
            self.console.print(
                Panel(
                    "Enter the account's login code when Telegram prompts. If two-step verification "
                    "is enabled, enter that password too. The session is saved in your system "
                    "credential store for later runs.",
                    title="[bold cyan]Sign in to Telegram[/bold cyan]",
                    border_style="cyan",
                    expand=False,
                )
            )
        try:
            await self.client.start()
            me = await self.client.get_me()
            if me is None:
                raise RuntimeError("Telegram did not return the signed-in account.")
            actual_account_id = str(me.id)
            if (
                self.selected_account_id is not None
                and actual_account_id != self.selected_account_id
            ):
                raise RuntimeError(
                    "The signed-in Telegram account does not match the selected saved account. "
                    "Use `telegram-dumper accounts` to choose another account."
                )
            try:
                keyring.set_password(
                    SESSION_KEYRING_SERVICE,
                    f"{self.api_id}:{actual_account_id}",
                    self.client.session.save(),
                )
                display_name = " ".join(
                    part for part in (me.first_name, me.last_name) if part
                ) or me.username or f"Telegram account {actual_account_id}"
                self.registry.upsert(
                    {
                        "account_id": actual_account_id,
                        "api_id": str(self.api_id),
                        "display_name": display_name,
                        "username": me.username or "",
                    },
                    activate=self.selected_account_id is None,
                )
            except Exception as exc:
                raise RuntimeError(
                    "Could not save the Telegram account and session safely."
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

            chat_folder = _chat_folder_name(chat, source.peer)

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
                    if file_info is None:
                        continue
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
                    original_name = getattr(file_info, "name", None) or default_name
                    if extensions and "all" not in extensions and not any(
                        original_name.lower().endswith(extension) for extension in extensions
                    ):
                        continue
                    filename = _safe_name(original_name, message.id)
                    category_folder = CATEGORY_FOLDERS[category]
                    target_directory = output_dir / chat_folder
                    target_directory.mkdir(exist_ok=True, mode=0o700)
                    restrict_permissions(target_directory, directory=True)
                    for folder in category_folder.split("/"):
                        target_directory /= folder
                        target_directory.mkdir(exist_ok=True, mode=0o700)
                        restrict_permissions(target_directory, directory=True)
                    target = target_directory / filename
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
    account_id: str | None = None,
    extensions: list[str] | None = None,
) -> tuple[int, int]:
    console = Console()
    downloader = TelegramDownloader(console, account_id)
    return asyncio.run(downloader.run(source, output_dir, categories, limit, extensions))


async def _add_account(console: Console) -> str:
    api_id, api_hash = _api_credentials(console, None)
    client = TelegramClient(StringSession(), api_id, api_hash)
    console.print(
        Panel(
            "A new Telegram account will be added. Enter its phone number, login code, and, if "
            "enabled, two-step verification password when prompted.",
            title="[bold cyan]Add Telegram account[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )
    try:
        await client.start()
        me = await client.get_me()
        if me is None:
            raise RuntimeError("Telegram did not return the signed-in account.")
        account_id = str(me.id)
        display_name = " ".join(part for part in (me.first_name, me.last_name) if part)
        account = {
            "account_id": account_id,
            "api_id": str(api_id),
            "display_name": display_name or me.username or f"Telegram account {account_id}",
            "username": me.username or "",
        }
        keyring.set_password(
            SESSION_KEYRING_SERVICE,
            f"{api_id}:{account_id}",
            client.session.save(),
        )
        AccountRegistry().upsert(account, activate=True)
        return account_id
    finally:
        await client.disconnect()


def run_add_account() -> str:
    if not sys.stdin.isatty():
        raise RuntimeError("Adding a Telegram account requires an interactive terminal.")
    return asyncio.run(_add_account(Console()))
