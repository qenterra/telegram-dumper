# Style guide

## Language

Public code identifiers, repository documentation, issues, pull requests, commits, and release notes use English. Preserve exact product names, APIs, standards, and user-facing localisations where required.

## Names and layout

- Repository and general directories use lowercase `kebab-case`.
- Every maintained file and directory uses lowercase kebab-case unless an external tool or provider requires one exact spelling.
- Keep each nonbuilt-in naming exception as one exact `path-naming` record in `.github/qenterra-repository.json`; wildcard and directory-wide waivers are invalid.
- Python modules use lowercase names; the importable package directory `src/telegram_dumper` is an
  exact contract exception because Python import identifiers cannot contain hyphens.
- New top-level paths require an architectural or tooling reason and a documentation update.

## Code

Use explicit functions and narrow modules. Keep Telegram protection checks independent from download
logic. Ruff is configured as the future formatter and linter; it is not part of the current gate.

## Documentation

Use descriptive headings, portable Markdown, runnable examples, meaningful link text, image alternative text, and one source of truth per durable subject. Do not publish placeholders or internal operational prose.

## Accessibility and inclusive language

Treat keyboard access, assistive technology, contrast, reduced motion, localisation, and clear error text as product requirements where the profile exposes an interface.
