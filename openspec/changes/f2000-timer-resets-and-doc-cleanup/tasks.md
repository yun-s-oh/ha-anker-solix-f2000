## 1. Core Implementation

- [x] 1.1 Guard AC Sockets Shutdown Timer: Implement a short-circuit guard in `custom_components/anker_solix_f2000/select.py` under `async_select_option` for `"ac_outlet_timer"` to return immediately if the requested option matches the current option.
- [x] 1.2 Guard 12V Car Port Shutdown Timer: Implement a short-circuit guard in `custom_components/anker_solix_f2000/select.py` under `async_select_option` for `"dc_12v_port1_timer"` to return immediately if the requested option matches the current option.

## 2. Documentation Refactoring

- [x] 2.1 Update tests/README.md: Add the raw telemetry `--raw` flag detail and detailed offline mock pytest coverage information from the root README to consolidate all testing details in one place.
- [x] 2.2 Refactor Root README.md: Remove the snarky warning sentence, professionally rephrase the 12-hour inactivity warning to include battery drain reactivation, and replace the large redundant testing setup instructions with a concise overview that links to `tests/README.md`.
- [x] 2.3 Update agent-guidelines.md: Refactor the file tree layout under the repository structure section to accurately represent all current `validate_*.py` and exploratory testing scripts.

## 3. Verification & Quality Control

- [x] 3.1 Run OpenSpec Code Validation: Execute OpenSpec syntax, formatting, and PEP 8 linter rules to verify code quality compliance.
- [x] 3.2 Run Pytest Offline Suite: Run the offline unit tests using `pytest` inside the testing before committing.
