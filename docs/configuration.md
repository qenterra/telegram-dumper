# Configuration

## Credentials

On first run, the guided setup offers to open [my.telegram.org/apps](https://my.telegram.org/apps),
then prompts for the API credentials. The API hash is hidden as you type. Both values are saved in
the operating-system credential store. You can instead provide the environment variables below;
environment values override stored credentials.

| Variable | Type | Sensitive | Effect |
| --- | --- | --- | --- |
| `TELEGRAM_API_ID` | Integer | No | Telegram API application identifier |
| `TELEGRAM_API_HASH` | String | Yes | Telegram API application secret |

When using environment variables, set `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` together. The Telegram API ID and hash are required to use Telegram's MTProto API. The Telegram website Login
Widget authorizes a user identity for a website or bot; it does not give this CLI access to chat
history or media. Telegram login codes and the optional two-step verification password are entered
in the interactive terminal prompt.

API hash and each account's Telethon authorisation session are stored in the operating-system
credential store through `keyring`. If no credential-store backend is available, the program refuses
to continue rather than writing secrets or sessions to a plaintext file.

## Accounts

The first successful sign-in is saved as the active account. Add, list, and switch accounts with:

```sh
telegram-dumper accounts add
telegram-dumper accounts
telegram-dumper accounts select ACCOUNT_ID
```

Use `telegram-dumper download ... --account ACCOUNT_ID` for a one-time account override. Remove an
account and its session with `telegram-dumper accounts remove ACCOUNT_ID`. The account registry is
stored under the user's application configuration directory with owner-only file permissions; it
contains Telegram account IDs, display names, usernames, and the active selection, not API hashes or
session strings.

## Download options

- `--types`: one or more comma-separated categories: `photo`, `video`, `audio`, `voice`, `document`,
  or `all`.
- `--out`: local output folder. Defaults to `telegram-downloads` in the current directory.
- `--limit`: maximum number of messages to scan.
- `--account`: saved account ID to use for one download instead of the active account.

Command-line options override interactive prompts. There is no project or global configuration file.
