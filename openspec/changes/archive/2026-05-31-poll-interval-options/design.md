## Context

Refining the active telemetry polling and reconnection ceiling retry intervals to improve stability,
reduce Bluetooth congestion, and provide highly flexible user control during setup.

## Goals / Non-Goals

**Goals:**
- Scale the active polling rate options to a range of 5s to 300s (defaulting to 30s).
- Scale the maximum retry reconnection interval to a range of 30s to 600s (defaulting to 30s).
- Enforce validation: `max_retry_interval` must be greater than or equal to `poll_interval`.
- Inject polling options directly into the auto-discovery flow step in `config_flow.py`.

**Non-Goals:**
- Modifying underlying Bleak connection or read logic.
- Dynamically varying the polling rate based on battery state.

## Decisions

### Decision 1: Default updates and range boundaries in const.py
- **Decision**: Update `const.py` to define the new default active polling interval as 30 seconds
  and establish boundary constants:
  - `CONF_POLL_INTERVAL_DEFAULT = 30`
  - `CONF_POLL_INTERVAL_MIN = 5`
  - `CONF_POLL_INTERVAL_MAX = 300`
  - `CONF_RETRY_INTERVAL_DEFAULT = 30`
  - `CONF_RETRY_INTERVAL_MIN = 30`
  - `CONF_RETRY_INTERVAL_MAX = 600`
- **Rationale**: Clean encapsulation of boundaries as named constants prevents magic numbers.

### Decision 2: Option Validation and Schema sharing in config_flow.py
- **Decision**: Build a common schema generator function for setup flows and options flow. Validate
  submitted options inside `config_flow.py`.
- **Validation rule**:
  ```python
  if user_input[CONF_MAX_RETRY_INTERVAL] < user_input[CONF_POLL_INTERVAL]:
      errors["base"] = "retry_interval_too_low"
  ```
- **Rationale**: Ensures the form cannot be submitted with invalid parameters, preventing runtime loops.

### Decision 3: Discovery Setup Flow Options Injection
- **Decision**: In `config_flow.py`, display the setup form with the shared schema during the discovery
  confirmation step (`async_step_bluetooth` confirmation), allowing the user to customize intervals
  immediately before integration registration.
- **Rationale**: Removes the requirement of post-setup customization for auto-discovered peripherals.

## Risks / Trade-offs

- **[Risk] High polling interval (e.g. 300s) causing disconnects**:
  - *Mitigation*: The keep-awake commands are run before polling. If the interval is long, the device
    might enter low-power sleep if keep-awake is not sent frequently enough. The coordinator should
    verify that a minimal background heartbeat keeps the connection active regardless of the slow
    telemetry polling rate.
