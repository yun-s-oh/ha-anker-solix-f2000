## 1. CI Release Workflow Alignment (HACS version tagging)

- [ ] 1.1 Refactor `release.yaml` to run Git Tag Action in dry-run mode
- [ ] 1.2 Add step in `release.yaml` to update `manifest.json` version using dry-run tag
- [ ] 1.3 Add step to commit and push the updated `manifest.json` to main branch
- [ ] 1.4 Add step to execute Git Tag Action (non-dry-run) to tag the updated manifest commit
- [ ] 1.5 Verify release tagging aligns version and manifest in dry runs

## 2. Home Assistant DC Keep-Awake Mechanism

- [ ] 2.1 Add `CONF_DC_KEEP_AWAKE` option constant and expose in options flow UI
- [ ] 2.2 Update coordinator logic to monitor AC outlets and charging states
- [ ] 2.3 Implement auto-DC keep-alive command dispatching when idle and enabled
- [ ] 2.4 Add pytest offline unit tests to validate keep-alive coordinator behavior
