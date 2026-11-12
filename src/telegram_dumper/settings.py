"""Persistent, non-secret preferences for the interactive terminal menu."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from telegram_dumper.accounts import config_directory, restrict_permissions


DEFAULT_SETTINGS: dict[str, Any] = {
    "schema_version": 1,
    "media_types": ["all"],
    "extensions": ["all"],
    "output_directory": "~/Downloads/telegram-dumper",
}
ALLOWED_MEDIA_TYPES = {"photo", "video", "audio", "voice", "document", "all"}


def normalize_extensions(extensions: list[str]) -> list[str]:
    normalized = list(
        dict.fromkeys(item.strip().lower() for item in extensions if item.strip())
    )
    normalized = [
        item if item == "all" or item.startswith(".") else f".{item}"
        for item in normalized
    ]
    if (
        not normalized
        or any(
            item != "all" and not re.fullmatch(r"\.[a-z0-9][a-z0-9._+-]*", item)
            for item in normalized
        )
        or ("all" in normalized and normalized != ["all"])
    ):
        raise ValueError("Enter file extensions such as .png,.jpg,.zip, or use all.")
    return normalized


class UserSettings:
    """Read and write safe, non-secret user preferences."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (config_directory() / "settings.json")

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return dict(DEFAULT_SETTINGS)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Could not read settings at {self.path}. Repair or remove that file and retry."
            ) from exc
        if (
            not isinstance(data, dict)
            or set(data) != {"schema_version", "media_types", "extensions", "output_directory"}
            or data.get("schema_version") != 1
            or not isinstance(data.get("media_types"), list)
            or not data["media_types"]
            or any(
                not isinstance(item, str) or item not in ALLOWED_MEDIA_TYPES
                for item in data["media_types"]
            )
            or ("all" in data["media_types"] and data["media_types"] != ["all"])
            or not isinstance(data.get("extensions"), list)
            or not data["extensions"]
            or any(
                not isinstance(item, str)
                or (item != "all" and not re.fullmatch(r"\.[a-z0-9][a-z0-9._+-]*", item))
                for item in data["extensions"]
            )
            or ("all" in data["extensions"] and data["extensions"] != ["all"])
            or not isinstance(data.get("output_directory"), str)
            or not data["output_directory"].strip()
        ):
            raise RuntimeError(f"Settings at {self.path} have an unsupported format.")
        if data["output_directory"] == "telegram-downloads":
            data["output_directory"] = DEFAULT_SETTINGS["output_directory"]
            self._write(data)
        return data

    def update(
        self,
        *,
        media_types: list[str] | None = None,
        extensions: list[str] | None = None,
        output_directory: str | None = None,
    ) -> dict[str, Any]:
        data = self.load()
        if media_types is not None:
            normalized = list(
                dict.fromkeys(item.strip().lower() for item in media_types if item.strip())
            )
            if (
                not normalized
                or any(item not in ALLOWED_MEDIA_TYPES for item in normalized)
                or ("all" in normalized and normalized != ["all"])
            ):
                raise ValueError(
                    "Choose all, or a comma-separated list of photo, video, audio, voice, document."
                )
            data["media_types"] = normalized
        if extensions is not None:
            data["extensions"] = normalize_extensions(extensions)
        if output_directory is not None:
            if not output_directory.strip():
                raise ValueError("The download folder cannot be empty.")
            data["output_directory"] = output_directory.strip()
        self._write(data)
        return data

    def _write(self, data: dict[str, Any]) -> None:
        directory = self.path.parent
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        restrict_permissions(directory, directory=True)
        descriptor, temporary_name = tempfile.mkstemp(prefix=".settings-", dir=directory)
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
            restrict_permissions(self.path, directory=False)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
