# Installation

`telegram-dumper` requires Python 3.12 or newer.

## Install with Homebrew

The formula is in this repository, so add it as a tap using its direct GitHub URL, then install:

```sh
brew tap qenterra/telegram-dumper https://github.com/QenTerra/telegram-dumper.git
brew install qenterra/telegram-dumper/telegram-dumper
```

Homebrew installs Python and the pinned application dependencies in an isolated formula
environment. To update or remove the app:

```sh
brew upgrade qenterra/telegram-dumper/telegram-dumper
brew uninstall qenterra/telegram-dumper/telegram-dumper
```

Then open the interactive menu:

```sh
telegram-dumper
```

On first run, the CLI offers to open [my.telegram.org/apps](https://my.telegram.org/apps), where you
can create an API ID and hash. It hides the hash while you enter it and stores both values in the
operating-system credential store. Telegram then sends a login code to your account; if two-step
verification is enabled, the CLI also asks for that password.

Manage multiple accounts with:

```sh
telegram-dumper accounts add
telegram-dumper accounts
telegram-dumper accounts select ACCOUNT_ID
```

Each Telegram session is stored separately in the system credential store. The local account list
contains only account identifiers, display names, usernames, and the active selection.

## Update or uninstall

Update Homebrew and install the latest version:

```sh
brew update
brew upgrade telegram-dumper
```

Remove the Homebrew installation:

```sh
brew uninstall telegram-dumper
```

Uninstalling the CLI does not remove saved API credentials, Telegram sessions, the local account
list, or downloaded files. Remove accounts with `telegram-dumper accounts remove ACCOUNT_ID` before
uninstalling if you want their saved sessions deleted.
