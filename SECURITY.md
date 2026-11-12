# Security

## Supported versions

Security fixes target only release lines listed here. Do not label an older line supported unless fixes are built, tested, and published for it.

| Release line | Supported | End of support | Evidence |
| --- | --- | --- | --- |
| No released version | No | No release published | Early development |

## Report a vulnerability

Report vulnerabilities privately through [GitHub Security Advisories](https://github.com/QenTerra/telegram-dumper/security/advisories/new). Do not open a public issue with exploit details, secrets, personal data, or vulnerable production information.

Include the affected version or commit, environment, expected impact, reproduction steps, and the smallest safe proof of concept. Remove credentials, personal paths, user content, signing material, and unrelated logs.

## Response

The maintainers will acknowledge a complete report, assess severity and affected versions, coordinate a fix and disclosure, and publish an advisory when appropriate.

| Stage | Target | Starts when | Evidence |
| --- | --- | --- | --- |
| Acknowledgement | No fixed target | A complete report reaches the private route | Private acknowledgement |
| Initial assessment | No fixed target | Reproduction material is safe and sufficient | Severity and affected-version record |
| Coordination update | As needed | A fix or disclosure remains open | Private status update |

No response-time commitment is currently offered. Delays caused by incomplete evidence, unsafe
reproduction, third-party coordination, or broader impact are communicated through the private
report.

## Boundaries

The application handles Telegram API credentials, login codes, account session data, private chat
metadata, and downloaded media. Credentials and sessions stay outside Git. Protected-content checks
must not be weakened to work around Telegram restrictions.
