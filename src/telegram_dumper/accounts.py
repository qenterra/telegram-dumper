"""Non-secret metadata for locally configured Telegram accounts."""

from __future__ import annotations

import json
import os
import getpass
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _config_directory() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home())) / "telegram-dumper"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "telegram-dumper"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "telegram-dumper"


def _restrict_permissions(path: Path, *, directory: bool) -> None:
    if os.name == "nt":
        username = getpass.getuser()
        domain = os.environ.get("USERDOMAIN")
        principal = f"{domain}\\{username}" if domain else username
        permission = f"{principal}:(OI)(CI)F" if directory else f"{principal}:F"
        try:
            subprocess.run(
                ["icacls", str(path), "/inheritance:r", "/grant:r", permission],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError(
                f"Could not restrict access to the local account registry at {path}."
            ) from exc
        return
    try:
        os.chmod(path, 0o700 if directory else 0o600)
    except OSError as exc:
        raise RuntimeError(
            f"Could not restrict access to the local account registry at {path}."
        ) from exc


class AccountRegistry:
    """Store account labels and selection; account sessions remain in the keyring."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (_config_directory() / "accounts.json")

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema_version": 1, "active_account_id": None, "accounts": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Could not read account list at {self.path}. Repair or remove that file and retry."
            ) from exc
        if (
            not isinstance(data, dict)
            or set(data) != {"schema_version", "active_account_id", "accounts"}
            or data.get("schema_version") != 1
            or not isinstance(data.get("accounts"), list)
        ):
            raise RuntimeError(f"Account list at {self.path} has an unsupported format.")
        seen: set[str] = set()
        for account in data["accounts"]:
            if not isinstance(account, dict):
                raise RuntimeError(f"Account list at {self.path} contains an invalid entry.")
            if set(account) - {"account_id", "api_id", "display_name", "username"}:
                raise RuntimeError(
                    f"Account list at {self.path} contains unsupported account fields."
                )
            account_id = account.get("account_id")
            api_id = account.get("api_id")
            if (
                not isinstance(account_id, str)
                or not account_id.isdecimal()
                or account_id in seen
                or not isinstance(api_id, str)
                or not api_id.isdecimal()
                or not isinstance(account.get("display_name"), str)
                or not isinstance(account.get("username", ""), str)
            ):
                raise RuntimeError(f"Account list at {self.path} contains an invalid entry.")
            seen.add(account_id)
        active_id = data.get("active_account_id")
        if active_id is not None and (
            not isinstance(active_id, str) or active_id not in seen
        ):
            raise RuntimeError(f"Account list at {self.path} selects an account that is not present.")
        return data

    def all(self) -> list[dict[str, Any]]:
        return self.load()["accounts"]

    def active(self) -> dict[str, Any] | None:
        data = self.load()
        account_id = data.get("active_account_id")
        return next(
            (account for account in data["accounts"] if account.get("account_id") == account_id),
            None,
        )

    def get(self, account_id: str) -> dict[str, Any] | None:
        return next(
            (account for account in self.all() if account.get("account_id") == str(account_id)),
            None,
        )

    def upsert(self, account: dict[str, str], *, activate: bool = True) -> None:
        data = self.load()
        account_id = str(account["account_id"])
        record = {
            "account_id": account_id,
            "api_id": str(account["api_id"]),
            "display_name": account["display_name"],
            "username": account.get("username", ""),
        }
        accounts = [item for item in data["accounts"] if item.get("account_id") != account_id]
        accounts.append(record)
        accounts.sort(key=lambda item: item["display_name"].casefold())
        data["accounts"] = accounts
        if activate or data.get("active_account_id") is None:
            data["active_account_id"] = account_id
        self._write(data)

    def select(self, account_id: str) -> dict[str, Any]:
        data = self.load()
        account_id = str(account_id)
        if not any(item.get("account_id") == account_id for item in data["accounts"]):
            raise ValueError(f"No saved Telegram account has ID {account_id}.")
        data["active_account_id"] = account_id
        self._write(data)
        return next(item for item in data["accounts"] if item["account_id"] == account_id)

    def remove(self, account_id: str) -> dict[str, Any]:
        data = self.load()
        account_id = str(account_id)
        removed = next(
            (item for item in data["accounts"] if item.get("account_id") == account_id), None
        )
        if removed is None:
            raise ValueError(f"No saved Telegram account has ID {account_id}.")
        data["accounts"] = [
            item for item in data["accounts"] if item.get("account_id") != account_id
        ]
        if data.get("active_account_id") == account_id:
            data["active_account_id"] = (
                data["accounts"][0]["account_id"] if data["accounts"] else None
            )
        self._write(data)
        return removed

    def _write(self, data: dict[str, Any]) -> None:
        directory = self.path.parent
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        _restrict_permissions(directory, directory=True)

        descriptor, temporary_name = tempfile.mkstemp(prefix=".accounts-", dir=directory)
        temporary_path = Path(temporary_name)
        try:
            if hasattr(os, "fchmod"):
                os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as output:
                json.dump(data, output, ensure_ascii=False, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary_path, self.path)
            _restrict_permissions(self.path, directory=False)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
