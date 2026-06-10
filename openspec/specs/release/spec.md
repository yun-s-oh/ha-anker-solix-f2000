# release Specification

## Purpose
This specification defines the repository's continuous integration and deployment (CI/CD) release pipeline. It details the requirements for manifest metadata verification, automated version calculations on push events to `main`, synchronization of the manifest file versioning, and publishing of GitHub Releases.
## Requirements
### Requirement: Manifest Metadata Accuracy
The integration manifest file `manifest.json` SHALL contain the correct repository URL under the `"documentation"` field, pointing to `https://github.com/yun-s-oh/ha-anker-solix-f2000`.

#### Scenario: Manifest metadata check
- **WHEN** Home Assistant parses the manifest file
- **THEN** it resolves the documentation URL to the correct repository.

### Requirement: Automated Version release on Push
The GitHub Actions release workflow SHALL trigger upon any push to the `main` branch. The workflow SHALL
automatically determine the next version bump dynamically:
- A commit message containing `major` or `breaking` keyword SHALL trigger a **major** version update.
- A commit message containing `feat` keyword SHALL trigger a **minor** version update.
- Any other commit SHALL trigger a **patch** version update.

The workflow SHALL then automatically update the `"version"` field in `manifest.json` with the new version, commit
and push it back to `main` (using `[skip ci]` to prevent recursive workflow runs), and publish the corresponding
Git tag and GitHub Release with auto-generated release notes.

#### Scenario: Workflow detects major/breaking commit and updates major version
- **WHEN** a commit containing `major` or `breaking` is pushed to the `main` branch
- **THEN** the workflow calculates a major version bump, writes it to `manifest.json`, commits and tags it,
  and publishes a new release.

#### Scenario: Workflow detects feat commit and updates minor version
- **WHEN** a commit containing `feat` is pushed to the `main` branch
- **THEN** the workflow calculates a minor version bump, writes it to `manifest.json`, commits and tags it,
  and publishes a new release.

#### Scenario: Workflow detects other commit and updates patch version
- **WHEN** any other commit is pushed to the `main` branch
- **THEN** the workflow calculates a patch version bump, writes it to `manifest.json`, commits and tags it,
  and publishes a new release.

