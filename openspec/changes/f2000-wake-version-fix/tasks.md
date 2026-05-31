## 1. CI Release Workflow Alignment (HACS version tagging)

- [x] 1.1 Refactor `release.yaml` to run Git Tag Action in dry-run mode
- [x] 1.2 Add step in `release.yaml` to update `manifest.json` version using dry-run tag
- [x] 1.3 Add step to commit and push the updated `manifest.json` to main branch
- [x] 1.4 Add step to execute Git Tag Action (non-dry-run) to tag the updated manifest commit
- [x] 1.5 Verify release tagging aligns version and manifest in dry runs

## 2. Active BLE Interrogation Heartbeat Validation

- [x] 2.1 Verify `TELEMETRY_QUERY` acts as the active wake-up keep-alive heartbeat
- [x] 2.2 Ensure the BLE coordinator maintains a persistent active GATT connection
- [x] 2.3 Verify all changes compile and unit tests pass with clean working tree
