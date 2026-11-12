# telegram-dumper

A terminal client for downloading media from Telegram chats your account can access and is permitted to save.

[Commands](docs/command-reference.md) · [Configuration](docs/configuration.md) · [Architecture](docs/architecture.md)

## Status and requirements

Early development. This is a public QenTerra repository under the MIT License. Homebrew builds the
command from source; no prebuilt binary is released. Requires Python 3.12+, a Telegram API
application ID and hash from [my.telegram.org](https://my.telegram.org), and an account that can
access the source chat.

Owner: Nikita Melnychenko (QenTerra).

## Scope

- Intended outcome: download media the signed-in account is permitted to save.
- Included data: Telegram media selected by the user, saved to a local folder.
- Exclusions: protected content, invite-link joining, format conversion, public distribution, and
  upload of downloaded files to another service.
- Retention trigger: local downloads remain until the user removes them; the app does not expire or
  delete downloaded files.

## Install and quick start

Install directly with Homebrew. This taps the formula from this repository and installs it:

```sh
brew tap qenterra/telegram-dumper https://github.com/QenTerra/telegram-dumper.git && brew install qenterra/telegram-dumper/telegram-dumper
```

Then open the interactive menu:

```sh
telegram-dumper
```

See the [installation guide](docs/installation.md) for updates, removal, and the pipx alternative.
The menu provides download, account, and settings sections, with a back option in each submenu.
You can set default file categories, extensions such as `.png`, `.jpg`, or `.zip`, and the download
folder. Settings are saved locally. On first sign-in, the CLI can open Telegram's API setup page,
collect the API ID/hash, and store them securely.

Start the guided terminal flow:

```sh
telegram-dumper
```

Or pass a link directly:

```sh
telegram-dumper download 'https://t.me/example/123' --types all --extensions .png,.zip --out ./downloads
```

The tool keeps Telegram's original file formats. `--types` filters media categories and
`--extensions` filters filename extensions; neither converts files.

## Protection and privacy

Protected chats and messages are skipped. The tool refuses downloads from a private chat when it
cannot verify the chat's protection state. It does not attempt to bypass restrictions on saving,
forwarding, or copying content. Use it only for material you have the right to save.

Telegram API credentials and account sessions are not written to the repository; they are stored in
the operating-system credential store. A local configuration file keeps only account identifiers,
display names, usernames, and the selected active account. Downloaded files remain in the selected
folder and are not sent elsewhere by the application.

## Data and recovery

Read [Data classification](docs/data-classification.md), [Retention](docs/retention.md), and
[Security](SECURITY.md). A partial file may remain if a download is interrupted; inspect it locally
before retrying. Existing filenames are skipped to avoid overwriting files.

## Commands and configuration

- [Command reference](docs/command-reference.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)

## Documentation

- [Command reference](docs/command-reference.md)
- [Installation](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Architecture](docs/architecture.md)
- [Development](docs/development.md)
- [Security](SECURITY.md)

Run `bash scripts/verify-repository.sh` for the repository governance audit and Python syntax
compilation. This does not prove that a Telegram login or live media transfer succeeds.

## Contact

- Product support, product help, and technical questions: [support@qenterra.com](mailto:support@qenterra.com).
- Proposals, general enquiries, and commercial matters: [contact@qenterra.com](mailto:contact@qenterra.com).
- Vulnerabilities: follow the private reporting process in [SECURITY.md](SECURITY.md).

## License

Copyright © 2026 Nikita Melnychenko (QenTerra). Distributed under the terms of the [MIT License](LICENSE).
