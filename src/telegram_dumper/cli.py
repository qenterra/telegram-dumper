"""Command-line entry point for telegram-dumper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import keyring
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.text import Text

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
AUTHOR = "Nikita Melnychenko · QenTerra"
ASCII_LOGO = r"""      /\
     /  \__
 ___/   ___/
\______/"""


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
        help="Save folder; defaults to the saved setting or ~/Downloads/telegram-dumper",
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


def _brand_header(section: str, account: str | None = None) -> Panel:
    details = Text()
    details.append("TELEGRAM DUMPER\n", style="bold cyan")
    details.append(f"Версия {__version__}\n", style="white")
    details.append(f"Автор: {AUTHOR}\n\n", style="dim")
    details.append(section, style="bold white")
    if account is not None:
        details.append(f"\nАккаунт: {account}", style="dim")
    content = Table.grid(padding=(0, 2))
    content.add_column(no_wrap=True)
    content.add_column()
    content.add_row(Text(ASCII_LOGO, style="bold bright_cyan"), details)
    return Panel(content, border_style="bright_blue", box=box.ROUNDED, padding=(1, 2))


def _guided_download() -> int:
    console.print(_brand_header("Загрузка из Telegram"))
    console.print(
        Panel(
            "Пришлите ссылку на публичный канал или сообщение.\n"
            "Ссылка проверяется сразу, остальные параметры спрошу только если она подходит.\n"
            "Примеры: https://t.me/channelname · https://t.me/channelname/123",
            title="[bold cyan]Начало загрузки[/bold cyan]",
            border_style="bright_blue",
            box=box.ROUNDED,
            expand=False,
        )
    )
    source_text = Prompt.ask("[bold cyan]Ссылка[/bold cyan]")
    try:
        parse_source(source_text)
    except ValueError as exc:
        console.print(
            Panel(
                f"[bold red]Неверная ссылка[/bold red]\n{exc}",
                border_style="red",
                box=box.ROUNDED,
                expand=False,
            )
        )
        return 2

    settings = UserSettings().load()
    console.print(
        f"[dim]Категории: {', '.join(MEDIA_CATEGORIES)}. Несколько значений разделяйте запятыми.[/dim]"
    )
    selected = Prompt.ask(
        "[bold]Категории файлов[/bold]", default=",".join(settings["media_types"])
    )
    console.print(
        "[dim]Расширения можно указать отдельно: .png, .jpg, .zip, .pdf. all — без фильтра.[/dim]"
    )
    extensions = Prompt.ask(
        "[bold]Расширения[/bold]", default=",".join(settings["extensions"])
    )
    out = Path(
        Prompt.ask("[bold]Папка загрузок[/bold]", default=settings["output_directory"])
    )
    active = AccountRegistry().active()
    account_id = str(active["account_id"]) if active else None
    if active:
        console.print(f"[dim]Активный аккаунт: {active['display_name']}[/dim]")
    return _download(source_text, selected, out, None, account_id, extensions)


def _clear_menu() -> None:
    if console.is_terminal:
        console.clear()


def _menu(title: str, rows: list[tuple[str, str]], hint: str) -> None:
    table = Table(
        title=title,
        show_header=False,
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(0, 1),
        expand=False,
    )
    table.add_column("Key", style="bold bright_cyan", justify="center", width=5)
    table.add_column("Action", style="white")
    for key, action in rows:
        table.add_row(f"[{key}]", action)
    console.print(table)
    console.print(f"[dim]{hint}[/dim]")


def _pause() -> bool:
    return Prompt.ask("[dim]Enter — назад · q — выход[/dim]", default="").strip().lower() == "q"


def _accounts_menu() -> bool:
    registry = AccountRegistry()
    while True:
        _clear_menu()
        console.print(_brand_header("Аккаунты Telegram"))
        _show_accounts()
        _menu(
            "Аккаунты",
            [
                ("1", "Добавить аккаунт"),
                ("2", "Выбрать активный"),
                ("3", "Удалить аккаунт"),
                ("0", "Назад"),
                ("q", "Выход"),
            ],
            "Введите номер · 0 — назад · q — выход",
        )
        choice = Prompt.ask("[bold cyan]Выбор[/bold cyan]", choices=["1", "2", "3", "0", "q"])
        if choice == "q":
            return True
        if choice == "0":
            return False
        if choice == "1":
            _manage_accounts("add", None)
            if _pause():
                return True
        elif choice == "2":
            accounts = registry.all()
            if not accounts:
                console.print("[yellow]Сохранённых аккаунтов пока нет.[/yellow]")
                if _pause():
                    return True
                continue
            account_id = Prompt.ask("ID аккаунта (0 — назад, q — выход)").strip()
            if account_id.lower() == "q":
                return True
            if account_id == "0":
                continue
            _manage_accounts("select", account_id)
            if _pause():
                return True
        else:
            accounts = registry.all()
            if not accounts:
                console.print("[yellow]Сохранённых аккаунтов пока нет.[/yellow]")
                if _pause():
                    return True
                continue
            account_id = Prompt.ask("ID аккаунта для удаления (0 — назад, q — выход)").strip()
            if account_id.lower() == "q":
                return True
            if account_id == "0":
                continue
            _manage_accounts("remove", account_id)
            if _pause():
                return True


def _settings_menu() -> bool:
    settings = UserSettings()
    while True:
        _clear_menu()
        current = settings.load()
        console.print(_brand_header("Настройки"))
        console.print(
            Panel(
                f"[bold]Категории[/bold]  {', '.join(current['media_types'])}\n"
                f"[bold]Расширения[/bold]  {', '.join(current['extensions'])}\n"
                f"[bold]Папка загрузок[/bold]  {current['output_directory']}",
                title="[bold cyan]Текущие настройки[/bold cyan]",
                border_style="bright_blue",
                box=box.ROUNDED,
                expand=False,
            )
        )
        _menu(
            "Настройки загрузки",
            [
                ("1", "Изменить категории файлов"),
                ("2", "Изменить расширения"),
                ("3", "Изменить папку загрузок"),
                ("0", "Назад"),
                ("q", "Выход"),
            ],
            "Введите номер · 0 — назад · q — выход",
        )
        choice = Prompt.ask("[bold cyan]Выбор[/bold cyan]", choices=["1", "2", "3", "0", "q"])
        if choice == "q":
            return True
        if choice == "0":
            return False
        if choice == "1":
            console.print(
                f"[dim]Категории: {', '.join(sorted(ALLOWED_MEDIA_TYPES))}. "
                "all или несколько значений через запятую.[/dim]"
            )
            value = Prompt.ask("Категории", default=",".join(current["media_types"]))
            try:
                updated = settings.update(media_types=value.split(","))
            except ValueError as exc:
                console.print(f"[bold red]Ошибка:[/bold red] {exc}")
                if _pause():
                    return True
            else:
                console.print(
                    f"[green]Сохранены категории: {', '.join(updated['media_types'])}[/green]"
                )
                if _pause():
                    return True
        elif choice == "2":
            console.print(
                "[dim]Примеры: .png,.jpg,.zip. Введите расширения через запятую; all — любой формат.[/dim]"
            )
            value = Prompt.ask("Расширения", default=",".join(current["extensions"]))
            try:
                updated = settings.update(extensions=value.split(","))
            except ValueError as exc:
                console.print(f"[bold red]Ошибка:[/bold red] {exc}")
                if _pause():
                    return True
            else:
                console.print(
                    f"[green]Сохранены расширения: {', '.join(updated['extensions'])}[/green]"
                )
                if _pause():
                    return True
        else:
            value = Prompt.ask("Папка загрузок", default=current["output_directory"])
            try:
                settings.update(output_directory=value)
            except ValueError as exc:
                console.print(f"[bold red]Ошибка:[/bold red] {exc}")
                if _pause():
                    return True
            else:
                console.print("[green]Папка загрузок сохранена.[/green]")
                if _pause():
                    return True


def _home_menu() -> int:
    if not sys.stdin.isatty():
        _parser().print_help()
        return 2
    while True:
        _clear_menu()
        active = AccountRegistry().active()
        account_label = active["display_name"] if active else "Вход не выполнен"
        console.print(_brand_header("Главное меню · загрузка и управление", account_label))
        _menu(
            "Главное меню",
            [
                ("1", "Скачать из Telegram"),
                ("2", "Аккаунты"),
                ("3", "Настройки"),
                ("0", "Выход"),
            ],
            "Введите номер действия · в подменю 0 — назад, q — выход",
        )
        choice = Prompt.ask("[bold cyan]Выбор[/bold cyan]", choices=["1", "2", "3", "0"])
        if choice == "0":
            console.print("[dim]До встречи.[/dim]")
            return 0
        if choice == "1":
            _clear_menu()
            _guided_download()
            if _pause():
                return 0
        elif choice == "2":
            if _accounts_menu():
                return 0
        else:
            if _settings_menu():
                return 0


def _download(
    source_text: str,
    selected: str | None,
    output: Path | None,
    limit: int | None,
    account_id: str | None = None,
    extensions_text: str | None = None,
) -> int:
    try:
        source = parse_source(source_text)
        defaults = UserSettings().load()
        selected = selected or ",".join(defaults["media_types"])
        output = output or Path(defaults["output_directory"])
        extensions_text = extensions_text or ",".join(defaults["extensions"])
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
        detail = f": {exc}" if str(exc) else " (no additional error message)"
        console.print(
            f"[bold red]Telegram operation failed:[/bold red] {type(exc).__name__}{detail}"
        )
        console.print_exception(show_locals=False)
        return 1
    console.print(f"Finished: {downloaded} downloaded, {skipped} skipped.")
    return 0


def _show_accounts() -> int:
    registry = AccountRegistry()
    accounts = registry.all()
    if not accounts:
        console.print(
            Panel(
                "Сохранённых аккаунтов пока нет. Добавьте аккаунт из меню "
                "или командой [cyan]telegram-dumper accounts add[/cyan].",
                title="[bold cyan]Аккаунты Telegram[/bold cyan]",
                border_style="bright_blue",
                box=box.ROUNDED,
                expand=False,
            )
        )
        return 0
    active = registry.active()
    table = Table(
        title="Сохранённые аккаунты",
        header_style="bold cyan",
        border_style="bright_blue",
        box=box.ROUNDED,
    )
    table.add_column("Активный", justify="center")
    table.add_column("Аккаунт")
    table.add_column("Имя пользователя")
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
        "[dim]Переключить: telegram-dumper accounts select ID · "
        "Добавить: telegram-dumper accounts add · Удалить: telegram-dumper accounts remove ID[/dim]"
    )
    return 0


def _manage_accounts(action: str | None, account_id: str | None) -> int:
    registry = AccountRegistry()
    try:
        if action == "add":
            new_id = run_add_account()
            console.print(f"[green]Аккаунт {new_id} добавлен и выбран активным.[/green]")
        elif action == "select":
            account = registry.select(account_id or "")
            console.print(f"[green]Активный аккаунт: {account['display_name']}.[/green]")
        elif action == "remove":
            account = registry.get(account_id or "")
            if account is None:
                raise ValueError(f"No saved Telegram account has ID {account_id}.")
            if not Confirm.ask(
                f"Удалить аккаунт {account['display_name']} и сохранённую сессию?", default=False
            ):
                console.print("Изменений нет.")
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
                            "[bold red]Не удалось удалить сессию или восстановить список аккаунтов. "
                            "Удаление сессии не подтверждено.[/bold red]"
                        )
                        return 2
                    console.print(
                        "[bold red]Не удалось удалить сессию; список аккаунтов восстановлен.[/bold red]"
                    )
                    return 2
            console.print(
                "[green]Аккаунт и сессия удалены. API-данные остались в системном хранилище.[/green]"
            )
        return _show_accounts()
    except (RuntimeError, ValueError, OSError) as exc:
        console.print(f"[bold red]Ошибка:[/bold red] {exc}")
        return 2
    except Exception as exc:
        console.print(
            f"[bold red]Не удалось выполнить действие с аккаунтом:[/bold red] {type(exc).__name__}. "
            "Проверьте системное хранилище учётных данных и повторите попытку."
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
