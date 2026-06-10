## Context

The Anker F2000's BLE switch controls have two distinct behavioral issues:

1. **AC (`0x86`) and DC (`0x87`) are toggles** — the device flips the current state regardless of the payload byte. The current `switch.py` sends `0x01` for ON and `0x00` for OFF, but the device ignores the payload. This causes `turn_off` to toggle the device ON when it's already OFF.

2. **Power Save (`0x8A`) respects the payload** (ON/OFF) but auto-reverts to OFF within ~1 second. The likely cause is the integration's `_async_deferred_refresh()` method, which sends a `TELEMETRY_QUERY` to the device 0.5s after every command. This BLE write activity appears to cause the F2000 to exit Power Save mode. The regular polling interval (default 30s) also contributes, but the deferred refresh is the immediate trigger.

The optimistic state update in `coordinator.py` is also incorrect for AC/DC — it uses `bool(payload[0])` which doesn't reflect toggle behavior.

## Goals / Non-Goals

**Goals:**
- Fix AC/DC switches with state-guarded toggle logic so ON/OFF commands are idempotent.
- Fix Power Save by suppressing the deferred telemetry refresh after Power Save ON commands.
- Fix optimistic state updates in coordinator for AC/DC to invert current state.
- Add a hardware validation test script to verify all three fixes.
- Update protocol documentation to accurately describe toggle vs. explicit command behavior.

**Non-Goals:**
- Changing the BLE packet structure or discovering new command IDs.
- Modifying select, number, or sensor entities (unaffected).
- Disabling polling entirely (needed for keep-awake and sensor freshness).

## Decisions

### 1. State-Guarded Toggle for AC/DC in `switch.py`

Before sending an AC or DC toggle command, check `self.is_on`. If the current state already matches the desired state, skip the command.

```python
async def async_turn_on(self, **kwargs: Any) -> None:
    """Turn the control switch ON."""
    if self._is_toggle_command() and self.is_on:
        _LOGGER.debug("Switch %s already ON, skipping toggle", self.entity_description.key)
        return
    cmd_id = self._get_command_id()
    await self.coordinator.async_send_control_command(cmd_id, bytes([0x01]))

async def async_turn_off(self, **kwargs: Any) -> None:
    """Turn the control switch OFF."""
    if self._is_toggle_command() and self.is_on is False:
        _LOGGER.debug("Switch %s already OFF, skipping toggle", self.entity_description.key)
        return
    cmd_id = self._get_command_id()
    await self.coordinator.async_send_control_command(cmd_id, bytes([0x00]))

def _is_toggle_command(self) -> bool:
    """Return True if this switch uses toggle protocol (AC/DC only)."""
    return self.entity_description.key in ("ac_outlet_on", "twelve_volt_on")
```

**Why `is_on is False` instead of `not self.is_on`?** Because `self.is_on` can be `None` (no data yet). We should still send the command when state is unknown. `is False` only skips when we have confirmed OFF state.

**Why not guard Power Save?** Power Save respects the payload — sending `0x01` always means ON. The guard would mask the real problem (deferred refresh interference) instead of fixing it.

**Why keep different payload values (0x01 vs 0x00)?** Although the F2000 ignores the payload for AC/DC toggles, sending semantically correct values preserves forward compatibility and makes BLE debug logs readable.

### 2. Toggle-Aware Optimistic State Updates for AC/DC

For AC and DC commands, the optimistic update must invert the current state instead of using the payload:

```python
if cmd_id == 0x86:
    self._state_data["ac_outlet_on"] = not self._state_data.get("ac_outlet_on", False)
elif cmd_id == 0x87:
    self._state_data["twelve_volt_on"] = not self._state_data.get("twelve_volt_on", False)
```

Power Save retains payload-based optimistic update (`bool(payload[0])`) since it respects the payload.

### 3. Suppress Deferred Refresh After Power Save ON

The `_async_deferred_refresh()` sends a `TELEMETRY_QUERY` 0.5s after every command. This BLE activity likely causes the F2000 to auto-exit Power Save mode. The fix:

- Pass `skip_refresh=True` from `switch.py` when sending Power Save ON.
- In `async_send_control_command`, conditionally skip scheduling the deferred refresh.

```python
async def async_send_control_command(
    self, cmd_id: int, payload: bytes, *, skip_refresh: bool = False
) -> bool:
    ...
    if not skip_refresh:
        self.hass.async_create_task(self._async_deferred_refresh())
    return True
```

In `switch.py`, Power Save ON passes `skip_refresh=True`:
```python
if self.entity_description.key == "power_save_on" and payload == bytes([0x01]):
    await self.coordinator.async_send_control_command(cmd_id, payload, skip_refresh=True)
else:
    await self.coordinator.async_send_control_command(cmd_id, payload)
```

**Why only suppress for Power Save ON?** Power Save OFF doesn't need the suppression — the device is already exiting Power Save mode. Other commands (LED, screen, timers) need the refresh to confirm state.

**Alternative considered: Longer deferred refresh delay.** We could increase the 0.5s delay to 2-3s for Power Save. Rejected because the root cause is BLE activity waking the device, not timing — the next polling cycle would also cause a revert.

### 4. Hardware Validation Test Script

Create `tests/validate_toggle_guard.py` that:
1. Connects to the physical F2000 via BLE.
2. Tests AC toggle: sends command when already in same state → verifies no state change.
3. Tests DC toggle: same pattern.
4. Tests Power Save: sends ON, waits 3s WITHOUT sending telemetry query, then queries to check if it stayed ON. Also tests with an immediate query to confirm the revert behavior.

## Risks / Trade-offs

- **[Risk]**: Stale state causes incorrect AC/DC guard decision (e.g., someone physically presses the F2000 button between polls).
  - *Mitigation*: Periodic polling (30s) and BLE notification subscription keep state reasonably fresh. Worst case: user sends command again after next poll corrects state.

- **[Risk]**: Skipping deferred refresh for Power Save means the HA state relies on the optimistic update until the next regular poll cycle (up to 30s).
  - *Mitigation*: The optimistic update is correct for Power Save (payload-based). The next regular poll will reconcile. This is an acceptable trade-off to keep Power Save functional.

- **[Risk]**: Power Save revert may also be triggered by the regular polling interval (30s), not just the deferred refresh.
  - *Mitigation*: The test script will diagnose this. If regular polling also causes reverts, we may need to temporarily pause polling after a Power Save ON command — but this is a separate concern to address based on test results.

- **[Trade-off]**: Keeping Switch entity for AC/DC despite toggle hardware gives better HA UX (automations can say "turn on AC") but requires state guard complexity.
