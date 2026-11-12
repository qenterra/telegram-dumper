# Data classification

## Data handled

| Class | Examples | Storage | Publication allowed |
| --- | --- | --- | --- |
| Internal | Source code, repository metadata | Private GitHub repository | No |
| Sensitive | Telegram API hash, login credentials, authorisation session | Shell environment and operating-system credential store | No |
| User-controlled | Downloaded media and local chat metadata | User-selected local folder | No |

Do not commit secrets, Telegram session data, downloaded media, private chat content, or local
configuration. The program does not upload downloaded files to a service.
