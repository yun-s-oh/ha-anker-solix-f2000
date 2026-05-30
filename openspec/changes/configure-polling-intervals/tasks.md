## 1. Constants and Shared Schema Configurations

- [x] 1.1 Update `const.py` to change default polling to 5 seconds and maximum reconnection back-off to 30 seconds
- [x] 1.2 Define shared configuration keys `CONF_POLL_INTERVAL` and `CONF_MAX_RETRY_INTERVAL` in `const.py`


## 2. Config Flow and Options Flow Handler

- [x] 2.1 Implement `AnkerSolixOptionsFlowHandler` in `config_flow.py` and register it on the config flow class
- [x] 2.2 Define the options flow user schema using HASS validation helpers with exact interval bounds (5s-30s and 30s-300s)
- [x] 2.3 Add option translation strings to `strings.json` to render descriptive form labels in the HA settings UI


## 3. Dynamic Coordinator Rescheduling

- [x] 3.1 Update `__init__.py` to register the `async_update_options` update listener on active config entries
- [x] 3.2 Implement the options update handler to dynamically update coordinator intervals without restarting the entry
- [x] 3.3 Modify `coordinator.py` to read poll intervals and max retries from `config_entry.options` (with updated defaults as fallback)
- [x] 3.4 Update the exponential back-off reconnection loop in `coordinator.py` to fetch updated max retries dynamically at runtime
- [x] 3.5 Raise `ConfigEntryNotReady` in `__init__.py` when BLE device is missing at startup




## 4. Branding and HACS Documentation

- [x] 4.1 Create the local `brand/` directory at `custom_components/anker_solix_f2000/brand/`
- [x] 4.2 Generate and save high-quality custom Anker Solix icons and logos (`icon.png`, `logo.png`, `dark_icon.png`, `dark_logo.png`) inside the `brand/` directory
- [x] 4.3 Revise `README.md` to document simple HACS custom repository integration procedures, using patterns inspired by the NeoVolt and Tuya integration documentation



## 5. Automated Testing and Verification

- [x] 5.1 Create mock test cases in `test_mock_telemetry.py` to verify dynamic rescheduling and options flow input validations
- [x] 5.2 Execute the comprehensive `pytest` test suite to assert zero regressions across all core entities
- [x] 5.3 Validate the integration codebase style using `flake8` and run syntax compilation checks

