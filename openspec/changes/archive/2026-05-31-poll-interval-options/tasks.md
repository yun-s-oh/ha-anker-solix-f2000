## 1. Constants & Schema Configuration

- [x] 1.1 Update `const.py` to define the new `DEFAULT_POLL_INTERVAL = 30` and bounds constants
- [x] 1.2 Update schema creation functions to use the new bounds for poll and retry intervals

## 2. Config Flow & Validation Implementation

- [x] 2.1 Update discovery flow (`async_step_bluetooth`) in `config_flow.py` to prompt for intervals
- [x] 2.2 Implement form validation to enforce `max_retry_interval >= poll_interval` in config flows
- [x] 2.3 Ensure error message `retry_interval_too_low` is defined in translation strings (`strings.json`)

## 3. Verification & Testing

- [x] 3.1 Run Python compile syntax check on all modified files
- [x] 3.2 Run flake8 validation to ensure PEP 8 and 100-character line length compliance
- [x] 3.3 Verify existing unit tests run and pass successfully
- [x] 3.4 Restart Home Assistant and verify auto-discovery options flow validation is functional
