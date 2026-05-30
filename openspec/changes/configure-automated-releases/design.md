## Context

The current integration manifest (`manifest.json`) points to the wrong GitHub owner's repository, and the GitHub release process requires manually creating and pushing git tags (`v*`). Automating tag generation and release publications when the version changes inside `manifest.json` simplifies the release pipeline.

## Goals / Non-Goals

**Goals:**
- Update `manifest.json` with the correct documentation link pointing to the new owner's repository.
- Re-configure `.github/workflows/release.yaml` to run automatically on pushes to `main`.
- Use `anothrNick/github-tag-action@1.64.0` to calculate the next version tag. A `feat` commit will result in a minor bump; everything else will trigger a patch bump.
- Update the version inside `manifest.json` and commit it back using `[skip ci]` to prevent recursive pipelines.

**Non-Goals:**
- Modifying test validation workflows (`validate.yaml`) or standard code behavior.

## Decisions

### Trigger Release on Push to main
The release action will run when changes are pushed to `main`.

```yaml
on:
  push:
    branches:
      - main
```

### Versioning Logic & Commit
We will use `anothrNick/github-tag-action@1.64.0` in live mode (no dry-run) to determine and push the next version tag. We then extract the version value, use `jq` to update `"version"` in `manifest.json`, and commit it with a `[skip ci]` tag.


## Risks / Trade-offs

- **[Risk]**: Recursive CI trigger when pushing the updated `manifest.json` back to `main`.
  - *Mitigation*: We will use a commit message containing `[skip ci]` to prevent GitHub Actions from running on the automated commit.

