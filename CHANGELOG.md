# Changelog

All notable changes to telegram-dumper are documented here. This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semver versioning.

## [Unreleased]

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
