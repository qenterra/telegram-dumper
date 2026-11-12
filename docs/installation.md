# Installation

`telegram-dumper` requires Python 3.12 or newer. `pipx` installs the command in an isolated
environment, so it does not modify the system Python environment.

## Install pipx

On macOS with Homebrew:

```sh
brew install pipx
pipx ensurepath
```

Open a new terminal after running `pipx ensurepath`. On other systems, follow the
[pipx installation guide](https://pipx.pypa.io/stable/installation/).

## Install telegram-dumper

```sh
pipx install 'git+https://github.com/QenTerra/telegram-dumper.git'
```

Then start the guided setup:

```sh
telegram-dumper
```

The first run needs a Telegram API ID and hash from [my.telegram.org](https://my.telegram.org).
The CLI will prompt for the Telegram account login code and, when enabled, the two-step
verification password.

## Update or uninstall

Install the latest version:

```sh
pipx upgrade telegram-dumper
```

Remove the command and its isolated environment:

```sh
pipx uninstall telegram-dumper
```

The application stores Telegram session data in the operating-system credential store. Uninstalling
the CLI does not remove that session entry or downloaded files. Remove those separately if needed.
