## MODIFIED Requirements

### Requirement: Structured Packet Telemetry Parsing
The system SHALL parse 102-byte telemetry packets (`0x49` subtype), 14-byte state packets (`0x48` subtype), and 122-byte auxiliary state packets (`0x01` subtype) by validating the `09 ff 00 00 01` header and decoding individual byte registers. In the `0x49` telemetry packet, the system SHALL decode `twelve_volt_on` from byte register `80` (but shall NOT decode `power_save_on` from byte register `82`), `ac_outlet_timer` from byte registers `9-10`, and `dc_12v_port1_timer` from byte registers `13-14`. In the 122-byte `0x01` auxiliary state packet, the system SHALL decode `power_save_on` from byte register `117`.

#### Scenario: Validating and decoding a telemetry frame
- **WHEN** a notification frame starting with `09 ff 00 00 01` and subtype `0x49` is received
- **THEN** the parser successfully extracts battery, temperature, solar input power, AC outlet power, twelve_volt_on master state, ac_outlet_timer, dc_12v_port1_timer, and serial numbers, but does not extract power_save_on state.

#### Scenario: Validating and decoding an auxiliary state frame
- **WHEN** a notification frame starting with `09 ff 00 00 01`, subtype `0x01`, and length 122 is received
- **THEN** the parser successfully extracts ac_recharging_power, screen_timeout, and power_save_on state (from byte register 117).
