# automated-version-alignment Specification

## Purpose
This specification defines the requirements for automated version alignment during repository releases, ensuring that the version in `manifest.json` is automatically updated and committed to the main branch prior to creating and publishing the official Git release tag.
## Requirements
### Requirement: Dry-Run Release Tag Calculation
The release workflow SHALL calculate the next Git tag in a dry-run mode before modifying
repository files.

#### Scenario: Release dry-run execution
- **WHEN** a push event to the main branch is triggered
- **THEN** the workflow executes the tagging action in dry-run mode to determine the next version.

### Requirement: Synchronized manifest.json Update
The release workflow SHALL update `manifest.json` with the calculated version and push the
change to `main` before creating the final Git tag.

#### Scenario: Tag commit alignment
- **WHEN** the next version tag is calculated
- **THEN** the workflow updates the `version` key in `manifest.json`, commits and pushes this
  change to `main`, and then creates the official Git tag targeting this new commit.

