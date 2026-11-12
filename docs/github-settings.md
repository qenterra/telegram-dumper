# GitHub settings and verification

Repository files declare expected behaviour but do not prove live GitHub settings. Verify the exact repository through an authorised API query or settings review and retain the evidence with the adopting task.

## Metadata and features

Confirm the canonical owner and repository URL, description, homepage, topics, visibility, default branch, and the Issues, Discussions, Wiki, and Projects switches declared in `.github/qenterra-repository.json`. Disable a surface that has no owner or workflow.

## Branch and tag rules

- Protect `main` against deletion and force pushes.
- Require focused pull requests, the project gate, `repository-governance`, conversation resolution, and linear history.
- Require independent approval and Code Owner review for team repositories; record honest self-review for solo repositories.
- Restrict bypass, preserve emergency evidence, and protect release tags from replacement.

## Merge and lifecycle settings

Enable squash merge, disable unused merge methods, delete merged head branches, and keep the default branch at `main`. Record any long-lived release-branch exception and its support window.

## Security and supply chain

Review dependency graph, Dependabot alerts and updates, secret scanning, push protection, code scanning, private vulnerability reporting, workflow permissions, environment protection, artifact attestations, and immutable releases where supported and applicable.

## Verification record

Repository privacy and branch settings have not yet been verified through GitHub read-back.

Never copy a prior repository’s result forward. Provider features, plan availability, and settings can change without a source diff.
