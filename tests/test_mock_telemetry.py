#!/usr/bin/env python3
"""Pytest unit test suite for verifying the F2000 BLE protocol parser and mock generator.

This test suite complies with the Python Code Style Guide (PEP 8, Type Hints, 100 char limit).
"""


from mock_f2000 import (
    calculate_checksum,
    generate_state_ack,
    generate_telemetry,
    parse_packet,
)


def test_calculate_checksum() -> None:
    """Verify that the unencrypted protocol checksum is computed correctly."""
    # Simple packet: 09 ff 00 00 01
    data = bytes([0x09, 0xFF, 0x00, 0x00, 0x01])
    # Sum: 0x09 + 0xFF + 0x00 + 0x00 + 0x01 = 0x109
    # Checksum: 0x109 & 0xFF = 0x09
    assert calculate_checksum(data) == 0x09


def test_generate_and_parse_state_ack() -> None:
    """Verify mock State Ack (0x48) generation, checksum calculation, and parsing."""
    raw_packet = generate_state_ack(
        ac_sockets_on=True,
        dc_on=False,
        power_save=True,
        led_state=3,
    )

    # 14 bytes total
    assert len(raw_packet) == 14

    # Header check
    assert raw_packet[0:5] == b"\x09\xff\x00\x00\x01"
    assert raw_packet[5] == 0x01  # Telemetry type
    assert raw_packet[6] == 0x48  # State Ack subtype

    # Parse and assert fields
    parsed = parse_packet(raw_packet)
    assert parsed is not None
    assert parsed["type"] == "state_ack"
    assert parsed["ac_outlet_on"] is True
    assert parsed["twelve_volt_on"] is False
    assert parsed["power_save_on"] is True
    assert parsed["led_state"] == 3


def test_generate_and_parse_telemetry() -> None:
    """Verify mock Telemetry (0x49) generation and scaling offset parsing."""
    raw_packet = generate_telemetry(
        battery_pct=85,
        ac_in_w=450,
        ac_out_w=120,
        temp_c=22,
        serial="AZV25N0F30400256",
        twelve_volt_on=True,
        power_save_on=True,
    )

    # 102 bytes total
    assert len(raw_packet) == 102

    # Parse and assert fields
    parsed = parse_packet(raw_packet)
    assert parsed is not None
    assert parsed["type"] == "telemetry"
    assert parsed["battery"]["internal_pct"] == 85
    assert parsed["battery"]["total_pct"] == 85
    assert parsed["battery"]["temp_c"] == 22
    assert parsed["power_input"]["ac_input_w"] == 450
    assert parsed["power_output"]["ac_outlet_w"] == 120
    assert parsed["power_output"]["ac_outlet_on"] is True
    assert parsed["power_output"]["twelve_volt_on"] is True
    assert parsed["power_output"]["power_save_on"] is True
    assert parsed["device"]["serial"] == "AZV25N0F30400256"


def test_checksum_validation_rejection() -> None:
    """Verify that the parser detects and handles invalid packet checksums gracefully."""
    raw_packet = bytearray(
        generate_telemetry(
            battery_pct=50,
            ac_in_w=0,
            ac_out_w=0,
            temp_c=25,
            serial="AZV25N0F30400256",
        )
    )

    # Tamper with the checksum byte at the end
    raw_packet[-1] = (raw_packet[-1] + 1) % 256

    # Parse and assert that it returns a checksum error dict
    parsed = parse_packet(bytes(raw_packet))
    assert parsed is not None
    assert parsed["type"] == "checksum_error"


def test_coordinator_dynamic_rescheduling() -> None:
    """Verify that coordinator dynamically reschedules update interval when options change."""
    import sys
    from unittest.mock import MagicMock
    from datetime import timedelta
    import asyncio
    import os

    # Stub/mock the entire homeassistant package and parent classes before importing coordinator
    mock_hass = MagicMock()
    mock_const = MagicMock()
    mock_const.Platform = MagicMock()

    class DummyDataUpdateCoordinator:
        def __init__(self, hass, logger, *, name, update_interval=None) -> None:
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval

        @classmethod
        def __class_getitem__(cls, item):
            return cls

    sys.modules["homeassistant"] = mock_hass
    sys.modules["homeassistant.components"] = mock_hass
    sys.modules["homeassistant.components.bluetooth"] = mock_hass
    sys.modules["homeassistant.config_entries"] = mock_hass
    sys.modules["homeassistant.const"] = mock_const
    sys.modules["homeassistant.core"] = mock_hass
    sys.modules["homeassistant.exceptions"] = mock_hass
    sys.modules["homeassistant.helpers"] = mock_hass
    sys.modules["homeassistant.helpers.update_coordinator"] = mock_hass
    mock_up_coord = sys.modules["homeassistant.helpers.update_coordinator"]
    mock_up_coord.DataUpdateCoordinator = DummyDataUpdateCoordinator

    # Ensure custom_components path is importable
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

    from custom_components.anker_solix_f2000.coordinator import (
        AnkerSolixBluetoothUpdateCoordinator,
    )
    from custom_components.anker_solix_f2000.const import (
        CONF_POLL_INTERVAL,
        CONF_MAX_RETRY_INTERVAL,
    )

    class MockConfigEntry:
        def __init__(self, options: dict) -> None:
            self.options = options
            self.entry_id = "test_entry"

    hass = MagicMock()
    entry = MockConfigEntry({
        CONF_POLL_INTERVAL: 10,
        CONF_MAX_RETRY_INTERVAL: 120,
    })
    device = MagicMock()

    # Initialize coordinator with custom options
    coordinator = AnkerSolixBluetoothUpdateCoordinator(hass, entry, device, "TestDevice")

    # Assert initial values are loaded correctly from config entry options
    assert coordinator.update_interval == timedelta(seconds=10)

    # Simulate user changing options flow to 15 seconds
    entry.options[CONF_POLL_INTERVAL] = 15

    # Trigger the options update handler synchronously (mocking HA event loop)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coordinator.async_update_options_handler())
    loop.close()

    # Assert that the update interval has dynamically updated to 15 seconds
    assert coordinator.update_interval == timedelta(seconds=15)
