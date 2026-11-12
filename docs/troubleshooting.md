# Troubleshooting

## Before collecting data

Confirm the version, supported environment, expected behaviour, and exact failing step. Remove credentials, personal paths, user content, signing data, and unrelated system logs.

## Symptoms

| Symptom | Safe checks | Likely boundary | Recovery |
| --- | --- | --- | --- |
| `TELEGRAM_API_ID` or hash missing | Check that both environment variables are set; never paste the values into a report | Local shell configuration | Set the values in the current shell and retry |
| Private message link cannot be resolved | Open the chat in Telegram with the same account and confirm it appears in dialogs | Telegram account access | Retry after the account has access |
| Protected message was skipped | Check the source chat's Telegram content-protection setting | Telegram protection policy | No download workaround is provided |
| Credential store unavailable | Check that the operating system credential store is unlocked | Local operating system | Unlock the credential store and retry |

## Diagnostic report

Include:

- version or full commit;
- operating system, architecture, runtime, browser, device, or deployment as relevant;
- smallest reproduction;
- expected and actual behaviour;
- sanitised logs and synthetic fixtures;
- checks already attempted and their exact results.

## Recovery

Prefer reversible steps. State what data changes, what remains preserved, and how to verify success. Destructive reset or deletion instructions require an explicit backup and exact target.
