# Command reference

## Syntax

```text
telegram-dumper [--version]
telegram-dumper
telegram-dumper accounts [add | select <account-id> | remove <account-id>]
telegram-dumper download <link> [--types <list>] [--extensions <list>] [--out <folder>] [--limit <count>] [--account <account-id>]
```

Run `telegram-dumper` without a command to open the home menu. Choose Downloads, Accounts, or
Settings; nested menus include a Back option.

## Commands

| Command | Purpose | Destructive |
| --- | --- | --- |
| `download <link>` | Download matching files from a chat or one message | No; creates files in the selected local folder |
| `accounts` | List saved accounts and show which one is active | No |
| `accounts add` | Sign in and save another Telegram account | No; adds a local credential-store session |
| `accounts select <account-id>` | Make a saved account active for later downloads | No |
| `accounts remove <account-id>` | Remove the local account record and its stored session | Yes; confirmation is required |
| `--version` | Print the installed version | No |

The first successful Telegram sign-in becomes the active account. Use `--account <account-id>` on
`download` to use another saved account for one run without changing the active selection.

`download` accepts HTTPS `t.me` and `telegram.me` channel/chat links, including direct message
links. A private `/c/` message link works only when the signed-in account has access and the chat is
present in its Telegram dialogs. Invite links are not joined automatically.

On first use, the guided flow can open Telegram's API application page. API hashes and account
sessions are stored in the operating-system credential store. The local account list contains only
account IDs, display names, usernames, and the active selection.

The home menu's Settings section saves default categories, extensions, and download folder locally.
Use `--extensions .png,.jpg,.zip` to match those original file extensions directly. Omit the filter
or use `all` to include every file format.

By default, files go under `~/Downloads/telegram-dumper/<chat-name-id>/<category>/`, sorted into
kebab-case folders such as `фото`, `видео`, `аудио`, and `файлы`. Downloaded filename stems also
use kebab-case, with the original file extension preserved in lowercase. In the interactive download
flow, the link is validated before category, extension, or folder prompts appear.

## Output and exit status

Progress and status messages are human-readable terminal output. Exit code `0` means the scan
finished; `2` means input, configuration, or filesystem validation failed. Telegram network and
authentication errors may currently surface as library errors.

Existing output filenames are skipped. The program does not overwrite them. It does not emit a
machine-readable output format in this initial version.
