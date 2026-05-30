## 1. Directory Renaming & Reference Updates

- [x] 1.1 Move all files from `test-scripts/` to `tests/`
- [x] 1.2 Update imports and `.env` lookup paths in `tests/diagnose_gatt.py`, `tests/test_passive_telemetry.py`, and `tests/test_heartbeat.py`
- [x] 1.3 Update paths and references in `agent-guidelines.md`

## 2. Core Code & Schema Refinements

- [x] 2.1 Rename `total_pct` sensor description from `"Total Battery"` to `"Battery"` in `sensor.py`
- [x] 2.2 Add translation strings for manual setup options under `strings.json`
- [x] 2.3 Modify `config_flow.py` step manual to accept polling rate and retry limit inputs
- [x] 2.4 Update `config_flow.py` step user and step manual to populate entry options on creation

## 3. Documentation Redesign

- [x] 3.1 Redesign `README.md` to include visual guide features, tables, badges, and the renamed tests folder paths

## 4. Verification and Validation

- [x] 4.1 Run flake8 and compilation style checks
- [x] 4.2 Run pytest unit tests under renamed `tests/` folder and ensure all are passing
