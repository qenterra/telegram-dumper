# Testing

## Complete gate

```sh
bash scripts/verify-repository.sh
```

The current script runs the repository-governance audit and Python syntax compilation. This early
scaffold has no automated behavior-test suite yet.

## Test layers

| Layer | Purpose | Command | Evidence limit |
| --- | --- | --- | --- |
| Static syntax | Python source parses and compiles | `bash scripts/verify-repository.sh` | Does not prove program behavior |
| Repository governance | Contract and required repository structure | `bash scripts/verify-repository.sh` | Does not prove runtime or GitHub settings |
| Telegram acceptance | Login, protection detection, and media transfer | Manual session with an authorised account | Not yet performed |

## Fixtures

Use synthetic, deterministic fixtures. Do not read personal data, live user libraries, production credentials, or mutable external resources unless a separately authorised acceptance test requires them.

## Failures and flaky tests

Reproduce before repair, preserve the failing evidence, identify whether the environment or product failed, and never weaken assertions to make a gate green.
