## 1. Configuration Updates

- [x] 1.1 Correct documentation URL in `custom_components/anker_solix_f2000/manifest.json`

## 2. GitHub Actions Configuration

- [x] 2.1 Update `.github/workflows/release.yaml` to trigger on push to `main`
- [x] 2.2 Configure `release.yaml` to calculate and push the version tag using `anothrNick/github-tag-action@1.64.0` in live mode (minor on `feat`, patch otherwise)
- [x] 2.3 Add step in `release.yaml` to update `manifest.json` with the new version and commit it with `[skip ci]`
- [x] 2.4 Add step in `release.yaml` to push the new git tag and publish a GitHub Release

## 3. Code Validation & Quality

- [x] 3.1 Run compilation check via `py_compile`
- [x] 3.2 Run formatting check via `flake8`
- [x] 3.3 Run unit tests via `pytest`

