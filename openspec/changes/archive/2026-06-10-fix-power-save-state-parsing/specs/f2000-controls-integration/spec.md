## MODIFIED Requirements

### Requirement: Switch Controls
The integration SHALL expose switch entities to control `AC Output`, `DC Output`, and `Power Saving Mode` on the Anker F2000. The integration SHALL update the state of the Power Saving Mode switch entity based on the `power_save_on` state received via the 14-byte `0x48` State ACK packet (byte register `11`) and the 122-byte `0x01` Auxiliary State packet (byte register `117`), and SHALL NOT query or update the Power Saving Mode state from the 102-byte `0x49` Telemetry packet.

#### Scenario: Turn AC Output ON
- **WHEN** the user toggles the AC Output switch entity to ON in Home Assistant
- **THEN** the integration formats and sends the corresponding unencrypted BLE frame to the F2000.

#### Scenario: Update Power Saving Mode switch state
- **WHEN** HASS receives a 122-byte Auxiliary State packet with Power Save set to ON at byte register 117
- **THEN** HASS updates the Power Saving Mode switch entity state to ON.
