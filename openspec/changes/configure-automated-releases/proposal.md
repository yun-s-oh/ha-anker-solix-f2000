## Why

Currently, the custom integration's manifest file contains an outdated repository URL pointing to the wrong username (`yunseokoh`). Furthermore, releasing new versions requires manual tagging and release creation. Setting up automated releases on pushes to `main` that modify the `manifest.json` version field reduces release overhead, guarantees matching version tags, and aligns manifest metadata with the correct repository (`https://github.com/yun-s-oh/ha-anker-solix-f2000`).

## What Changes

- Update `custom_components/anker_solix_f2000/manifest.json` documentation link to `https://github.com/yun-s-oh/ha-anker-solix-f2000`.
- Update `.github/workflows/release.yaml` to trigger on push to the `main` branch.
- Configure the release workflow to calculate the next version using `anothrNick/github-tag-action@1.64.0` (minor bump if `feat` is present, patch bump otherwise), update the `"version"` field in `manifest.json`, commit/push it back to `main` with `[skip ci]`, and publish a GitHub Release with auto-generated release notes.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
<!-- None -->

## Impact

- Pushing to `main` will automatically calculate the next version, update `manifest.json` in the codebase, and release/tag it, without requiring manual intervention.

