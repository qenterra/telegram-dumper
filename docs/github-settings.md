# GitHub settings and verification

Repository settings were read from the GitHub REST API for `QenTerra/telegram-dumper` on
2026-11-12. This evidence applies only to the fields named below and may become stale.

## Verified settings

| Setting | Verified value |
| --- | --- |
| Visibility | Private |
| Default branch | `main` |
| Issues, Discussions, Projects, Wiki | Disabled |
| Topics | `cli`, `media-downloader`, `python`, `telegram`, `telegram-api` |
| Merge methods | Squash enabled; merge commit and rebase disabled |
| Delete merged branches | Enabled |
| Repository governance workflow | Passed for the initial `main` push |

## Unverified settings and limits

Reading branch protection and repository rulesets returned HTTP 403 with GitHub's response that the
feature requires GitHub Pro or a public repository. Branch protection, pull-request requirements,
required checks, force-push restrictions, and ruleset bypasses therefore remain unverified and are
not represented as configured. Dependabot alerts, secret scanning, push protection, and code scanning
were not checked through provider read-back.

The local QenTerra governance audit reports the external-settings scope as `Unverified`; a passing
local file audit is not evidence that those live provider controls are enabled.
