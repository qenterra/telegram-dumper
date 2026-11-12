# Dependencies

## Policy

- Prefer maintained dependencies from canonical registries or verified upstream repositories.
- Pin or lock resolved versions appropriate to python and commit the lockfile when the ecosystem expects it.
- Review source, maintainer status, release notes, compatibility, transitive impact, license, vulnerabilities, and final lockfile diff.
- Keep runtime and bundled dependencies minimal; development tooling does not silently become a shipped dependency.

## Inventory

Runtime dependencies are declared in `pyproject.toml`: Telethon for Telegram client access, `keyring`
for operating-system credential storage, and Rich for terminal rendering and progress. Resolved
versions and SPDX license metadata are not yet locked; review both before any distribution.

## Updates

Review upstream release notes, compatibility, transitive dependencies, and license metadata before
updating. Major updates require migration review. Security alerts are evidence to investigate, not
permission for an unreviewed forced update.

## Removal

Remove unused code paths, configuration, lockfile entries, notices, caches, and documentation together. Verify the built artifact no longer contains the dependency.
