## MODIFIED Requirements

### Requirement: Structured Packet Telemetry Parsing
The system SHALL parse 102-byte telemetry packets (`0x49` subtype) and 14-byte state packets (`0x48` subtype) by validating the `09 ff 00 00 01` header and decoding individual byte registers. In the `0x49` telemetry packet, the system SHALL decode `twelve_volt_on` from byte register `80` and `power_save_on` from byte register `82`.

#### Scenario: Validating and decoding a telemetry frame
- **WHEN** a notification frame starting with `09 ff 00 00 01` and subtype `0x49` is received
- **THEN** the parser successfully extracts battery, temperature, solar input power, AC outlet power, twelve_volt_on master state, power_save_on state, and serial numbers.
