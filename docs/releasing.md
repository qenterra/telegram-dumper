# Releasing

## Current release status

No binary or package release is configured. The repository contract sets `release_mode` to `none`;
the version in `pyproject.toml` identifies source development and is not a published release.

## Future release boundary

Creating tags, GitHub Releases, or distributing installable packages requires a separate decision
and an updated repository contract. Before that decision, review the dependency lock, license and
notice inventory, install and upgrade paths, security reporting, and the complete local verification
gate. Do not describe the current source checkout as a signed or supported binary release.
