"""Bluetooth Data Update Coordinator for the Anker Solix F2000.

This coordinator manages a single persistent BLE connection to the unencrypted F2000 ports,
subscribes to characteristic notification updates, handles periodic active queries, and parsed
inbound telemetry packets to update Home Assistant state entities.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from enum import IntEnum
import logging
from typing import Any

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_MAX_RETRY_INTERVAL,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    HEADER_PREFIX,
    MAX_RETRY_INTERVAL,
    MIN_RETRY_INTERVAL,
    NOTIFY_UUID,
    TELEMETRY_QUERY,
    WRITE_UUID,
)

_LOGGER = logging.getLogger(__name__)


class BatteryState(IntEnum):
    """Charging and discharging states for the F2000 battery."""

    IDLE = 0
    DISCHARGING = 1
    CHARGING = 2


class LedState(IntEnum):
    """Operating states of the built-in LED utility light."""

    OFF = 0
    LOW = 1
    MID = 2
    HIGH = 3
    SOS = 4


def extract16(data: bytes, index: int) -> int:
    """Extract a 16-bit LE integer from a byte sequence at a given offset."""
    return int.from_bytes(data[index:index + 2], byteorder="little")


def parse_state_ack(data: bytes) -> dict[str, Any]:
    """Decode a 14-byte State ACK (0x48 subtype) packet."""
    try:
        led = LedState(data[12]).name if data[12] <= 4 else f"UNKNOWN({data[12]})"
    except ValueError:
        led = f"UNKNOWN({data[12]})"

    return {
        "ac_outlet_on": bool(data[9]),
        "twelve_volt_on": bool(data[10]),
        "power_save_on": bool(data[11]),
        "led_state": led,
    }


def parse_telemetry(data: bytes) -> dict[str, Any]:
    """Decode a 102-byte Main Telemetry (0x49 subtype) packet."""
    try:
        battery_state = BatteryState(data[68]).name
    except ValueError:
        battery_state = f"UNKNOWN({data[68]})"

    # Duration calculations
    hours_raw = data[17] / 10.0
    days_raw = data[18]
    total_minutes = int((days_raw * 24 + hours_raw) * 60)

    # Device serial extraction
    try:
        serial = data[85:101].decode("utf-8").rstrip("\x00")
    except (UnicodeDecodeError, IndexError):
        serial = "N/A"

    # Check if external expansion battery is physically connected (non-zero temp or percent)
    external_connected = data[71] != 0 or data[67] != 0
    external_pct = data[71] if external_connected else None
    external_temp = data[67] if external_connected else None

    return {
        "serial": serial,
        # Battery details
        "internal_pct": data[70],
        "external_pct": external_pct,
        "total_pct": data[72],
        "battery_state": battery_state,
        "battery_remaining_minutes": total_minutes,
        "internal_temp_c": data[66],
        "external_temp_c": external_temp,
        # Input power
        "ac_input_w": extract16(data, 19),
        "solar_input_w": extract16(data, 37),
        "total_input_w": extract16(data, 39),
        # Output power
        "ac_outlet_w": extract16(data, 21),
        "ac_outlet_on": bool(data[63]),
        "total_output_w": extract16(data, 41),
        # USB ports
        "usb_c1_on": bool(data[75]),
        "usb_c1_w": extract16(data, 23),
        "usb_c2_on": bool(data[76]),
        "usb_c2_w": extract16(data, 25),
        "usb_c3_on": bool(data[77]),
        "usb_c3_w": extract16(data, 27),
        "usb_a1_on": bool(data[78]),
        "usb_a1_w": extract16(data, 29),
        "usb_a2_on": bool(data[79]),
        "usb_a2_w": extract16(data, 31),
        # 12V DC ports
        "dc_12v_port1_on": bool(data[80]),
        "dc_12v_port1_w": extract16(data, 33),
        "dc_12v_port1_timer": extract16(data, 13),
        "ac_outlet_timer": extract16(data, 9),
        "dc_12v_port2_on": bool(data[81]),
        "dc_12v_port2_w": extract16(data, 35),
    }


def parse_aux_state(data: bytes) -> dict[str, Any]:
    """Decode a 122-byte Auxiliary State (0x01 subtype) packet."""
    return {
        "ac_recharging_power": extract16(data, 101),
        "screen_timeout": extract16(data, 105),
    }


class AnkerSolixBluetoothUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Resilient BLE coordinator for collecting telemetry from the F2000."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device: BLEDevice,
        device_name: str,
    ) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self.device = device
        self.device_name = device_name
        self._client: BleakClient | None = None
        self._connect_lock = asyncio.Lock()
        self._running = False
        self._retry_delay = MIN_RETRY_INTERVAL
        self._state_data: dict[str, Any] = {
            "ac_outlet_timer": 0,
            "dc_12v_port1_timer": 0,
            "led_state": "OFF",
            "screen_brightness": 1,
            "screen_timeout": 30,
            "ac_recharging_power": 500,
        }

        poll_interval = self.config_entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_name}",
            update_interval=timedelta(seconds=poll_interval),
        )

    async def async_update_options_handler(self) -> None:
        """Handle dynamic options updates from HASS configuration entry flow."""
        poll_interval = self.config_entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
        self.update_interval = timedelta(seconds=poll_interval)
        _LOGGER.info(
            "Dynamic poll interval updated to %d seconds. Rescheduling timer.", poll_interval
        )

    def _notification_handler(self, _sender: int, data: bytearray) -> None:
        """Handle incoming unencrypted BLE notification frames."""
        frame = bytes(data)
        if len(frame) < 10:
            return

        # Check unencrypted header signature: 09 ff
        if frame[0] != HEADER_PREFIX[0] or frame[1] != HEADER_PREFIX[1]:
            return

        packet_type = frame[5]
        sub_type = frame[6]

        if packet_type == 0x01:  # Telemetry / State notification
            if sub_type == 0x48:
                parsed = parse_state_ack(frame)
                self._state_data.update(parsed)
                self.async_set_updated_data(dict(self._state_data))
            elif sub_type == 0x49 and len(frame) >= 102:
                parsed = parse_telemetry(frame)
                self._state_data.update(parsed)
                self.async_set_updated_data(dict(self._state_data))
            elif sub_type == 0x01 and len(frame) == 122:
                parsed = parse_aux_state(frame)
                self._state_data.update(parsed)
                self.async_set_updated_data(dict(self._state_data))

    async def _async_connect(self) -> bool:
        """Establish a persistent BLE connection with the F2000."""
        async with self._connect_lock:
            if self._client and self._client.is_connected:
                return True

            _LOGGER.debug("Connecting to Anker F2000 BLE at %s", self.device.address)
            try:
                # Resolve fresh BLEDevice from the central HA Bluetooth subsystem
                ble_device = bluetooth.async_ble_device_from_address(
                    self.hass, self.device.address, connectable=True
                )
                if ble_device:
                    self.device = ble_device

                # establish_connection manages reconnection retries automatically
                self._client = await establish_connection(
                    BleakClient,
                    self.device,
                    self.device_name,
                    disconnected_callback=self._handle_disconnect,
                )
                _LOGGER.info("Successfully connected to Anker F2000 at %s", self.device.address)
                self._retry_delay = MIN_RETRY_INTERVAL

                # Subscribe to unencrypted notification stream
                await self._client.start_notify(
                    NOTIFY_UUID, self._notification_handler  # type: ignore[arg-type]
                )
                _LOGGER.debug("Subscribed to BLE notifications on UUID %s", NOTIFY_UUID)

                # Send initial active query immediately
                await self._async_write_query()
                return True

            except (BleakError, asyncio.TimeoutError) as err:
                _LOGGER.warning(
                    "BLE connection attempt to %s failed: %s. "
                    "The F2000 only supports a single BLE connection — "
                    "ensure the official Anker app is closed on all "
                    "phones before retrying.",
                    self.device.address,
                    err,
                )
                self._client = None
                return False

    def _handle_disconnect(self, client: BleakClient) -> None:
        """Handle unexpected BLE radio link disconnection."""
        _LOGGER.warning("Anker F2000 BLE link disconnected cleanly or dropped.")
        self._client = None
        if self._running:
            self.hass.async_create_task(self._async_reconnect_loop())

    async def _async_reconnect_loop(self) -> None:
        """Resilient background loop implementing exponential retry back-offs."""
        if self._connect_lock.locked():
            return

        _LOGGER.info("Starting exponential back-off reconnection loop...")
        while self._running and (not self._client or not self._client.is_connected):
            _LOGGER.debug("Retrying connection in %d seconds...", self._retry_delay)
            await asyncio.sleep(self._retry_delay)

            success = await self._async_connect()
            if success:
                break

            # Increase delay exponentially up to max back-off
            max_retry = self.config_entry.options.get(CONF_MAX_RETRY_INTERVAL, MAX_RETRY_INTERVAL)
            self._retry_delay = min(self._retry_delay * 2, max_retry)

    async def _async_write_query(self) -> None:
        """Write the unencrypted telemetry query to trigger a data stream update."""
        if not self._client or not self._client.is_connected:
            return

        try:
            await self._client.write_gatt_char(WRITE_UUID, TELEMETRY_QUERY, response=False)
            _LOGGER.debug("Sent active telemetry query: %s", TELEMETRY_QUERY.hex())
        except BleakError as err:
            _LOGGER.warning("Failed to write BLE query frame: %s", err)

    async def _async_update_data(self) -> dict[str, Any]:
        """Trigger active poll and return current telemetry state."""
        if not self._client or not self._client.is_connected:
            connected = await self._async_connect()
            if not connected:
                # Return current local data during transient dropouts
                return self._state_data

        # Prompt device to emit telemetry update
        await self._async_write_query()
        return self._state_data

    async def async_start(self) -> None:
        """Start the coordinator connection processes."""
        self._running = True
        await self._async_connect()

    async def async_stop(self) -> None:
        """Stop connection processes and cleanly disconnect BLE client."""
        self._running = False
        async with self._connect_lock:
            if self._client:
                if self._client.is_connected:
                    try:
                        await self._client.stop_notify(NOTIFY_UUID)
                    except BleakError as err:
                        _LOGGER.debug("Error stopping BLE notifications during shutdown: %s", err)
                    try:
                        await self._client.disconnect()
                    except BleakError as err:
                        _LOGGER.warning("Error during BLE client disconnect shutdown: %s", err)
                self._client = None

    async def async_send_control_command(self, cmd_id: int, payload: bytes) -> bool:
        """Send a control command to the F2000 and wait for its ACK."""
        if not self._client or not self._client.is_connected:
            _LOGGER.warning("Cannot send control command: BLE not connected")
            return False

        # Build unencrypted packet
        packet = bytearray()
        packet.extend(bytes([0x08, 0xEE, 0x00, 0x00, 0x00]))
        packet.append(0x02)  # PacketType: Command/Control
        packet.append(cmd_id)
        # Length: header (5) + type (1) + cmd_id (1) + len_bytes (2) + payload + checksum (1)
        total_len = 5 + 1 + 1 + 2 + len(payload) + 1
        packet.extend(total_len.to_bytes(2, byteorder="little"))
        packet.extend(payload)
        packet.append(sum(packet) & 0xFF)
        packet_bytes = bytes(packet)

        try:
            _LOGGER.info("Sending BLE command 0x%02X, payload %s", cmd_id, payload.hex())
            async with self._connect_lock:
                await self._client.write_gatt_char(WRITE_UUID, packet_bytes, response=False)

            # Optimistically update local state cache for instant UI feedback
            if cmd_id == 0x86:
                self._state_data["ac_outlet_on"] = bool(payload[0])
            elif cmd_id == 0x87:
                self._state_data["twelve_volt_on"] = bool(payload[0])
            elif cmd_id == 0x8A:
                self._state_data["power_save_on"] = bool(payload[0])
            elif cmd_id == 0x8B:
                try:
                    self._state_data["led_state"] = LedState(payload[0]).name
                except ValueError:
                    pass
            elif cmd_id == 0x88:
                self._state_data["screen_brightness"] = int(payload[0])
            elif cmd_id == 0x82:
                self._state_data["screen_timeout"] = int.from_bytes(payload, byteorder="little")
            elif cmd_id == 0x80:
                self._state_data["ac_recharging_power"] = int.from_bytes(
                    payload, byteorder="little"
                )
            elif cmd_id == 0x02:
                self._state_data["ac_outlet_timer"] = int.from_bytes(
                    payload, byteorder="little"
                )
            elif cmd_id == 0x03:
                self._state_data["dc_12v_port1_timer"] = int.from_bytes(
                    payload, byteorder="little"
                )

            self.async_set_updated_data(dict(self._state_data))

            # Schedule a deferred active query refresh to fetch official telemetry 0.5s later
            self.hass.async_create_task(self._async_deferred_refresh())
            return True
        except BleakError as err:
            _LOGGER.error("Failed to send BLE command 0x%02X: %s", cmd_id, err)
            return False

    async def _async_deferred_refresh(self) -> None:
        """Query telemetry after a 0.5s delay to refresh all states cleanly."""
        await asyncio.sleep(0.5)
        await self._async_write_query()
