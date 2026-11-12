"""Command-line entry point for telegram-dumper."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from telegram_dumper import __version__
from telegram_dumper.source import parse_source
from telegram_dumper.telegram_client import MEDIA_CATEGORIES, run_download


console = Console()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="telegram-dumper",
        description="Download media you are permitted to save from Telegram.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    download = commands.add_parser("download", help="Download media from a chat or message link")
    download.add_argument("source", help="Telegram channel, chat, or message link")
    download.add_argument(
        "--types",
        default="all",
        help=f"Comma-separated media types: {', '.join(MEDIA_CATEGORIES)} or all",
    )
    download.add_argument("--out", type=Path, default=Path("telegram-downloads"))
    download.add_argument("--limit", type=int, help="Maximum messages to scan")
    return parser


def _guided_download() -> int:
    console.print(
        Panel(
            "[bold cyan]telegram-dumper[/bold cyan]\n"
            "Download Telegram media that your account is allowed to save.\n"
            "Protected messages and protected chats are always skipped.",
            border_style="cyan",
        )
    )
    source_text = Prompt.ask("Telegram link")
    selected = Prompt.ask("File types (all or comma-separated)", default="all")
    out = Path(Prompt.ask("Save folder", default="telegram-downloads"))
    return _download(source_text, selected, out, None)


def _download(source_text: str, selected: str, output: Path, limit: int | None) -> int:
    try:
        source = parse_source(source_text)
        categories = {item.strip().lower() for item in selected.split(",") if item.strip()}
        valid = set(MEDIA_CATEGORIES) | {"all"}
        invalid = categories - valid
        if invalid or not categories:
            raise ValueError(f"Unknown media type(s): {', '.join(sorted(invalid)) or selected}")
        if limit is not None and limit <= 0:
            raise ValueError("--limit must be greater than zero.")
        downloaded, skipped = run_download(source, output.expanduser(), categories, limit)
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


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.command is None:
        raise SystemExit(_guided_download())
    if args.command == "download":
        raise SystemExit(_download(args.source, args.types, args.out, args.limit))
    parser.print_help()
    raise SystemExit(2)


if __name__ == "__main__":
    main()
