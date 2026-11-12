# Contributing

Focused bug fixes, tests, documentation corrections, and well-scoped improvements are welcome.

## Before opening an issue

1. Search existing issues and documentation.
2. Reproduce the problem on a supported version.
3. Remove credentials, personal paths, private data, copyrighted fixtures, and unrelated logs.
4. Use the issue form that matches the request. Report vulnerabilities through `SECURITY.md`, never a public issue.

## Development setup

```sh
git clone https://github.com/QenTerra/telegram-dumper.git
cd telegram-dumper
pipx install 'git+https://github.com/QenTerra/telegram-dumper.git'
```

Requirements: Python 3.12 or newer, a Telegram API application ID and hash, and an account permitted to access the source chat.

## Required checks

```sh
bash scripts/verify-repository.sh
git diff --check
```

State any hardware, accessibility, performance, security, deployment, or provider behaviour these checks do not prove.

## Branches and commits

- Create `qenterra/<short-kebab-purpose>` from the current `main`.
- Use Conventional Commit subjects with an allowed type and optional lowercase scope.
- Write in English unless the project explicitly selects another language. Use an imperative description, no trailing period, and at most 72 characters for the complete subject; for example, `fix(parser): reject an empty configuration`.
- Explain why in the optional body. Mark incompatible changes with `!` or a `BREAKING CHANGE:` footer, and always include actionable migration guidance in the footer.
- Keep one coherent outcome per commit and pull request.
- Remove fixup, squash, WIP, and checkpoint commits before review.

## Pull requests

Use a Conventional Commit title. Keep the template's section order and describe the final diff: purpose, scope, verification, evidence, risk and recovery, documentation and release, then checklist. Complete required fields; explain inapplicable items briefly. Use concrete outcomes, sentence case, and ordinary Markdown without emoji headings or generic praise.

Review comments state the condition, location, consequence, and requested change. Use a priority only for a substantiated finding; label nonblocking suggestions explicitly. Resolution replies identify the repair revision and the actual verification result.

- Explain purpose, scope, verification, risk, migration, documentation, privacy/security, and release impact.
- Add a regression test when behaviour can be checked deterministically.
- Include screenshots or recordings for visible changes and identify the exact build and fixture.
- Update public documentation and changelog when users, consumers, or operators are affected.
- Do not commit generated caches, credentials, signing material, personal data, private planning, or unreviewed artifacts.

By contributing, you agree that your contribution is licensed under the repository’s declared MIT terms.
