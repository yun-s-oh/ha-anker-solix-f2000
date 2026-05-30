## ADDED Requirements

### Requirement: Manifest Metadata Accuracy
The integration manifest file `manifest.json` SHALL contain the correct repository URL under the `"documentation"` field, pointing to `https://github.com/yun-s-oh/ha-anker-solix-f2000`.

#### Scenario: Manifest metadata check
- **WHEN** Home Assistant parses the manifest file
- **THEN** it resolves the documentation URL to the correct repository.

### Requirement: Automated Version release on Push
The GitHub Actions release workflow SHALL trigger upon any push to the `main` branch. The workflow SHALL use `anothrNick/github-tag-action@1.64.0` (or similar) to automatically determine the next version: a commit containing `feat` SHALL trigger a minor version update, while any other commit SHALL trigger a patch version update. The workflow SHALL then automatically update the `"version"` field in `manifest.json` with the new version, commit and push it back to `main` (using `[skip ci]` to prevent recursive workflow runs), and publish the corresponding Git tag and GitHub Release with auto-generated release notes.

#### Scenario: Workflow detects feat commit and updates minor version
- **WHEN** a commit starting with `feat:` is pushed to the `main` branch
- **THEN** the workflow calculates a minor version bump, writes it to `manifest.json`, commits and tags it, and publishes a new release.

#### Scenario: Workflow detects non-feat commit and updates patch version
- **WHEN** a regular commit or fix is pushed to the `main` branch
- **THEN** the workflow calculates a patch version bump, writes it to `manifest.json`, commits and tags it, and publishes a new release.

