# Changelog

All notable changes to telegram-dumper are documented here. This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semver versioning.

## [Unreleased]

### Added

- Initial terminal CLI scaffold with Telegram link parsing, media category filters, local downloads,
  operating-system credential-store sessions, and protected-content checks.

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

- Telegram authorisation data is stored through the operating-system credential-store interface;
  plaintext session files are not created by the application.

[Unreleased]: https://github.com/QenTerra/telegram-dumper/commits/main
