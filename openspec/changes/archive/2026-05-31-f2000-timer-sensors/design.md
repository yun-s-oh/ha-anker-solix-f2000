## Context

The `ac_outlet_timer` is already fully decoded from unencrypted BLE telemetry packets in the
update coordinator, but has not yet been registered as a Home Assistant sensor entity.
Furthermore, the single 12V Car Port Remaining Timer currently has a redundant `" 1"` in its
display name, which should be removed.

## Goals / Non-Goals

**Goals:**
- Rename the existing `"12V Car Port 1 Timer Remaining"` sensor to `"12V Car Port Timer Remaining"`.
- Expose the `"ac_outlet_timer"` payload value as a standard `"AC Sockets Timer Remaining"` sensor.

**Non-Goals:**
- Modifying the underlying protocol parser or the BLE command-sending architecture.
- Changing entity keys in a way that breaks existing Home Assistant unique ID database maps.

## Decisions

### Decision 1: Expose `ac_outlet_timer` as a standard duration sensor
- **Options Considered**:
  - Option A: Expose as a diagnostic entity.
  - Option B: Expose as a standard first-class numeric sensor with `SensorDeviceClass.DURATION`.
- **Decision**: Option B.
- **Rationale**: Output shutdown timers are high-value telemetry metrics for home automation and
  dashboards, similar to the battery remaining minutes.

### Decision 2: Modify display name while preserving unique entity keys
- **Options Considered**:
  - Option A: Rename both the database key and display name.
  - Option B: Rename only the display `name` property while keeping `key="dc_12v_port1_timer"`.
- **Decision**: Option B.
- **Rationale**: Keeping the key ensures we do not break any existing unique ID mappings or
  entity database records for existing integration users, while cleanly updating the UI display.

## Risks / Trade-offs

- **[Risk] Entity ID change in HA**: Modifying the display name might cause the auto-generated entity
  ID to change on fresh setups (from `dc_12v_port1_timer` to `dc_12v_port_timer`), but using the
  same unique ID prevents database issues.
  - *Mitigation*: The unique ID remains anchored to the MAC address and `dc_12v_port1_timer` key,
    ensuring continuity.
