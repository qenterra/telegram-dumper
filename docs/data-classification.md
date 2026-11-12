# Data classification

## Data handled

| Class | Examples | Storage | Publication allowed |
| --- | --- | --- | --- |
| Public | Source code, repository metadata | Public GitHub repository | Yes |
| Sensitive | Telegram API hash, authorisation session | Operating-system credential store; optional API environment variables | No |
| Personal metadata | Telegram account IDs, display names, usernames, active account ID | Owner-only local application configuration | No |
| User-controlled | Downloaded media | User-selected local folder | No |

Do not commit secrets, Telegram session data, downloaded media, private chat content, or local
configuration. The program does not upload downloaded files to a service.
