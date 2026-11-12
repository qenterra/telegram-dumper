# telegram-dumper

A terminal client for downloading media from Telegram chats your account can access and is permitted to save.

[Commands](docs/command-reference.md) · [Configuration](docs/configuration.md) · [Architecture](docs/architecture.md)

## Status and access

Early development. This is a private QenTerra repository, licensed for internal use only. No package
or binary release is available. Requires Python 3.12+, a Telegram API application ID and hash from
[my.telegram.org](https://my.telegram.org), and an account that can access the source chat.

Owner: Nikita Melnychenko (QenTerra).

## Scope

- Intended outcome: download media the signed-in account is permitted to save.
- Included data: Telegram media selected by the user, saved to a local folder.
- Exclusions: protected content, invite-link joining, format conversion, public distribution, and
  upload of downloaded files to another service.
- Retention trigger: local downloads remain until the user removes them; the app does not expire or
  delete downloaded files.

## Install and quick start

Install `pipx` and GitHub CLI (`gh`), then sign in to GitHub with an account that can read this
private repository. On macOS with Homebrew:

```sh
brew install pipx gh
pipx ensurepath
```

Open a new terminal after `pipx ensurepath`, then install and run the CLI with:

```sh
gh auth setup-git && pipx install 'git+https://github.com/QenTerra/telegram-dumper.git'
telegram-dumper
```

`gh auth setup-git` configures Git to use your existing GitHub CLI login when pipx fetches the
private repository. It does not expose or put your token in the command. To update or remove the
installation later:

```sh
pipx upgrade telegram-dumper
pipx uninstall telegram-dumper
```

Before the first run, set `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` in the shell. Telegram will ask
for the account login code and, if enabled, the two-step verification password.

Start the guided terminal flow:

```sh
telegram-dumper
```

Or pass a link directly:

```sh
telegram-dumper download 'https://t.me/example/123' --types photo,video --out ./downloads
```

The tool keeps Telegram's original file formats. `--types` filters media categories; it does not
convert files.

## Protection and privacy

Protected chats and messages are skipped. The tool refuses downloads from a private chat when it
cannot verify the chat's protection state. It does not attempt to bypass restrictions on saving,
forwarding, or copying content. Use it only for material you have the right to save.

Telegram credentials and session data are not written to the repository. The application stores
session data in the operating-system credential store. Downloaded files remain in the selected local
folder and are not sent elsewhere by the application.

## Data and recovery

Read [Data classification](docs/data-classification.md), [Retention](docs/retention.md), and
[Security](SECURITY.md). A partial file may remain if a download is interrupted; inspect it locally
before retrying. Existing filenames are skipped to avoid overwriting files.

## Documentation

- [Command reference](docs/command-reference.md)
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

Copyright © 2026 Nikita Melnychenko (QenTerra). All rights reserved unless a separate written agreement states otherwise.
