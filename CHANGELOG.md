# Changelog

All notable changes to telegram-dumper are documented here. This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semver versioning.

## [Unreleased]

## [0.2.1] - 2026-11-12

### Added

- A Telegram-style ASCII header with version, author, and clearer menu navigation.
- Chat and media-category subfolders under the download directory.
- Kebab-case names for chat folders, category folders, and downloaded file stems.
- Immediate link validation before asking for download options.

### Changed

- New downloads default to `~/Downloads/telegram-dumper`; the old default is migrated automatically.

## [0.2.0] - 2026-11-12

### Added

- A home menu with download, account, settings, back, and exit actions.
- Persistent default download folder, media categories, and file-extension filters.
- Direct extension selection for files such as `.png`, `.jpg`, `.zip`, and `.pdf`.

### Added

- Initial terminal CLI scaffold with Telegram link parsing, media category filters, local downloads,
  operating-system credential-store sessions, and protected-content checks.
- A source-built Homebrew formula with pinned Python dependencies and a direct-repository tap
  installation path.
- Guided API setup that can open Telegram's official API application page, hides the API hash during
  entry, and saves API credentials in the operating-system credential store.
- Separate saved Telegram account sessions, active-account selection, one-time account overrides,
  and account management commands.
- Rich terminal guidance for links, media filters, destination folders, account selection, and
  protected-content handling.

### Changed

- Protected chats and messages are skipped; private chats are refused if protection state cannot be
  checked.

### Deprecated

No deprecated surfaces.

### Removed

No removed behaviour.

### Fixed

No fixes recorded.

### Security

- Telegram API hashes and account-specific authorisation sessions are stored through the
  operating-system credential-store interface; plaintext secret or session files are not created.
- The local account registry contains only account IDs, display names, usernames, API IDs, and active
  selection, with owner-only file permissions.

[Unreleased]: https://github.com/QenTerra/telegram-dumper/commits/main
