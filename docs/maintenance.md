# Repository maintenance

## Ownership and cadence

Nikita Melnychenko (QenTerra) owns repository maintenance. This public project has no scheduled
release cadence; review dependencies and access when preparing a change or release.

## Routine review

- Weekly or event-driven: triage security alerts, dependency updates, failed workflows, support requests, and release blockers.
- Monthly: review stale issues and pull requests, flaky checks, documentation drift, dependency removals, generated artifacts, and support status.
- Quarterly: verify ownership, branch and tag rules, GitHub features, topics, security settings, support contacts, license notices, Wiki projection, and recovery instructions.
- Before every release: follow `docs/releasing.md` against the exact release commit.
- Before every release: audit the canonical checkout and a fresh clean clone for operational artifacts, caches, ignored debris, and undeclared generated output.

## Dependency and security lifecycle

Record accepted update sources, lockfile ownership, vulnerability decisions, private disclosure handling, removed dependencies, and third-party notice changes. Do not merge an automated update because the automation looked confident.

## Documentation and compatibility

Retest documented setup, install, quick-start, migration, troubleshooting, and recovery paths. Mark volatile provider instructions with their verification date and update compatibility tables when support changes.

## Inactivity, transfer, and archival

If active maintenance stops, update the README and repository description with status, final supported version, replacement, security boundary, and archival date. Transfers, visibility changes, archival, deletion, and publication remain separately authorised external actions.

## Maintenance record

No maintenance review has been recorded yet.
