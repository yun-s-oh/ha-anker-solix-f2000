## ADDED Requirements

### Requirement: Smart Battery Fallback Logic
The primary battery sensor (`total_pct` / `"Battery"`) SHALL return the accurate internal battery cell percentage
(`internal_pct`) if no external battery expansion is physically connected.

#### Scenario: Single unit battery updates
- **WHEN** no external expansion battery is connected (`external_pct` is `None`)
- **THEN** the primary `"Battery"` entity returns the value of `"internal_pct"`.

#### Scenario: Expanded unit battery updates
- **WHEN** an external expansion battery is connected
- **THEN** the primary `"Battery"` entity returns the combined value of `"total_pct"`.

### Requirement: Car Port Master Icon
The `twelve_volt_on` switch entity ("12V Car Port Master") SHALL use the standard, working Material
Design Icon `"mdi:car-power-outlet"`.

#### Scenario: Retrieve entity icon
- **WHEN** the 12V Car Port Master switch is registered in Home Assistant
- **THEN** the entity uses `"mdi:car-power-outlet"` as its icon.

### Requirement: Safe Shutdown Timer Durations
The pre-generated dropdown options for the AC and DC Output Shutdown select entities SHALL be capped
at a maximum of 18 hours (64,800 seconds) to ensure that the duration fits safely inside a 2-byte
little-endian uint16 without causing integer overflow exceptions.

#### Scenario: Verify dropdown options limit
- **WHEN** the AC or DC shutdown select entity dropdown options are generated
- **THEN** the options list SHALL NOT contain any durations exceeding 18 hours, and the highest option is "18h".
