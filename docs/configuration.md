# Configuration

## Credentials

Set both environment variables before launching the application:

| Variable | Type | Sensitive | Effect |
| --- | --- | --- | --- |
| `TELEGRAM_API_ID` | Integer | No | Telegram API application identifier |
| `TELEGRAM_API_HASH` | String | Yes | Telegram API application secret |

Obtain the values from [my.telegram.org](https://my.telegram.org). The program does not print the
hash. Telegram login codes and the optional two-step verification password are entered in the
interactive terminal prompt.

After login, Telethon's authorisation session is stored with the operating system credential store
through `keyring`. If no credential-store backend is available, the program refuses to continue
instead of writing a plaintext session file.

## Download options

- `--types`: one or more comma-separated categories: `photo`, `video`, `audio`, `voice`, `document`,
  or `all`.
- `--out`: local output folder. Defaults to `telegram-downloads` in the current directory.
- `--limit`: maximum number of messages to scan.

Command-line options override interactive prompts. There is no project or global configuration file.
