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
