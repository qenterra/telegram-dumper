"""Command-line entry point for telegram-dumper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import keyring
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt

from telegram_dumper import __version__
from telegram_dumper.accounts import AccountRegistry
from telegram_dumper.source import parse_source
from telegram_dumper.settings import ALLOWED_MEDIA_TYPES, UserSettings, normalize_extensions
from telegram_dumper.telegram_client import (
    MEDIA_CATEGORIES,
    SESSION_KEYRING_SERVICE,
    run_add_account,
    run_download,
)


console = Console()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="telegram-dumper",
        description="Download Telegram media that your signed-in account is permitted to save.",
        epilog=(
            "Examples:\n"
            "  telegram-dumper\n"
            "  telegram-dumper accounts\n"
            "  telegram-dumper download 'https://t.me/example/123' "
            "--types photo,video --extensions .png,.zip --out ./downloads\n\n"
            "Protected chats and messages are always skipped."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    download = commands.add_parser(
        "download",
        help="Download media from a Telegram link",
        description="Download media you are permitted to save. Invite links are not joined.",
    )
    download.add_argument(
        "source",
        help="Public channel/chat link or a message link from a chat your account can access",
    )
    download.add_argument(
        "--types",
        help=(
            f"Comma-separated categories ({', '.join(MEDIA_CATEGORIES)}) or all; "
            "defaults to saved settings"
        ),
    )
    download.add_argument(
        "--out",
        type=Path,
        help="Save folder; defaults to the saved setting or ./telegram-downloads",
    )
    download.add_argument(
        "--extensions",
        help=(
            "Comma-separated file extensions such as .png,.jpg,.zip, or all; "
            "defaults to saved settings"
        ),
    )
    download.add_argument("--limit", type=int, help="Maximum number of messages to scan")
    download.add_argument(
        "--account",
        metavar="ID",
        help="Use this saved account ID for this download instead of the active account",
    )

    accounts = commands.add_parser(
        "accounts", help="View, add, switch, or remove Telegram accounts"
    )
    account_actions = accounts.add_subparsers(dest="accounts_action")
    account_actions.add_parser("add", help="Sign in and save another Telegram account")
    select = account_actions.add_parser("select", help="Choose the active account")
    select.add_argument("account_id", help="Numeric account ID shown by `telegram-dumper accounts`")
    remove = account_actions.add_parser("remove", help="Remove an account and its saved session")
    remove.add_argument("account_id", help="Numeric account ID shown by `telegram-dumper accounts`")
    return parser


def _guided_download() -> int:
    settings = UserSettings().load()
    console.print(
        Panel(
            "[bold cyan]telegram-dumper[/bold cyan]\n"
            "[dim]A guided Telegram media downloader[/dim]\n\n"
            "[bold]1[/bold] Paste a public Telegram channel or message link.\n"
            "[bold]2[/bold] Choose file categories, or keep [cyan]all[/cyan].\n"
            "[bold]3[/bold] Choose a local save folder. Files keep their original format.\n\n"
            "Use [cyan]telegram-dumper accounts[/cyan] to add or switch accounts.\n"
            "Protected chats and messages are always skipped; invite links are not joined.",
            title="[bold cyan]Telegram Dumper[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )
    console.print(
        "[dim]Examples: https://t.me/channelname or https://t.me/channelname/123[/dim]"
    )
    source_text = Prompt.ask("[bold]Telegram link[/bold]")
    console.print(
        f"[dim]Available: {', '.join(MEDIA_CATEGORIES)}. Use commas to combine categories.[/dim]"
    )
    selected = Prompt.ask(
        "[bold]File types[/bold]", default=",".join(settings["media_types"])
    )
    console.print(
        "[dim]Optional extensions: .png, .jpg, .zip, .pdf. Use all to keep every format.[/dim]"
    )
    extensions = Prompt.ask(
        "[bold]Extensions[/bold]", default=",".join(settings["extensions"])
    )
    out = Path(
        Prompt.ask("[bold]Save folder[/bold]", default=settings["output_directory"])
    )
    active = AccountRegistry().active()
    account_id = str(active["account_id"]) if active else None
    if active:
        console.print(f"[dim]Active account: {active['display_name']}[/dim]")
    return _download(source_text, selected, out, None, account_id, extensions)


def _clear_menu() -> None:
    if console.is_terminal:
        console.clear()


def _menu(title: str, rows: list[tuple[str, str]]) -> None:
    table = Table(title=title, header_style="bold cyan", border_style="dim")
    table.add_column("Key", style="bold cyan", justify="center", width=5)
    table.add_column("Action")
    for key, action in rows:
        table.add_row(key, action)
    console.print(table)


def _pause() -> None:
    Prompt.ask("[dim]Press Enter to return[/dim]", default="")


def _accounts_menu() -> None:
    registry = AccountRegistry()
    while True:
        _clear_menu()
        _show_accounts()
        _menu(
            "Accounts",
            [
                ("1", "Add account"),
                ("2", "Switch active account"),
                ("3", "Remove account"),
                ("0", "Back"),
            ],
        )
        choice = Prompt.ask("[bold]Choose[/bold]", choices=["1", "2", "3", "0"])
        if choice == "0":
            return
        if choice == "1":
            _manage_accounts("add", None)
            _pause()
        elif choice == "2":
            accounts = registry.all()
            if not accounts:
                console.print("[yellow]No saved accounts yet.[/yellow]")
                _pause()
                continue
            account_id = Prompt.ask("Account ID (0 to go back)")
            if account_id == "0":
                continue
            _manage_accounts("select", account_id)
            _pause()
        else:
            accounts = registry.all()
            if not accounts:
                console.print("[yellow]No saved accounts yet.[/yellow]")
                _pause()
                continue
            account_id = Prompt.ask("Account ID to remove (0 to go back)")
            if account_id == "0":
                continue
            _manage_accounts("remove", account_id)
            _pause()


def _settings_menu() -> None:
    settings = UserSettings()
    while True:
        _clear_menu()
        current = settings.load()
        console.print(
            Panel(
                f"[bold]Default file types[/bold]  {', '.join(current['media_types'])}\n"
                f"[bold]Extensions[/bold]  {', '.join(current['extensions'])}\n"
                f"[bold]Download folder[/bold]  {current['output_directory']}",
                title="[bold cyan]Settings[/bold cyan]",
                border_style="cyan",
                expand=False,
            )
        )
        _menu(
            "Preferences",
            [
                ("1", "Change file categories"),
                ("2", "Change extensions"),
                ("3", "Change download folder"),
                ("0", "Back"),
            ],
        )
        choice = Prompt.ask("[bold]Choose[/bold]", choices=["1", "2", "3", "0"])
        if choice == "0":
            return
        if choice == "1":
            console.print(
                f"[dim]Available: {', '.join(sorted(ALLOWED_MEDIA_TYPES))}. "
                "Choose all, or combine categories with commas.[/dim]"
            )
            value = Prompt.ask("Default file types", default=",".join(current["media_types"]))
            try:
                updated = settings.update(media_types=value.split(","))
            except ValueError as exc:
                console.print(f"[bold red]Error:[/bold red] {exc}")
                _pause()
            else:
                console.print(
                    f"[green]Default types saved: {', '.join(updated['media_types'])}[/green]"
                )
                _pause()
        elif choice == "2":
            console.print(
                "[dim]Type extensions with dots, separated by commas: .png,.jpg,.zip. "
                "Use all for every format.[/dim]"
            )
            value = Prompt.ask("Default extensions", default=",".join(current["extensions"]))
            try:
                updated = settings.update(extensions=value.split(","))
            except ValueError as exc:
                console.print(f"[bold red]Error:[/bold red] {exc}")
                _pause()
            else:
                console.print(
                    f"[green]Default extensions saved: {', '.join(updated['extensions'])}[/green]"
                )
                _pause()
        else:
            value = Prompt.ask("Default download folder", default=current["output_directory"])
            try:
                settings.update(output_directory=value)
            except ValueError as exc:
                console.print(f"[bold red]Error:[/bold red] {exc}")
                _pause()
            else:
                console.print("[green]Download folder saved.[/green]")
                _pause()


def _home_menu() -> int:
    if not sys.stdin.isatty():
        _parser().print_help()
        return 2
    while True:
        _clear_menu()
        active = AccountRegistry().active()
        account_label = active["display_name"] if active else "Not signed in"
        console.print(
            Panel(
                "[bold cyan]Telegram Dumper[/bold cyan]\n"
                "Download media from chats available to your Telegram account.\n"
                f"[dim]Active account: {account_label}[/dim]",
                border_style="cyan",
                expand=False,
            )
        )
        _menu(
            "Main menu",
            [
                ("1", "Download from a link"),
                ("2", "Telegram accounts"),
                ("3", "Settings"),
                ("0", "Exit"),
            ],
        )
        choice = Prompt.ask("[bold]Choose[/bold]", choices=["1", "2", "3", "0"])
        if choice == "0":
            console.print("[dim]Bye.[/dim]")
            return 0
        if choice == "1":
            _clear_menu()
            _guided_download()
            _pause()
        elif choice == "2":
            _accounts_menu()
        else:
            _settings_menu()


def _download(
    source_text: str,
    selected: str | None,
    output: Path | None,
    limit: int | None,
    account_id: str | None = None,
    extensions_text: str | None = None,
) -> int:
    try:
        defaults = UserSettings().load()
        selected = selected or ",".join(defaults["media_types"])
        output = output or Path(defaults["output_directory"])
        extensions_text = extensions_text or ",".join(defaults["extensions"])
        source = parse_source(source_text)
        categories = {item.strip().lower() for item in selected.split(",") if item.strip()}
        valid = set(MEDIA_CATEGORIES) | {"all"}
        invalid = categories - valid
        if invalid or not categories:
            raise ValueError(f"Unknown media type(s): {', '.join(sorted(invalid)) or selected}")
        extensions = normalize_extensions(extensions_text.split(","))
        if limit is not None and limit <= 0:
            raise ValueError("--limit must be greater than zero.")
        downloaded, skipped = run_download(
            source, output.expanduser(), categories, limit, account_id, extensions
        )
    except (RuntimeError, ValueError, OSError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 2
    except Exception as exc:
        console.print(
            f"[bold red]Telegram operation failed:[/bold red] {type(exc).__name__}. "
            "Check the account's chat access and network connection, then retry."
        )
        return 1
    console.print(f"Finished: {downloaded} downloaded, {skipped} skipped.")
    return 0


def _show_accounts() -> int:
    registry = AccountRegistry()
    accounts = registry.all()
    if not accounts:
        console.print(
            Panel(
                "No saved accounts yet. Start a download to sign in, or run "
                "[cyan]telegram-dumper accounts add[/cyan] to add one now.",
                title="[bold cyan]Telegram accounts[/bold cyan]",
                border_style="cyan",
                expand=False,
            )
        )
        return 0
    active = registry.active()
    table = Table(title="Saved Telegram accounts", header_style="bold cyan", border_style="dim")
    table.add_column("Active", justify="center")
    table.add_column("Account")
    table.add_column("Username")
    table.add_column("ID", style="dim")
    for account in accounts:
        is_active = active is not None and account["account_id"] == active["account_id"]
        table.add_row(
            "●" if is_active else "",
            account["display_name"],
            f"@{account['username']}" if account.get("username") else "—",
            account["account_id"],
        )
    console.print(table)
    console.print(
        "[dim]Switch: telegram-dumper accounts select ID  ·  Add: telegram-dumper accounts add  ·  "
        "Remove: telegram-dumper accounts remove ID[/dim]"
    )
    return 0


def _manage_accounts(action: str | None, account_id: str | None) -> int:
    registry = AccountRegistry()
    try:
        if action == "add":
            new_id = run_add_account()
            console.print(f"[green]Account {new_id} added and selected as active.[/green]")
        elif action == "select":
            account = registry.select(account_id or "")
            console.print(f"[green]Active account: {account['display_name']}.[/green]")
        elif action == "remove":
            account = registry.get(account_id or "")
            if account is None:
                raise ValueError(f"No saved Telegram account has ID {account_id}.")
            if not Confirm.ask(
                f"Remove {account['display_name']} and its saved session?", default=False
            ):
                console.print("No changes made.")
                return 0
            session_key = f"{account['api_id']}:{account['account_id']}"
            has_session = keyring.get_password(SESSION_KEYRING_SERVICE, session_key) is not None
            active = registry.active()
            was_active = active is not None and active["account_id"] == account["account_id"]
            registry.remove(account_id or "")
            if has_session:
                try:
                    keyring.delete_password(SESSION_KEYRING_SERVICE, session_key)
                except Exception:
                    try:
                        registry.upsert(account, activate=was_active)
                    except Exception:
                        console.print(
                            "[bold red]Session deletion failed and the account list could not be restored. "
                            "The saved session was not confirmed removed.[/bold red]"
                        )
                        return 2
                    console.print(
                        "[bold red]Could not remove the session; the account list was restored.[/bold red]"
                    )
                    return 2
            console.print(
                "[green]Account and saved session removed. API credentials remain in the system keyring.[/green]"
            )
        return _show_accounts()
    except (RuntimeError, ValueError, OSError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 2
    except Exception as exc:
        console.print(
            f"[bold red]Account operation failed:[/bold red] {type(exc).__name__}. "
            "Check the system credential store and retry."
        )
        return 1


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.command is None:
        raise SystemExit(_home_menu())
    if args.command == "download":
        raise SystemExit(
            _download(args.source, args.types, args.out, args.limit, args.account, args.extensions)
        )
    if args.command == "accounts":
        raise SystemExit(_manage_accounts(args.accounts_action, getattr(args, "account_id", None)))
    parser.print_help()
    raise SystemExit(2)


if __name__ == "__main__":
    main()
