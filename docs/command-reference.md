# Command reference

## Syntax

```text
telegram-dumper [--version] [download <link> [--types <list>] [--out <folder>] [--limit <count>]]
```

Run `telegram-dumper` without a command to open the guided terminal flow.

## Commands

| Command | Purpose | Destructive |
| --- | --- | --- |
| `download <link>` | Download matching files from a chat or one message | No; creates files in the selected local folder |
| `--version` | Print the installed version | No |

`download` accepts HTTPS `t.me` and `telegram.me` channel/chat links, including direct message
links. A private `/c/` message link works only when the signed-in account has access and the chat is
present in its Telegram dialogs. Invite links are not joined automatically.

## Output and exit status

Progress and status messages are human-readable terminal output. Exit code `0` means the scan
finished; `2` means input, configuration, or filesystem validation failed. Telegram network and
authentication errors may currently surface as library errors.

Existing output filenames are skipped. The program does not overwrite them. It does not emit a
machine-readable output format in this initial version.
