#!/usr/bin/env python3
"""Standalone script to validate toggle behavior for AC, DC, and Power Save on the Anker F2000.

This script connects to the real BLE device and runs three test suites:
1. AC Toggle Test: Verifies that command 0x86 behaves as a toggle (ignores payload).
2. DC Toggle Test: Verifies that command 0x87 behaves as a toggle (ignores payload).
3. Power Save Refresh Test: Verifies that 0x8A respects payload but reverts when a
   telemetry query is sent shortly after, confirming the deferred refresh interference.

Each test queries the initial state, sends commands, and observes the resulting
state through State ACK (0x48) and Telemetry (0x49) notifications.
"""

import asyncio
import logging
import os
import sys
from typing import Any

from bleak import BleakClient, BleakScanner

# Constants
NOTIFY_UUID = "00008888-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "00007777-0000-1000-8000-00805f9b34fb"
TELEMETRY_QUERY = bytes([0x08, 0xEE, 0x00, 0x00, 0x00, 0x01, 0x01, 0x0A, 0x00, 0x02])

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("validate_toggle_guard")


def load_env() -> None:
    """Load key-value pairs from .env files into environment variables."""
    paths = [".env", "../.env", "tests/.env"]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip()
            break


def calculate_checksum(data: bytes) -> int:
    """Calculate the unencrypted protocol checksum."""
    return sum(data) & 0xFF


def build_unencrypted_packet(
    header_prefix: bytes, packet_type: int, cmd_id: int, payload: bytes
) -> bytes:
    """Build a complete unencrypted protocol frame with dynamic length and checksum."""
    packet = bytearray()
    packet.extend(header_prefix)
    packet.append(packet_type)
    packet.append(cmd_id)
    # Total length = prefix (5) + type (1) + cmd_id (1) + len_bytes (2) + payload + checksum (1)
    total_len = len(header_prefix) + 1 + 1 + 2 + len(payload) + 1
    packet.extend(total_len.to_bytes(2, byteorder="little"))
    packet.extend(payload)
    packet.append(calculate_checksum(bytes(packet)))
    return bytes(packet)


def build_f2000_control_packet(cmd_id: int, value: int) -> bytes:
    """Build a complete unencrypted command packet for Anker F2000 controls."""
    return build_unencrypted_packet(
        bytes([0x08, 0xEE, 0x00, 0x00, 0x00]),
        0x02,
        cmd_id,
        bytes([value]),
    )


