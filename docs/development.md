# Development

## Requirements

Python 3.12 or newer, a Telegram API application ID and hash, and a Telegram account permitted to access the source chat.

## Setup

```sh
git clone https://github.com/QenTerra/telegram-dumper.git
cd telegram-dumper
python3 -m pip install -e .
```

## Common workflow

```sh
git switch -c qenterra/<short-kebab-purpose>
bash scripts/verify-repository.sh
git diff --check
```

The current verification script runs a repository-governance audit and compiles the Python package.
It does not run a behavioral test suite or connect to Telegram.

## Configuration and secrets

The CLI uses command-line flags and `TELEGRAM_API_ID` / `TELEGRAM_API_HASH`. Never commit live
credentials, Telegram session data, downloaded files, or user content.

## Generated source

No generated product source is committed.

Keep private operational planning, transient work state, caches, local environments, logs, coverage, test output, and temporary build state outside the checkout. Commit consumer-facing generated output only when `.github/qenterra-repository.json` declares it under `published_artifacts` with a separate source path, a `schemaVersion: 1` JSON manifest covering every source and artifact file by SHA-256 and strict integer byte count, an existing Git-tracked `scripts/` verifier, and a concrete regeneration trigger. A source without a readable Git index leaves tracking `Unverified`. The static audit never executes that command; run it separately in an isolated temporary checkout before publication.

## Debugging

Do not enable protocol-level debug logging when handling account credentials or private messages.
Report errors without sharing login codes, API hashes, session contents, or downloaded media.
