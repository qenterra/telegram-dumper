"""Command-line entry point for telegram-dumper."""

from __future__ import annotations

import argparse
from pathlib import Path

import keyring
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt

from telegram_dumper import __version__
from telegram_dumper.accounts import AccountRegistry
from telegram_dumper.source import parse_source
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
            "--types photo,video --out ./downloads\n\n"
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
        default="all",
        help=f"Comma-separated categories ({', '.join(MEDIA_CATEGORIES)}) or all; original formats are kept",
    )
    download.add_argument(
        "--out",
        type=Path,
        default=Path("telegram-downloads"),
        help="Save folder (default: ./telegram-downloads); existing files are not overwritten",
    )
    download.add_argument("--limit", type=int, help="Maximum number of messages to scan")
    download.add_argument(
        "--account",
        metavar="ID",
        help="Use this saved account ID for this download instead of the active account",
    )

    accounts = commands.add_parser("accounts", help="View, add, switch, or remove Telegram accounts")
    account_actions = accounts.add_subparsers(dest="accounts_action")
    account_actions.add_parser("add", help="Sign in and save another Telegram account")
    select = account_actions.add_parser("select", help="Choose the active account")
    select.add_argument("account_id", help="Numeric account ID shown by `telegram-dumper accounts`")
    remove = account_actions.add_parser("remove", help="Remove an account and its saved session")
    remove.add_argument("account_id", help="Numeric account ID shown by `telegram-dumper accounts`")
    return parser


def _guided_download() -> int:
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
    selected = Prompt.ask("[bold]File types[/bold]", default="all")
    out = Path(Prompt.ask("[bold]Save folder[/bold]", default="telegram-downloads"))
    active = AccountRegistry().active()
    account_id = str(active["account_id"]) if active else None
    if active:
        console.print(f"[dim]Active account: {active['display_name']}[/dim]")
    return _download(source_text, selected, out, None, account_id)


def _download(
    source_text: str,
    selected: str,
    output: Path,
    limit: int | None,
    account_id: str | None = None,
) -> int:
    try:
        source = parse_source(source_text)
        categories = {item.strip().lower() for item in selected.split(",") if item.strip()}
        valid = set(MEDIA_CATEGORIES) | {"all"}
        invalid = categories - valid
        if invalid or not categories:
            raise ValueError(f"Unknown media type(s): {', '.join(sorted(invalid)) or selected}")
        if limit is not None and limit <= 0:
            raise ValueError("--limit must be greater than zero.")
        downloaded, skipped = run_download(
            source, output.expanduser(), categories, limit, account_id
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
        raise SystemExit(_guided_download())
    if args.command == "download":
        raise SystemExit(_download(args.source, args.types, args.out, args.limit, args.account))
    if args.command == "accounts":
        raise SystemExit(_manage_accounts(args.accounts_action, getattr(args, "account_id", None)))
    parser.print_help()
    raise SystemExit(2)


if __name__ == "__main__":
    main()