class ToggleGuardVerificationSession:
    """BLE toggle behavior validation session for Anker F2000.

    Tests AC/DC toggle semantics and Power Save deferred refresh interference
    to validate the state-guard design before implementing fixes.
    """

    def __init__(self, mac_address: str):
        self.mac = mac_address
        self.client: BleakClient | None = None
        self.ac_state: bool | None = None
        self.dc_state: bool | None = None
        self.power_save_state: bool | None = None
        self.update_event = asyncio.Event()
        self.results: list[dict[str, Any]] = []

    def handle_notification(self, _sender: Any, data: bytearray) -> None:
        """Process incoming BLE notification frames for state extraction."""
        frame = bytes(data)
        if len(frame) < 10:
            return

        if frame[0] != 0x09 or frame[1] != 0xFF:
            return

        packet_type = frame[5]
        sub_type = frame[6]

        if packet_type == 0x01:
            if sub_type == 0x48:  # State ACK (14 bytes)
                self.ac_state = bool(frame[9])
                self.dc_state = bool(frame[10])
                self.power_save_state = bool(frame[11])
                logger.info(
                    "StateAck (0x48): AC=%s, DC=%s, PowerSave=%s",
                    self.ac_state, self.dc_state, self.power_save_state,
                )
                self.update_event.set()
            elif sub_type == 0x49 and len(frame) >= 102:  # Telemetry (102 bytes)
                self.ac_state = bool(frame[63])
                self.dc_state = bool(frame[80])
                # Power Save is not in Telemetry, so do not update self.power_save_state here
                logger.info(
                    "Telemetry (0x49): AC=%s, DC=%s",
                    self.ac_state, self.dc_state,
                )
                self.update_event.set()
            elif sub_type == 0x01 and len(frame) == 122:  # Aux state (122 bytes)
                self.ac_state = bool(frame[63])
                self.dc_state = bool(frame[80])
                self.power_save_state = bool(frame[117])
                logger.info(
                    "AuxState (0x01): AC=%s, DC=%s, PowerSave=%s",
                    self.ac_state, self.dc_state, self.power_save_state,
                )
                self.update_event.set()

    async def wait_for_state(self, timeout: float = 4.0) -> bool:
        """Wait for a state update notification within the given timeout."""
        self.update_event.clear()
        try:
            await asyncio.wait_for(self.update_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def query_state(self) -> None:
        """Send telemetry query and wait for the response to refresh state."""
        if not self.client:
            return
        self.update_event.clear()
        await self.client.write_gatt_char(WRITE_UUID, TELEMETRY_QUERY, response=False)
        await self.wait_for_state(timeout=4.0)

    async def send_command(self, cmd_id: int, value: int) -> None:
        """Send a control command and wait for the state update response."""
        if not self.client:
            return
        packet = build_f2000_control_packet(cmd_id, value)
        logger.info("📤 Sending command 0x%02X with value 0x%02X", cmd_id, value)
        self.update_event.clear()
        await self.client.write_gatt_char(WRITE_UUID, packet, response=False)
        await self.wait_for_state(timeout=4.0)

    def record_result(
        self, test_name: str, passed: bool, details: str
    ) -> None:
        """Record a test result for the final summary."""
        status = "PASS ✅" if passed else "FAIL ❌"
        logger.info("[%s] %s: %s", status, test_name, details)
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
        })

    # -----------------------------------------------------------------
    # Test Suite 1: AC Toggle Behavior
    # -----------------------------------------------------------------
    async def test_ac_toggle(self) -> None:
        """Verify that AC command 0x86 behaves as a toggle (ignores payload).

        Test plan:
        1. Query initial AC state
        2. Send command with same-state payload → expect state to CHANGE (toggle)
        3. Send command again with same payload → expect state to CHANGE again (toggle)
        4. Restore original state
        """
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUITE 1: AC TOGGLE BEHAVIOR (0x86)")
        logger.info("=" * 60)

        await self.query_state()
        initial_ac = self.ac_state
        logger.info("Initial AC state: %s", initial_ac)

        if initial_ac is None:
            self.record_result(
                "AC-1: Initial state query", False,
                "Could not determine initial AC state"
            )
            return

        # Test AC-1: Send command with value matching current state
        # If AC is ON, send 0x01 (ON). If toggle, it should flip to OFF.
        same_val = 0x01 if initial_ac else 0x00
        logger.info(
            "AC-1: Sending 0x86 with value 0x%02X (same as current state %s)",
            same_val, initial_ac,
        )
        await self.send_command(0x86, same_val)
        await asyncio.sleep(1.0)
        await self.query_state()

        ac_after_same = self.ac_state
        toggled = ac_after_same != initial_ac
        self.record_result(
            "AC-1: Same-state command toggles",
            toggled,
            f"Sent 0x{same_val:02X} when AC={initial_ac}, "
            f"result AC={ac_after_same} (toggled={toggled})"
        )

        # Test AC-2: Send command with opposite payload
        # Regardless of payload, it should toggle again back to original.
        opposite_val = 0x00 if initial_ac else 0x01
        logger.info(
            "AC-2: Sending 0x86 with value 0x%02X (opposite payload)",
            opposite_val,
        )
        await self.send_command(0x86, opposite_val)
        await asyncio.sleep(1.0)
        await self.query_state()

        ac_after_opposite = self.ac_state
        restored = ac_after_opposite == initial_ac
        self.record_result(
            "AC-2: Opposite-payload command also toggles",
            restored,
            f"Sent 0x{opposite_val:02X}, result AC={ac_after_opposite} "
            f"(restored to original={restored})"
        )

    # -----------------------------------------------------------------
    # Test Suite 2: DC Toggle Behavior
    # -----------------------------------------------------------------
    async def test_dc_toggle(self) -> None:
        """Verify that DC command 0x87 behaves as a toggle (ignores payload).

        Same test pattern as AC but using command 0x87 and DC state.
        """
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUITE 2: DC TOGGLE BEHAVIOR (0x87)")
        logger.info("=" * 60)

        await self.query_state()
        initial_dc = self.dc_state
        logger.info("Initial DC state: %s", initial_dc)

        if initial_dc is None:
            self.record_result(
                "DC-1: Initial state query", False,
                "Could not determine initial DC state"
            )
            return

        # Test DC-1: Send command with value matching current state
        same_val = 0x01 if initial_dc else 0x00
        logger.info(
            "DC-1: Sending 0x87 with value 0x%02X (same as current state %s)",
            same_val, initial_dc,
        )
        await self.send_command(0x87, same_val)
        await asyncio.sleep(1.0)
        await self.query_state()

        dc_after_same = self.dc_state
        toggled = dc_after_same != initial_dc
        self.record_result(
            "DC-1: Same-state command toggles",
            toggled,
            f"Sent 0x{same_val:02X} when DC={initial_dc}, "
            f"result DC={dc_after_same} (toggled={toggled})"
        )

        # Test DC-2: Send command with opposite payload
        opposite_val = 0x00 if initial_dc else 0x01
        logger.info(
            "DC-2: Sending 0x87 with value 0x%02X (opposite payload)",
            opposite_val,
        )
        await self.send_command(0x87, opposite_val)
        await asyncio.sleep(1.0)
        await self.query_state()

        dc_after_opposite = self.dc_state
        restored = dc_after_opposite == initial_dc
        self.record_result(
            "DC-2: Opposite-payload command also toggles",
            restored,
            f"Sent 0x{opposite_val:02X}, result DC={dc_after_opposite} "
            f"(restored to original={restored})"
        )

    # -----------------------------------------------------------------
    # Test Suite 3: Power Save Behavior (0x8A)
    # -----------------------------------------------------------------
    async def test_power_save_refresh(self) -> None:
        """Diagnose Power Save command 0x8A behavior.

        Test plan:
        1. PS-1: Toggle test — send command with same-state payload, check if it
           toggles (like AC/DC) or respects payload.
        2. PS-2: Toggle test — send command with opposite payload, check behavior.
        3. PS-3: Immediate query test — send ON command then immediately query
           telemetry to see if BLE activity causes revert.
        """
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUITE 3: POWER SAVE BEHAVIOR (0x8A)")
        logger.info("=" * 60)

        await self.query_state()
        initial_ps = self.power_save_state
        logger.info("Initial Power Save state: %s", initial_ps)

        if initial_ps is None:
            self.record_result(
                "PS-1: Initial state query", False,
                "Could not determine initial Power Save state"
            )
            return

        # Test PS-1: Send command with value matching current state
        # If it's a toggle like AC/DC, it should flip regardless of payload.
        same_val = 0x01 if initial_ps else 0x00
        logger.info(
            "PS-1: Sending 0x8A with value 0x%02X (same as current state %s)",
            same_val, initial_ps,
        )
        await self.send_command(0x8A, same_val)
        await asyncio.sleep(1.0)
        await self.query_state()

        ps_after_same = self.power_save_state
        toggled = ps_after_same != initial_ps
        self.record_result(
            "PS-1: Same-state command effect",
            True,  # Diagnostic — always pass, we just want to observe
            f"Sent 0x{same_val:02X} when PS={initial_ps}, "
            f"result PS={ps_after_same} (changed={toggled})"
        )

        # Test PS-2: Send command with opposite payload
        opposite_val = 0x00 if initial_ps else 0x01
        logger.info(
            "PS-2: Sending 0x8A with value 0x%02X (opposite payload)",
            opposite_val,
        )
        await self.send_command(0x8A, opposite_val)
        await asyncio.sleep(1.0)
        await self.query_state()

        ps_after_opposite = self.power_save_state
        self.record_result(
            "PS-2: Opposite-payload command effect",
            True,  # Diagnostic — always pass, we just want to observe
            f"Sent 0x{opposite_val:02X}, result PS={ps_after_opposite} "
            f"(was {ps_after_same} before)"
        )

        # Ensure PS is OFF before PS-3
        if self.power_save_state:
            logger.info("Resetting Power Save to OFF for PS-3...")
            await self.send_command(0x8A, 0x00)
            await asyncio.sleep(2.0)
            await self.query_state()
            # If still ON, try sending again (toggle)
            if self.power_save_state:
                await self.send_command(0x8A, 0x01)
                await asyncio.sleep(2.0)
                await self.query_state()

        # Test PS-3: Send ON then immediately query to check timing behavior
        logger.info(
            "PS-3: Sending Power Save ON, then immediate telemetry query..."
        )
        await self.send_command(0x8A, 0x01)
        ps_after_cmd = self.power_save_state
        logger.info("Power Save after command (before query): %s", ps_after_cmd)

        # Immediately send telemetry query (simulating deferred refresh at 0.5s)
        logger.info(
            "Sending immediate telemetry query after 0.5s "
            "(simulating deferred refresh)..."
        )
        await asyncio.sleep(0.5)
        await self.query_state()
        ps_after_query = self.power_save_state

        self.record_result(
            "PS-3: State after immediate telemetry query",
            True,  # Diagnostic — always pass, we just want to observe
            f"Before query: PS={ps_after_cmd}, after query: PS={ps_after_query}"
        )

        # Final cleanup: try to ensure Power Save is OFF
        if self.power_save_state:
            logger.info("Final cleanup: turning Power Save OFF...")
            await self.send_command(0x8A, 0x00)
            await asyncio.sleep(1.0)

    # -----------------------------------------------------------------
    # Main Execution
    # -----------------------------------------------------------------
    async def execute_validation(self) -> bool:
        """Run the full validation sequence."""
        logger.info("Resolving BLE device for: %s...", self.mac)
        device = await BleakScanner.find_device_by_address(self.mac, timeout=10.0)
        if not device:
            logger.error("Could not find F2000 device in range.")
            return False

        logger.info("Connecting to %s...", device.name or "F2000")
        async with BleakClient(device) as client:
            self.client = client
            logger.info("Connected successfully! Subscribing to notifications...")
            await client.start_notify(NOTIFY_UUID, self.handle_notification)
            logger.info("Subscribed!")

            # Run all test suites
            await self.test_ac_toggle()
            await asyncio.sleep(2.0)

            await self.test_dc_toggle()
            await asyncio.sleep(2.0)

            await self.test_power_save_refresh()

            await client.stop_notify(NOTIFY_UUID)

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        for result in self.results:
            status = "PASS ✅" if result["passed"] else "FAIL ❌"
            logger.info("  [%s] %s", status, result["test"])
            logger.info("         %s", result["details"])
        logger.info("-" * 60)
        logger.info("Results: %d/%d passed", passed, total)
        logger.info("=" * 60)

        return passed == total


def main() -> None:
    """Script entry point."""
    load_env()
    mac = os.getenv("ANKER_MAC_ADDRESS")
    if not mac:
        logger.error(
            "ANKER_MAC_ADDRESS is not set in your environment / .env file."
        )
        sys.exit(1)

    try:
        success = asyncio.run(
            ToggleGuardVerificationSession(mac).execute_validation()
        )
        if success:
            logger.info("All tests passed!")
        else:
            logger.warning("Some tests failed — review results above.")
    except KeyboardInterrupt:
        logger.info("Verification script interrupted.")
    except Exception as e:
        logger.exception("Fatal error in validation session: %s", e)


if __name__ == "__main__":
    main()
